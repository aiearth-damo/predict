import numpy as np
import typing as t
import pandas as pd

from aiearth.predict.predictors.predictor import Predictor
from aiearth.predict.checkpoint import ModelCheckpoint


class ImageEchoPredictor(Predictor):
    def init(self, checkpoint: ModelCheckpoint):
        ...

    def _predict_numpy(
        self,
        data: t.Union[np.ndarray, t.Dict[str, np.ndarray]],
        dtype: t.Optional[np.dtype] = None,
    ) -> t.Dict[str, np.ndarray]:
        predict_outputs = self.predict_udf(data["image"])

        return pd.DataFrame({"image": predict_outputs})

    def predict_udf(self, data: np.ndarray):
        return [data]
