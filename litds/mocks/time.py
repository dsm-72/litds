# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/mocks/00_time.ipynb.

# %% auto 0
__all__ = ['MockTimeSeries']

# %% ../../nbs/mocks/00_time.ipynb 3
from dataclasses import dataclass, field, KW_ONLY
from beartype.typing import Optional
from beartype import beartype
from ..abc.mock.base import BaseMock
from ..types import DataFrame

import pandas as pd, numpy as np

# %% ../../nbs/mocks/00_time.ipynb 4
from iza.static import TIME, SERIES, PHATE, BARCODE, CONDITION

# %% ../../nbs/mocks/00_time.ipynb 7
@dataclass
class MockTimeSeries(BaseMock):
    n_series: int = 5
    n_features: int = 3

    series_key: Optional[str] = SERIES
    time_key: Optional[str] = TIME

    max_t: Optional[int] = 10
    max_int: Optional[bool] = 10
    max_rows: Optional[int] = None

    use_int_features: Optional[bool] = True

    def setup(self) -> DataFrame:
        key_cols = [self.series_key, self.time_key]

        data = np.empty((0, len(key_cols) + self.n_features))

        for idx in range(self.n_series):
            # Randomly choose the number of timepoints
            n_chose = np.random.randint(1, self.max_t)
            
            # Randomly pick timepoints as it is not a guarantee that all timepoints are present
            # or that they are consequentive (e.g. 1, 2, 5, 6, 9)
            timepoints = np.random.choice(np.arange(self.max_t), n_chose, replace=False)
            
            # Generate random features
            feature_shape = (n_chose, self.n_features)
            features = np.random.randn(*feature_shape)
            if self.use_int_features:
                features =  np.random.randint(0, self.max_int, feature_shape)

            
            # Stack everything together
            series_data = np.hstack((
                np.repeat([idx], n_chose).reshape(-1, 1),
                timepoints.reshape(-1, 1),
                features
            ))

            # Append to the data
            data = np.vstack((data, series_data))

        # make a dataframe        
        columns = key_cols + self.make_col_names(self.n_features)
        df = pd.DataFrame(data, columns=columns)
        
        # make sure series and time are integers        
        df = df.astype({col: int for col in key_cols}, copy=False)
        if self.use_int_features:
            df = df.astype(int)

        # downsample if needed
        if self.max_rows is not None and self.max_rows < len(df):
            df = df.sample(self.max_rows, replace=False)
            
        # sort by series and time to more easily see that not all time points are present
        df.sort_values(key_cols, inplace=True)
        df.reset_index(inplace=True, drop=True)

        if self.set_index:
            df.set_index(self.series_key, inplace=True)

        return df
