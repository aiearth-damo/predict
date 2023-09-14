# __local_predict_start__
from aiearth.predict.checkpoint import ModelCheckpoint
from aiearth.predict.predictors import TensorrtPredictor
from aiearth.predict.processors import (
    Chw2HwcProcessor,
    MeanNormProcessor,
    Hwc2ChwProcessor,
    SqueezeNdimProcessor,
    MaskBinarizationProcessor,
)
from aiearth.predict.pipelines import GeoSegmentationPredictPipeline

from aiearth.predict.logging import root_logger as logger


ckpt = ModelCheckpoint.from_local_path(
    "/path/to/your/onnx/model",
    image_size=1024,
    bound=128,
)

pipe = GeoSegmentationPredictPipeline(
    model_checkpoint=ckpt,
    predictor_cls=TensorrtPredictor,
    pre_processors=[
        Chw2HwcProcessor(["image"]),
        MeanNormProcessor(
            ["image"], [123.675, 116.28, 103.53], [0.01712475, 0.017507, 0.01742919]
        ),
        Hwc2ChwProcessor(["image"]),
    ],
    post_processors=[
        SqueezeNdimProcessor(["image"]),
        MaskBinarizationProcessor(["image"], 63.75),
    ],
)

pipe("/path/to/your/tiff")
# __local_predict_end__
