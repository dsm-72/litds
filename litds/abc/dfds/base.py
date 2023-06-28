# AUTOGENERATED! DO NOT EDIT! File to edit: ../../../nbs/abc/dfds/02_base.ipynb.

# %% auto 0
__all__ = ['BaseDataFrameDataset']

# %% ../../../nbs/abc/dfds/02_base.ipynb 3
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field

from beartype.typing import (
    Tuple, Union, List, Any, Optional,  Type
)

import numpy as np, pandas as pd

from torch.utils.data import Dataset

# %% ../../../nbs/abc/dfds/02_base.ipynb 4
from ...types import IterLike

from .meta import MetaDataFrameDataset
from .mixs import DataFrameArgsMixin, DataFrameKWArgsMixins
from litds.abc.idxs import (
    DataFrameDatasetLocIndexer,
    DataFrameDatasetILocIndexer, 
    DataFrameDatasetCLocIndexer
)

# %% ../../../nbs/abc/dfds/02_base.ipynb 6
@dataclass
class BaseDataFrameDataset(Dataset, DataFrameArgsMixin, DataFrameKWArgsMixins, metaclass=MetaDataFrameDataset):
          
    def __post_init__(self):
        super().__post_init__()

        self.loc  = DataFrameDatasetLocIndexer(self)
        self.iloc = DataFrameDatasetILocIndexer(self)
        self.cloc = DataFrameDatasetCLocIndexer(self)

    def __len__(self):
        return len(self.df)
    
    def __iter__(self):
        for i in range(len(self)):
            yield self[i]
    
    def check(self, attr: Any, default: Optional[Any]=None) -> Any:
        return getattr(self, attr, default)

    def __len__(self):
        return len(self.df)
    
    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __getitem__(self, idx: Union[int, slice, IterLike]) -> List:
        return self.df.iloc[idx]

    def getall(self):
        unique_idxs = self.cloc.cindex.categories
        return self.__getitem__(np.arange(len(unique_idxs)))