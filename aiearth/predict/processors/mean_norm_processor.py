import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional, Union, Callable, Tuple

from aiearth.predict.processors import Processor


class MeanNormProcessor(Processor):
    def __init__(self, columns: List[str], mean, norm):
        super().__init__()
        self.columns = columns
        self.mean = mean
        self.norm = norm

    def pandas_udf(self, df: pd.DataFrame):
        df[self.columns] = df[self.columns].applymap(
            lambda np_data: (np_data - self.mean) * self.norm
        )
        return df
