import numpy as np
import pandas as pd
from ray.train.predictor import Predictor
from typing import Any, Dict, List, Optional, Union, Callable, Tuple

from aiearth.predict.checkpoint import ModelCheckpoint


class TensorrtPredictor(Predictor):
    def __init__(self, checkpoint: ModelCheckpoint):
        from aiearth.predict.predictors.infer_sdk.tensorrt_infer import TensorRTInfer

        cfg = checkpoint.get_cfg()
        model_path = cfg.path
        use_quant = cfg.params.use_quant
        attached_files = cfg.attached_files if cfg.attached_files else {}
        self.model = TensorRTInfer(
            model_path=model_path, attached_files=attached_files, use_quant=use_quant
        )

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
