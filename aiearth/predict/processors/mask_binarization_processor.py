import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional, Union, Callable, Tuple

from aiearth.predict.processors import Processor


class MaskBinarizationProcessor(Processor):
    def __init__(self, columns: List[str], mask_threshold, fill_value=1):
        super().__init__()
        self.columns = columns
        if mask_threshold > 1.0:
            mask_threshold = mask_threshold / 255.0
        self.mask_threshold = mask_threshold
        self.fill_value = fill_value


class MaskBinarizationProcessor(Processor):
    def __init__(self, columns: List[str], mask_threshold, fill_value=1):
        super().__init__()
        self.columns = columns
        if mask_threshold > 1.0:
            mask_threshold = mask_threshold / 255.0
        self.mask_threshold = mask_threshold
        self.fill_value = fill_value

    def pandas_udf(self, df: pd.DataFrame):
        df[self.columns] = df[self.columns].applymap(
            lambda np_data: np.where(
                np_data > self.mask_threshold, self.fill_value, 0
            ).astype(np.uint8)
        )
        return df
