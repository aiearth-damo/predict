import pandas as pd
from abc import ABCMeta, abstractmethod
from ray.data.preprocessor import Preprocessor
from typing import Any, Dict, List, Optional, Union, Callable, Tuple

from aiearth.predict.schedule import ExecutionBundleOptions, GiB
from aiearth.predict.logging import root_logger as logger


class Processor(Preprocessor, metaclass=ABCMeta):
    _is_fittable = False

    def __init__(self):
        self.execution_bundle_options = ExecutionBundleOptions(
            num_cpus=1, batch_size=1, memory=GiB(1)
        )

    def _transform_pandas(self, df: "pd.DataFrame") -> "pd.DataFrame":
        return self.pandas_udf(df)

    def set_batch_size(self, batch_size):
        self.execution_bundle_options.batch_size = batch_size
        return self

    def set_num_cpus(self, num_cpus):
        self.execution_bundle_options.num_cpus = num_cpus
        return self

    def set_num_gpus(self, num_gpus):
        self.execution_bundle_options.num_gpus = num_gpus
        return self

    def _get_transform_config(self) -> Dict[str, Any]:
        d = self.execution_bundle_options.to_dict()
        return d

    @abstractmethod
    def pandas_udf(self, df: "pd.DataFrame") -> "pd.DataFrame":
        raise NotImplementedError()
