import os
import numpy as np
import pycuda.driver as cuda
import tensorrt as trt
from typing import List, Optional, Dict, Any

from aiearth.predict.predictors.infer_sdk.cuda_utils import get_accelerator_type
from aiearth.predict.predictors.infer_sdk.infer_base import InferBase
from aiearth.predict.checkpoint import ModelAttachedFile
from aiearth.predict.logging import root_logger as logger


def GiB(val):
    return val * 1 << 30


# Simple helper data class that's a little nicer to use than a 2-tuple.
class HostDeviceMem(object):
    def __init__(self, host_mem, device_mem, shape, dtype):
        self.host = host_mem
        self.device = device_mem
        self.shape = shape
        self.dtype = dtype

    def __str__(self):
        return "Shape: " + str(self.shape) + ", Dtype: " + str(self.dtype)

    def __repr__(self):
        return self.__str__()


class Precision:
    FP32 = "FP32"
    FP16 = "FP16"
    INT8 = "INT8"


def get_precision(precision: str):
    if precision.upper() == Precision.FP32:
        return Precision.FP32
    elif precision.upper() == Precision.FP16:
        return Precision.FP16
    elif precision.upper() == Precision.INT8:
        raise RuntimeError(f"precision {precision} not support!")
    else:
        raise RuntimeError(f"precision {precision} not support!")


class TensorRTInfer(InferBase):
    def __init__(
        self,
        model_path,
        attached_files: Optional[Dict[str, ModelAttachedFile]] = {},
        precision="FP16",
        use_static=True,
        use_quant=False,
        verbose=False,
    ):
        # Use autoprimaryctx if available (pycuda >= 2021.1) to
        # prevent issues with other modules that rely on the primary
        # device context.
        try:
            import pycuda.autoprimaryctx
        except ModuleNotFoundError:
            import pycuda.autoinit

        trt_logger = trt.Logger(trt.Logger.INFO)
        if verbose:
            trt_logger.min_severity = trt.Logger.Severity.VERBOSE

        logger.info(f"model_path:{model_path}")
        model_path = os.path.realpath(model_path)
        precision = get_precision(precision)

        dev = get_accelerator_type()

        model_dir = os.path.dirname(model_path)
        model_name_without_ext = os.path.splitext(os.path.basename(model_path))[0]
        # Quantization and trt file naming structure unified
        engine_path = f"{os.path.join(model_dir, model_name_without_ext)}.{dev}.trt"
        quant_engine_path = (
            f"{os.path.join(model_dir, model_name_without_ext)}.{dev}.quant.trt"
        )

        # attached
        attached_engine_key = f"{model_name_without_ext}.{dev}.trt"
        attached_quant_engine_key = f"{model_name_without_ext}.{dev}.trt"

        engine = None
        if use_static:
            if use_quant:
                logger.info("use quantized model")
                if os.path.exists(quant_engine_path):
                    engine = self.deserialize_engine(trt_logger, quant_engine_path)
                    self.engine_path = quant_engine_path
                elif attached_quant_engine_key in attached_files:
                    attached_file: ModelAttachedFile = attached_files[
                        attached_quant_engine_key
                    ]
                    engine = self.deserialize_engine(trt_logger, attached_file.path)
                    self.engine_path = attached_file.path
                else:
                    raise RuntimeError(f"not found trt quant_engine_path!")
            else:
                logger.info("use trt model")
                if os.path.exists(engine_path):
                    engine = self.deserialize_engine(trt_logger, engine_path)
                    self.engine_path = engine_path
                elif attached_engine_key in attached_files:
                    attached_file: ModelAttachedFile = attached_files[
                        attached_engine_key
                    ]
                    engine = self.deserialize_engine(trt_logger, attached_file.path)
                    self.engine_path = attached_file.path
                else:
                    raise RuntimeError(f"not found trt engine_path!")
        else:
            logger.warn("use onnx model")
            engine = self.build_engine_onnx(trt_logger, model_path, precision)

            if use_quant:
                raise RuntimeError("build_engine_onnx not support use_quant")
            self.serialize_engine(engine, engine_path)
            self.engine_path = engine_path

        if not engine:
            raise RuntimeError("trt engine build error!")

        # Inference is the same regardless of which parser is used to build the engine, since the model architecture is the same.
        # Allocate buffers and create a CUDA stream.
        (
            self.inputs,
            self.outputs,
            self.bindings,
            self.stream,
        ) = self.allocate_buffers(engine)
        # Contexts are used to perform inference.
        self.context = engine.create_execution_context()

        logger.info(f"inputs spec: {self.inputs}")
        logger.info(f"outputs spec: {self.outputs}")

    def get_engine_path(self):
        return self.engine_path

    @classmethod
    def from_cfg(cls, cfg: Dict[str, Any]):
        return cls(**cfg)

    def get_inputs_spec(self):
        return self.inputs

    def get_outputs_spec(self):
        return self.outputs

    def infer(self, inputs: List[np.ndarray]):
        if len(inputs) != len(self.inputs):
            raise RuntimeError(
                f"infer inputs num {len(inputs)} is not equal engine inputs num {len(self.inputs)}"
            )
        for idx in range(len(inputs)):
            np.copyto(self.inputs[idx].host, inputs[idx].ravel())
        trt_outputs = self.do_inference_v2(
            self.context,
            bindings=self.bindings,
            inputs=self.inputs,
            outputs=self.outputs,
            stream=self.stream,
        )
        return trt_outputs

    def build_engine_onnx(self, trt_logger, model_path, precision):
        logger.info(f"building engine from file: {model_path}")
        # You can set the logger severity higher to suppress messages (or lower to display more messages).
        builder = trt.Builder(trt_logger)
        network = builder.create_network(
            1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
        )
        parser = trt.OnnxParser(network, trt_logger)

        # Load the Onnx model and parse it in order to populate the TensorRT network.
        success = parser.parse_from_file(model_path)
        for idx in range(parser.num_errors):
            logger.error(parser.get_error(idx))

        if not success:
            raise RuntimeError(f"onnx parser parse from file error! file: {model_path}")

        builder_config = builder.create_builder_config()
        builder_config.max_workspace_size = GiB(10)
        if precision == Precision.FP16:
            if builder.platform_has_fast_fp16:
                builder_config.set_flag(trt.BuilderFlag.FP16)
            else:
                logger.warn("FP16 is not supported natively on this platform/device")
        return builder.build_engine(network, builder_config)

    def serialize_engine(self, built_engine, engine_path):
        logger.info(f"serializing engine to file: {engine_path}")
        with open(engine_path, "wb") as f:
            f.write(built_engine.serialize())

    def deserialize_engine(self, trt_logger, engine_path):
        logger.info(f"deserializing engine from file: {engine_path}")
        with open(engine_path, "rb") as f:
            serialized_engine = f.read()
        runtime = trt.Runtime(trt_logger)
        if not runtime:
            raise RuntimeError("trt runtime create error!")
        return runtime.deserialize_cuda_engine(serialized_engine)

    # Allocates all buffers required for an engine, i.e. host/device inputs/outputs.
    def allocate_buffers(self, engine):
        inputs = []
        outputs = []
        bindings = []
        stream = cuda.Stream()
        for binding in engine:
            shape = engine.get_binding_shape(binding)
            dtype = engine.get_binding_dtype(binding)
            size = trt.volume(shape) * engine.max_batch_size
            dtype = trt.nptype(dtype)
            # Allocate host and device buffers
            host_mem = cuda.pagelocked_empty(size, dtype)
            device_mem = cuda.mem_alloc(host_mem.nbytes)
            # Append the device buffer to device bindings.
            bindings.append(int(device_mem))
            # Append to the appropriate list.
            if engine.binding_is_input(binding):
                inputs.append(HostDeviceMem(host_mem, device_mem, shape, dtype))
            else:
                outputs.append(HostDeviceMem(host_mem, device_mem, shape, dtype))
        return inputs, outputs, bindings, stream

    # This function is generalized for multiple inputs/outputs.
    # inputs and outputs are expected to be lists of HostDeviceMem objects.
    def do_inference(self, context, bindings, inputs, outputs, stream, batch_size=1):
        # Transfer input data to the GPU.
        [cuda.memcpy_htod_async(inp.device, inp.host, stream) for inp in inputs]
        # Run inference.
        context.execute_async(
            batch_size=batch_size, bindings=bindings, stream_handle=stream.handle
        )
        # Transfer predictions back from the GPU.
        [cuda.memcpy_dtoh_async(out.host, out.device, stream) for out in outputs]
        # Synchronize the stream
        stream.synchronize()
        # Return only the host outputs.
        return [out.host.copy().reshape(out.shape) for out in outputs]

    # This function is generalized for multiple inputs/outputs for full dimension networks.
    # inputs and outputs are expected to be lists of HostDeviceMem objects.
    def do_inference_v2(self, context, bindings, inputs, outputs, stream):
        # Transfer input data to the GPU.
        [cuda.memcpy_htod_async(inp.device, inp.host, stream) for inp in inputs]
        # Run inference.
        context.execute_async_v2(bindings=bindings, stream_handle=stream.handle)
        # Transfer predictions back from the GPU.
        [cuda.memcpy_dtoh_async(out.host, out.device, stream) for out in outputs]
        # Synchronize the stream
        stream.synchronize()
        # Return only the host outputs.
        return [out.host.copy().reshape(out.shape) for out in outputs]
