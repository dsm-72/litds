# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/named/03_named_arrays.ipynb.

# %% auto 0
__all__ = ['NamedAxis', 'NamedAxes', 'NamedArrayDimsError', 'NamedArrayDynamicAttrsMixin', 'NamedArray']

# %% ../../nbs/named/03_named_arrays.ipynb 4
import os, copy, itertools
import numpy as np, pandas as pd

from dataclasses import dataclass, field
from rich.repr import auto as rich_auto, Result as RichReprResult

from typing import overload, Union, List, Tuple, Optional, Dict

# %% ../../nbs/named/03_named_arrays.ipynb 5
@dataclass
class NamedAxis:
    name: str
    axis: Optional[int] = None

    def __str__(self):
        return f'{self.name}({self.axis})'

    def __repr__(self):
        return f'NamedAxis(name="{self.name}", axis={self.axis})'

    def copy(self) -> 'NamedAxis':
        return copy.deepcopy(self)
    
    def __iter__(self):
        return iter([self.name, self.axis])
    
    @property
    def snake_case(self):
        return self.name.lower().replace(' ', '_')

# %% ../../nbs/named/03_named_arrays.ipynb 6
@dataclass
class NamedAxes:
    axes: Union[List[NamedAxis], Tuple[NamedAxis]]
    name: Optional[str] = 'NamedAxes'
    umap: Dict[str, NamedAxis] = field(default_factory=dict, init=False, repr=False)
    
    def __post_init__(self):
        for i, axis in enumerate(self.axes):
            axis.axis = i
        self.umap = {ax.axis: ax for ax in self.axes}
        
    @property
    def ndim(self) -> int:
        return len(self.axes)
    
    @property
    def anames(self) -> List[str]:
        return [str(ax.name) for ax in self.axes]
       
    @property
    def aidxs(self) -> List[int]:        
        return [int(ax.axis) for ax in self.axes]

    @property
    def alocs(self) -> List[int]:
        return list(range(len(self)))
 
    def __getitem__(self, key:Union[int, str, NamedAxis]) -> NamedAxis:
        if isinstance(key, int):
            return self.axes[key]
        
        elif isinstance(key, NamedAxis):
            # NOTE: this gets location based off original location
            return self.umap[key.axis]
        
        elif isinstance(key, str):
            return next((ax for ax in self.umap.values() if key in [ax.name, ax.axis]), None)
        
        else:
            raise KeyError(f'Key {key} not found in {self.name}')
        
    def __str__(self):        
        return f'{self.name}(' + ', '.join(self.anames) + ')'
    
    def __repr__(self):
        return f'NamedAxes(axes={self.axes}, name="{self.name}")'

    def __rich_repr__(self) -> RichReprResult:        
        yield self.__str__()
    
    def __iter__(self):
        return iter(self.axes)

    def __len__(self):
        return len(self.axes)
    
    def copy(self):
        axes = copy.deepcopy(self)
        axes.umap = copy.deepcopy(self.umap)
        return axes
    
    def index(self, key:Union[int, str, NamedAxis]):
        ax = self[key]
        return self.axes.index(ax)

    def transpose(self, *order:Union[str, int, NamedAxis]):
        axes = self.copy()
        # check input and convert to axes
        update_axes = [axes[key] for key in order]
        # gather the axes that are not in the provided order
        needed_axes = [ax for ax in axes.axes if ax not in update_axes]
        # the new order of axes is the updated axes followed by the needed axes
        new_order = update_axes + needed_axes        
        # rearrange axes according to the new order
        axes.axes = new_order
        for ax in axes.axes:
            ax.axis = new_order.index(ax)
        return axes

# %% ../../nbs/named/03_named_arrays.ipynb 7
class NamedArrayDimsError(ValueError):
     def __init__(self, dims=None, ndim=None):
          message = f'NamedArray must have {len(dims)} dimensions, but got {ndim}.'
          if dims is None or ndim is None:
               message = f'NamedArray dims do not match shape of underlying numpy ndarray.'

          self.dims = dims
          self.ndim = ndim    
          self.message = message
          super().__init__(message)

# %% ../../nbs/named/03_named_arrays.ipynb 8
class NamedArrayDynamicAttrsMixin:
    def _idx_str(self, axis:NamedAxis):
        return f'{axis.snake_case}_idx'
    
    def _get_idx(self, axis:NamedAxis):
        return getattr(self, self._idx_str(axis))
    
    def _axis_idx_eq(self, axis:NamedAxis, i:int) -> bool:
        return self._get_idx(axis) == i
    
    def __make_idx_attrs__(self):        
        for axis in self.dims: 
            property_func = property(lambda self, axis=axis: self.dims.index(axis))
            setattr(self.__class__, self._idx_str(axis), property_func)
        return self
    
    
    def _make_is_perm_order_check_func(self, perm):
        def check_func(self):
            return all(self._axis_idx_eq(axis, i) for i, axis in enumerate(perm))
        return check_func

    def __make_is_attrs__(self):   
        for perm in itertools.permutations(self.dims):
            method = f'is_{"_".join([axis.snake_case for axis in perm])}'
            func = self._make_is_perm_order_check_func(perm)
            setattr(self.__class__, method, property(func))
        return self
    

# %% ../../nbs/named/03_named_arrays.ipynb 9
class NamedArray(np.ndarray):
    '''
    See: https://numpy.org/doc/stable/user/basics.subclassing.html
    '''
    DIMS : Union[NamedAxes, None] = None
    def default_dims(self) -> NamedAxes:        
        return self.DIMS.copy() if self.DIMS else self.make_dims(self.ndim)
        
    def make_dims(self, ndim:int) -> NamedAxes:        
        dims = NamedAxes([NamedAxis(f'a{i}') for i in range(ndim)])
        return dims

    def __new__(cls, arr, dims:NamedAxes=None):
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        obj = np.asarray(arr).view(cls)
        # add the new attribute to the created instance
        obj.dims = (dims or cls.default_dims(obj)).copy()
        # check for dynamic mixins

        # TODO: there is a bug where the dynamic attrs are added
        # but .T will not update the properties
        if issubclass(cls, NamedArrayDynamicAttrsMixin):
            obj.__make_idx_attrs__()
            obj.__make_is_attrs__()

        # Finally, we must return the newly created object:        
        return obj
                
    def __array_finalize__(self, obj):     
        # We do not need to return anything
        if obj is None: return

        dims = getattr(obj, 'dims', self.default_dims())
        self.dims = dims
        # Ensure correct shape
        if self.ndim != len(self.dims):            
            raise NamedArrayDimsError(self.dims, self.shape)
        
        # TODO: there is a bug where the dynamic attrs are added
        # but .T affects the original object
        if issubclass(self.__class__, NamedArrayDynamicAttrsMixin):
            self.__make_idx_attrs__()
            self.__make_is_attrs__()
                    
    @property
    def dim_names(self) -> Union[Tuple[str], None]:
        return tuple(self.dims.anames) if self.dims else None
    
    @property
    def dim_str(self) -> str:
        _str = ', '.join([f'{s} {n}' for s, n in zip(self.shape, self.dim_names)])
        return f'({_str})'
    
    @overload
    def transpose(self, *axes: Union[int, str, NamedAxis]) -> 'NamedArray': ...
    @overload
    def transpose(self, axes: Tuple[Union[int, str, NamedAxis], ...]) -> 'NamedArray': ...
    def transpose(self, *axes:Union[str, int, NamedAxis]):
        dims = self.dims.copy()
        if len(axes) == 0:
            # If no arguments are provided, reverse the order of axes
            axes = dims.anames[::-1]
            
        # If the first argument is a tuple, use it as the axes
        elif len(axes) == 1 and isinstance(axes[0], tuple):
            axes = axes[0]
            
        # Get the order of axes indices        
        new_idxs = [dims.index(ax) for ax in axes]
        # Transpose the NamedAxes
        dims = dims.transpose(*axes)
        # Transpose the underlying numpy array
        transposed_array = np.transpose(np.asarray(self), axes=new_idxs)
        # Create new NamedArray with the transposed ndarray and the updated NamedAxes
        return self.__class__(transposed_array, dims)
    
    def __repr__(self):
        # base = super(NamedArray, self).__repr__()
        base = np.ndarray.__repr__(self)
        
        first_line = base.split('\n')[0]
        spaces = 0
        for s in first_line:            
            if s.isdigit():
                break
            spaces += 1
        spaces = ' ' * (spaces - 1)
        return f'{base}\n{spaces}{self.dim_str}'
    
    @property
    def T(self):
        return self.transpose(*self.dims.anames[::-1])