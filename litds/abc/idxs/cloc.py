# AUTOGENERATED! DO NOT EDIT! File to edit: ../../../nbs/abc/idxs/05_cloc.ipynb.

# %% auto 0
__all__ = ['logger', 'DataFrameDatasetCLocIndexer']

# %% ../../../nbs/abc/idxs/05_cloc.ipynb 3
from dataclasses import dataclass, field
from beartype.typing import (Union, List, Iterable, Optional)
from nptyping import NDArray, Shape, Bool
 
import numpy as np

from iza.nbs import NotebookLogger
from iza.utils import (isiter, allinstance, allsametype, arein, isin, Slice)

# %% ../../../nbs/abc/idxs/05_cloc.ipynb 4
from .base import BaseDataFrameDatasetIndexer
from ...types import BoolLike, IndexLike

# %% ../../../nbs/abc/idxs/05_cloc.ipynb 5
logger = NotebookLogger()

# %% ../../../nbs/abc/idxs/05_cloc.ipynb 7
@dataclass
class DataFrameDatasetCLocIndexer(BaseDataFrameDatasetIndexer):
    '''
    NOTE: what is the difference between loc and cloc? Afterall loc can handle both
    integer and string indexing, either with repeated values. So why do we need cloc?
    Well we might not know what the categorical value is (if it is a string label). So
    we extract the catgories from the index and then assume that the index is working
    on the __categories__ rather than the index. We then use the categories (labels) to work
    with df.loc.
    '''
    def is_bools_idx(self, idx: Iterable[bool]) -> bool:
        return isiter(idx) and len(idx) == len(self.index) and allinstance(idx, BoolLike)

    def bools2iloc(self, bools) -> np.ndarray:
        if self.is_bools_idx(bools):
            return np.where(bools)[0]
        return np.empty(0)

    def cat2iloc(self, idx: Union[int, str]) -> IndexLike:
        bools = self.cindex.get_loc(idx)
        iloc = self.boolsiloc(bools)
        return iloc
    
    def cat2bool(self, cat):
        return self.cindex.get_loc(cat)
    
    def safe_cat2bool(self, cat):
        return self.cindex == cat
    
    def join_bools_or(self, idx: Iterable[bool]) -> NDArray[Shape['*'], Bool]:
        if not isiter(idx):
            return np.zeros_like(self.index, dtype=bool)
        
        if allinstance(idx, bool):
            idx = [idx]
        
        return np.logical_or.reduce(idx)
    
    def cats2bool(self, idx: Iterable):
        bools = [self.safe_cat2bool(i) for i in idx]
        bools = self.join_bools_or(bools)
        return bools

    def cats2iloc(self, idx: Iterable[Union[int, str, bool]]) -> IndexLike:
        if allinstance(idx, BoolLike):
            bools = idx
            iloc = self.bools2iloc(bools)
            return iloc
        bools = self.cats2bool(idx)
        iloc = self.bools2iloc(bools)
        return iloc
    
    def icat(self, idx:Union[int, slice, List[int]], unique: Optional[bool]=True) -> IndexLike:
        '''Category at index `idx` of all categories'''
        if isinstance(idx, slice):
            slc = Slice(idx)
            idx = slc.astype(list)
            # recall that slice(0, 3, 1) --> [0, 1, 2] so indexing will be the same

        # try to take from categories
        if (isiter(idx) and max(idx) < len(self.categories)):
            cats = self.categories[idx]

        elif isinstance(idx, int) and idx < len(self.categories):            
            cats = self.categories[idx]        
        # to big take categories from rows
        else:
            cats = self.cindex[idx]

        if unique and isiter(cats):
            cats = sorted(np.unique(cats))
        return cats

        

    def geticat(self, idx:Union[int, slice], unique: Optional[bool]=True) -> IndexLike:  
        # unique row indicies corresponding to a category
        cats = self.icat(idx)
        if unique:
            cats = np.unique(cats)        
        return cats

    def __getitem__(self, idx: Union[int, slice]) -> List:  
        # single categorical int or str (label) 
        if isinstance(idx, (int, str)) and isin(idx, self.categories):
            iloc = self.cindex.get_indexer_for([idx])

        # boolean array same length as index
        elif self.is_bools_idx(idx):
            iloc = self.boolsiloc(idx)

        # array of single type
        elif isiter(idx) and allsametype(idx) and arein(idx, self.categories):       
            iloc = self.cindex.get_indexer_for(idx)

        # we have a slice, so now we try to make it an index array
        # note that slice('a') --> slice(None, 'a', None)
        elif isinstance(idx, slice):
            cats = self.icat(idx)            
            return self.__getitem__(cats)

        # single int and it is not a category. So replace it with the category
        # at that index
        elif isinstance(idx, int):            
            cats = self.icat(idx)
            return self.__getitem__(cats)

        # index array and it is not a category. So replace each with a category
        elif allinstance(idx, int):
            cats = self.geticat(idx, unique=True)
            return self.__getitem__(cats)
            # iloc = self.cats2iloc(cats)            

        # use safe_cat2bool to check (cindex == c) for all cats
        elif isiter(idx):            
            iloc = self.cats2iloc(idx)

        else:
            logger.debug(f"idx: {idx}")

        return self.dataset.__getitem__(iloc)
    
    @property
    def cindex(self):
        try:
            return self._cindex
        except AttributeError:
            self._cindex = self.index.astype('category')
            return self._cindex 
        
    @property
    def categories(self):
        try:
            return self._categories
        except AttributeError:
            self._categories = self.cindex.categories
            return self._categories
