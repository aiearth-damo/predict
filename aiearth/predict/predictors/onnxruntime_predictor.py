import numpy as np
import pandas as pd
from ray.train.predictor import Predictor
from typing import Any, Dict, List, Optional, Union, Callable, Tuple

from aiearth.predict.checkpoint import ModelCheckpoint


class ONNXRuntimePredictor(Predictor):
    def __init__(self, checkpoint: ModelCheckpoint):
        from aiearth.predict.predictors.infer_sdk.onnxruntime_infer import (
            OnnxRuntimeInfer,
        )

        file_path = checkpoint.get_cfg().path
        self.model = OnnxRuntimeInfer(model_path=file_path)

    @classmethod
    def from_checkpoint(cls, checkpoint: ModelCheckpoint):
        return cls(checkpoint)

    def _predict_numpy(
        self,
        data: Union[np.ndarray, Dict[str, np.ndarray]],
        dtype: Optional[np.dtype] = None,
    ) -> Dict[str, np.ndarray]:
        predict_outputs = self.predict_udf(data["image"])

        return pd.DataFrame({"image": predict_outputs})

    def predict_udf(self, data: np.ndarray):
        outputs = []
        batch_size = data.shape[0]
        for i in range(batch_size):
            out = self.model.infer([data[i : i + 1]])
            outputs.append(out[0])
        return outputs
