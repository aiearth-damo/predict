import os
import numpy as np
from typing import Any, List
import onnxruntime as ort

from aiearth.predict.predictors.infer_sdk.infer_base import InferBase
from aiearth.predict.logging import root_logger as logger


class OnnxRuntimeInfer(InferBase):
    def __init__(self, model_path, device_id=0, ort_custom_op_path=""):
        self.model_path = os.path.realpath(model_path)

        logger.info(f"model_path:{model_path}")

        session_options = ort.SessionOptions()
        # register custom op for onnxruntime
        if os.path.exists(ort_custom_op_path):
            session_options.register_custom_ops_library(ort_custom_op_path)

        providers = ["CPUExecutionProvider"]
        provider_options = [{}]
        is_cuda_available = ort.get_device() == "GPU"
        if is_cuda_available:
            providers.insert(0, "CUDAExecutionProvider")
            provider_options.insert(0, {"device_id": device_id})
        else:
            logger.warn("cuda device is not available, using cpu instead.")
        sess = ort.InferenceSession(
            self.model_path,
            sess_options=session_options,
            providers=providers,
            provider_options=provider_options,
        )

        self.ort_sess = sess
        self.inputs = sess.get_inputs()
        self.outputs = sess.get_outputs()

        logger.info(f"inputs spec: {[str(inp) for inp in self.inputs]}")
        logger.info(f"outputs spec: {[str(out) for out in self.outputs]}")

    def infer(self, inputs: List[np.ndarray]):
        if len(inputs) != len(self.inputs):
            raise RuntimeError(
                f"infer inputs num {len(inputs)} is not equal engine inputs num {len(self.inputs)}"
            )

        ort_inputs = {
            ort_inp.name: self.ort_input_cast(ort_inp, inp)
            for ort_inp, inp in zip(self.inputs, inputs)
        }
        ort_outputs = self.ort_sess.run(None, ort_inputs)

        return ort_outputs

    def ort_input_cast(self, ort_inp, inp):
        ort_dtype = ort_inp.type
        if "float" in ort_dtype:
            cast_dtype = np.float32
        else:
            raise RuntimeError(f"ort input:{ort_inp} tensor type not support!")

        if inp.dtype != cast_dtype or list(inp.shape) != ort_inp.shape:
            return inp.reshape(*ort_inp.shape).astype(cast_dtype)
        else:
            return inp

    def get_inputs_spec(self):
        return self.inputs

    def get_outputs_spec(self):
        return self.outputs
