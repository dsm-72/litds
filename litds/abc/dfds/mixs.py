# AUTOGENERATED! DO NOT EDIT! File to edit: ../../../nbs/abc/dfds/01_mixs.ipynb.

# %% auto 0
__all__ = ['DataFrameArgsMixin', 'DataFrameKWArgsMixins']

# %% ../../../nbs/abc/dfds/01_mixs.ipynb 3
from dataclasses import dataclass, field

# %% ../../../nbs/abc/dfds/01_mixs.ipynb 4
from ...types import BoolLike, DataFrame

# %% ../../../nbs/abc/dfds/01_mixs.ipynb 6
@dataclass
class DataFrameArgsMixin:
    df: DataFrame = field(default_factory=DataFrame, repr=False)
    
    def __post_init__(self):
        self.index = self.df.index

# %% ../../../nbs/abc/dfds/01_mixs.ipynb 7
@dataclass
class DataFrameKWArgsMixins:
    '''Helper methods for getting the arguments used to construct the class'''
    @classmethod
    def __classfields__(cls):
        return list(cls.__dataclass_fields__.keys())
    
    def __kwargs__(self):
        return {k: getattr(self, k) for k in self.__classfields__()}