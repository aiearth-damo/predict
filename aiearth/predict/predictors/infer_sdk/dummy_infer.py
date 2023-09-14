import os
import ray
import numpy as np
from typing import Dict, List

from aiearth.predict.predictors.infer_sdk.infer_base import InferBase
from aiearth.predict.logging import root_logger as logger


class DummyInfer(InferBase):
    def __init__(self, output_shapes=None, **kwargs):
        if output_shapes:
            self.output_shapes = output_shapes
        else:
            self.output_shapes = [[1, 11, 1024, 1024]]

    @classmethod
    def from_cfg(cls, cfg):
        return cls(**cfg)

    def infer(self, inputs: List[np.ndarray]):
        logger.info("ray.get_gpu_ids(): {}".format(ray.get_gpu_ids()))
        logger.info(
            "CUDA_VISIBLE_DEVICES: {}".format(os.environ["CUDA_VISIBLE_DEVICES"])
        )
        return [np.random.randn(*out) for out in self.output_shapes]
