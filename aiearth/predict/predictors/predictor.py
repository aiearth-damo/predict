import typing as t
import numpy as np
import pandas as pd
from abc import ABCMeta, abstractmethod
from ray.train.predictor import Predictor as RayPredictor

from aiearth.predict.checkpoint import ModelCheckpoint


class Predictor(RayPredictor, metaclass=ABCMeta):
    def __init__(self, checkpoint: ModelCheckpoint):
        super().__init__()
        self.init(checkpoint)

    @abstractmethod
    def init(self, checkpoint: ModelCheckpoint):
        raise NotImplementedError()

    @classmethod
    def from_checkpoint(cls, checkpoint: ModelCheckpoint):
        return cls(checkpoint)

    def _predict_numpy(
        self,
        data: t.Union[np.ndarray, t.Dict[str, np.ndarray]],
        dtype: t.Optional[np.dtype] = None,
    ) -> t.Dict[str, np.ndarray]:
        predict_outputs = self.predict_udf(data)
        return pd.DataFrame({"predict": predict_outputs})

    @abstractmethod
    def predict_udf(self, data: t.Union[np.ndarray, t.Dict[str, np.ndarray]]):
        raise NotImplementedError()
