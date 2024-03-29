# AUTOGENERATED! DO NOT EDIT! File to edit: ../../../nbs/abc/idxs/01_base.ipynb.

# %% auto 0
__all__ = ['BaseDataFrameDatasetIndexer']

# %% ../../../nbs/abc/idxs/01_base.ipynb 3
from dataclasses import dataclass, field
from beartype.typing import (Union, List, Any)

# %% ../../../nbs/abc/idxs/01_base.ipynb 4
from ...types import BoolLike, IndexLike
from .meta import MetaDataFrameDatasetIndexer

# %% ../../../nbs/abc/idxs/01_base.ipynb 6
@dataclass
class BaseDataFrameDatasetIndexer(metaclass=MetaDataFrameDatasetIndexer):
    dataset: Any
    
    def __init__(self, dataset) -> None:
        self.dataset = dataset

    def __post_init__(self):
        self.index = self.setup()

    def setup(self) -> IndexLike:
        return self.dataset.index

    def __getitem__(self, idx: Union[int, slice]) -> List:
        return self.dataset.__getitem__(idx)
    
    def __len__(self) -> int:
        return len(self.index)
    
    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __setitem__(self, idx: Union[int, slice], value: Any) -> None:
        raise NotImplementedError("Setting values is not supported.")

    def __delitem__(self, idx: Union[int, slice]) -> None:
        raise NotImplementedError("Deleting values is not supported.")
