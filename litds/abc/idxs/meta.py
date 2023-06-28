# AUTOGENERATED! DO NOT EDIT! File to edit: ../../../nbs/abc/idxs/00_meta.ipynb.

# %% auto 0
__all__ = ['MetaDataFrameDatasetIndexer']

# %% ../../../nbs/abc/idxs/00_meta.ipynb 3
from abc import ABCMeta, abstractmethod
from beartype.typing import (Tuple, Union, List, Any)

# %% ../../../nbs/abc/idxs/00_meta.ipynb 4
from ...types import IndexLike

# %% ../../../nbs/abc/idxs/00_meta.ipynb 6
class MetaDataFrameDatasetIndexer(ABCMeta): 
    __args__: Tuple[Any,]

    def __instancecheck__(cls, instance):
        return hasattr(instance, 'dataset')
     
    @abstractmethod
    def __getitem__(self, idx: Union[int, slice]) -> List:
        pass

    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def setup(self) -> IndexLike:
        '''Should make the index for the dataset.'''
        pass