# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/fetch/08_pbmc.ipynb.

# %% auto 0
__all__ = ['LEVEL_SENSITIVITY', 'FluentBioPBMC2023']

# %% ../../nbs/fetch/08_pbmc.ipynb 4
import os, sys, json, math, pickle, warnings, itertools
import requests, tarfile, gzip, shutil

import numpy as np, pandas as pd
import torch, torch.nn as nn, pytorch_lightning as pl
import scprep, anndata as ad

# import scanpy as sc

import phate

import matplotlib as mpl, matplotlib.pyplot as plt, seaborn as sns

# %% ../../nbs/fetch/08_pbmc.ipynb 5
from dataclasses import dataclass, field, KW_ONLY

from beartype.typing import Optional, Tuple, Union, TypeAlias, Dict, Any, List, ClassVar
from nptyping import NDArray, Float, Shape, Number as AnyNumber
from beartype import beartype

#| export
from littyping.core import Device

# %% ../../nbs/fetch/08_pbmc.ipynb 6
from tqdm.auto import tqdm
from kuut.core import (kuut, kstep)

# %% ../../nbs/fetch/08_pbmc.ipynb 7
from iza.types import AnnData

from iza.utils import (
    drop_ext, stream_file, make_missing_dirs,
    Directory, FilterMatrixDirectory, 
    decompress_tarball_of_gunzipped_files
)

from iza.static import (
    EXT_TAR_GZ,  ADATA, MATRIX, FEATURES, BARCODES, SENSITIVITY
)
LEVEL_SENSITIVITY = 1

# %% ../../nbs/fetch/08_pbmc.ipynb 8
from ..utils import (random_split_dataframe)

# %% ../../nbs/fetch/08_pbmc.ipynb 10
AMAZON_BUCKET = 'https://fbs-public.s3.us-east-2.amazonaws.com'
REPORT_LINK = f'{AMAZON_BUCKET}/public-datasets/pbmc/combined.html'
FILTERED_MATRIX_LINK = f'{AMAZON_BUCKET}/public-datasets/pbmc/filtered_matrix.tar.gz'

SENSITIVITY_LEVELS = 5

SENSITIVITY_DIRS = [f'sensitivity_{i}' for i in range(1, SENSITIVITY_LEVELS + 1)]

FILTERED_MATRIX_FILES = (
    FilterMatrixDirectory.BARCODES_FILE,
    FilterMatrixDirectory.FEATURES_FILE,
    FilterMatrixDirectory.MATRIX_FILE
)

# %% ../../nbs/fetch/08_pbmc.ipynb 13
@dataclass
class FluentBioPBMC2023:
    data_dir: str = os.path.expanduser('~/Downloads/fluentbio_pbmc')
 
    _: KW_ONLY
    perc_train: float = 0.7
    perc_valid: float = 0.1
    perc_test: float = 0.2

    AMAZON_BUCKET: ClassVar[str] = AMAZON_BUCKET
    REPORT_LINK: ClassVar[str] = REPORT_LINK
    FILTERED_MATRIX_LINK: ClassVar[str] = FILTERED_MATRIX_LINK
    SENSITIVITY_LEVELS: ClassVar[str] = SENSITIVITY_LEVELS
    SENSITIVITY_DIRS: ClassVar[List[str]] = SENSITIVITY_DIRS
    FILTERED_MATRIX_FILES: ClassVar[Tuple[str]] = FILTERED_MATRIX_FILES

    def __post_init__(self):
        make_missing_dirs(self.data_dir)

    @property
    def report(self):
        # NOTE: filter_matrix.tar.gz
        uri = self.REPORT_LINK
        filename = os.path.basename(uri)
        fullpath = os.path.join(self.data_dir, filename)
        return fullpath
    
    @property
    def archive_file(self):
        # NOTE: filter_matrix.tar.gz
        uri = self.FILTERED_MATRIX_LINK
        filename = os.path.basename(uri)
        fullpath = os.path.join(self.data_dir, filename)
        return fullpath
    
    @property
    def archive(self):
        # NOTE: filter_matrix        
        dirname = drop_ext(self.archive_file, EXT_TAR_GZ)
        return dirname

    @property
    def known_sensitivities(self):
        return [i for i in range(1, self.SENSITIVITY_LEVELS + 1)]

    @property
    def sensitivity_dirs(self):
        return [os.path.join(self.archive, dirname) for dirname in self.SENSITIVITY_DIRS]
    
    def int_to_sensitivity(self, i:int) -> str:
        return f'sensitivity_{i}'

    def wrangle_sensitivity(self, sensitivity:Union[str, int]) -> str:
        if isinstance(sensitivity, int):
            return self.int_to_sensitivity(sensitivity)            
        return sensitivity

    def get_sensitivity_dir(self, sensitivity:Union[str, int]) -> str:
        sensitivity = self.wrangle_sensitivity(sensitivity)
        return os.path.join(self.archive, sensitivity)

    def get_adata_filename(self, sensitivity:Union[str, int]) -> str:
        sens_dir = self.get_sensitivity_dir(sensitivity)
        sens_dir = FilterMatrixDirectory(sens_dir)
        return sens_dir.adata_filename

    def get_adata(self, sensitivity:Union[str, int]) -> AnnData:
        sens_dir = self.get_sensitivity_dir(sensitivity)
        sens_dir = FilterMatrixDirectory(sens_dir)
        return sens_dir.get_adata()

    @property
    def archive_files(self):
        return list(map(
            lambda e : os.path.join(*e),
            itertools.product(
                self.sensitivity_dirs,
                self.FILTERED_MATRIX_FILES
            ))
        )

    def print_archive_contents(self):
        print(Directory(self.archive))

    @property
    def is_archive_downloaded(self):
        return os.path.isfile(self.archive_file) or os.path.isdir(self.archive)

    @property
    def is_archive_decompressed(self):
        return all([os.path.isfile(file) for file in self.archive_files])        
    
    @property
    def is_report_downloaded(self):
        return os.path.isfile(self.report)
    

    def download(self):
        uri = self.FILTERED_MATRIX_LINK        
        description = 'Downloading FluentBio PBMC filtered matrix'  
        if not self.is_archive_downloaded:
            stream_file(uri, self.archive_file, description)

        uri = self.REPORT_LINK
        description = 'Downloading FluentBio PBMC report'
        if not self.is_report_downloaded:
            stream_file(uri, self.report, description)

    def decompress(self):
        description = 'Decompressing FluentBio PBMC filtered matrix'  
        if not self.is_archive_decompressed:
            decompress_tarball_of_gunzipped_files(self.archive_file, description, remove=True)

    def make_adata_files(self):
        desc = 'PIPSeeker Sensitivities'
        for sensitivity_dir in tqdm(self.sensitivity_dirs, desc=desc):
            try:
                fm_dir = FilterMatrixDirectory(sensitivity_dir)
            except Exception:
                pass

    def prepare(self):
        steps = [
            'Downloading', 'Decompressing',
            'Creating adata files'
        ]
        
        steps = tqdm(steps, desc='FluentBio')        
        for step in steps:
            steps.set_postfix(stage=step)
            match step:
                case 'Downloading':
                    self.download()
                case 'Decompressing':
                    self.decompress()
                case 'Creating adata files':
                    self.make_adata_files()
                case _:
                    pass
    
