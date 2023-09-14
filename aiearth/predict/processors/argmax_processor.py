import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional, Union, Callable, Tuple

from aiearth.predict.processors import Processor


class ArgmaxProcessor(Processor):
    def __init__(self, columns: List[str]):
        super().__init__()
        self.columns = columns

    def pandas_udf(self, df: pd.DataFrame):
        df[self.columns] = df[self.columns].applymap(
            lambda np_data: np.argmax(np_data, axis=0)
        )
        return df
