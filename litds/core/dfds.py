# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/core/00_dfds.ipynb.

# %% auto 0
__all__ = ['DataFrameDatasetMixin', 'DataFrameDataset']

# %% ../../nbs/core/00_dfds.ipynb 3
import numpy as np
import torch

from dataclasses import dataclass, field, KW_ONLY
from beartype.typing import Optional, Iterable

from iza.static import (LABEL, )
from iza.utils import (Slice, wrangle_kwargs_for_func, )

from littyping.core import Device

# %% ../../nbs/core/00_dfds.ipynb 4
from ..mocks.time import MockTimeSeries
from ..abc.dfds.base import BaseDataFrameDataset

# %% ../../nbs/core/00_dfds.ipynb 8
@dataclass
class DataFrameDatasetMixin(BaseDataFrameDataset): 
    label_key: str = LABEL

    _: KW_ONLY = field(default=None, init=False)    
    device: Optional[Device] = None

    def __init__(self, *args, **kwargs) -> None:
        params = wrangle_kwargs_for_func(super().__init__, dict(label_key=self.label_key), **kwargs)        
        super().__init__(**params)
    
    def __post_init__(self):
        super().__post_init__()
        label_cats = self.df[self.label_key].astype('category')

        unique_labels = sorted(label_cats.cat.codes.unique())
        
        self.y_uni = unique_labels

        self.y_idxs = {
            label: (label_cats.cat.codes == label)
            for label in unique_labels
        }

    def __len__(self):
        # NOTE: we divide by the number of timepoints we have
        # even though it is not gaurenteed that we have an uniform number
        # of samples per time point

        # NOTE: this will impact the DataLoader later on
        # as the batch size will be the min(batch_size, len(self))

        # we group by label and then take mean count for each label
        groups = self.df.reset_index().groupby(self.label_key)
        return int(groups.count().mean().mean().round())

    def getone(self):
        df_tmp = self.df.drop(columns=self.label_key, errors='ignore')

        sample = np.vstack(tuple([
            df_tmp[y_idx].sample(1) for y_idx in self.y_idxs.values()
        ]))
        labels = self.y_uni

        sample = torch.Tensor(sample)
        labels = torch.Tensor(labels)

        if self.device is not None:
            sample = sample.to(self.device)
            labels = labels.to(self.device)

        return sample, labels
    
    def getmany(self, idx: int):        
        data = [self.getone() for _ in idx]
        samples, targets = zip(*data)
        
        samples = torch.stack(samples)
        targets = torch.stack(targets)
        return samples, targets

    
    def sample(self, label: int, n: int = 1, replace: bool = False):
        idx = self.y_idxs[label]
        return self.df[idx].sample(n=n, replace=replace)

    def __getitem__(self, idx):

        if isinstance(idx, slice):
            src = Slice(idx)
            arr = src.astype(list)
            idx = arr

        if isinstance(idx, Iterable):
            return self.getmany(idx)
        
        sample, labels = self.getone()
        return sample, labels

# %% ../../nbs/core/00_dfds.ipynb 10
class DataFrameDataset(DataFrameDatasetMixin, BaseDataFrameDataset):
    pass
