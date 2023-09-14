import cv2
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional, Union, Callable, Tuple

from aiearth.predict.processors import Processor


class RGB2GrayProcessor(Processor):
    def __init__(self, columns: List[str]):
        super().__init__()
        self.columns = columns

    def pandas_udf(self, df: pd.DataFrame):
        df[self.columns] = df[self.columns].applymap(
            lambda np_data: cv2.cvtColor(np_data, cv2.COLOR_BGR2GRAY)
        )
        return df
