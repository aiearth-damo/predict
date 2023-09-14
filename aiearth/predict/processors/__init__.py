from aiearth.predict.processors.processor import Processor

from aiearth.predict.processors.argmax_processor import ArgmaxProcessor
from aiearth.predict.processors.chw2hwc_processor import Chw2HwcProcessor
from aiearth.predict.processors.hwc2chw_processor import Hwc2ChwProcessor
from aiearth.predict.processors.mask_binarization_processor import (
    MaskBinarizationProcessor,
)
from aiearth.predict.processors.mean_norm_processor import MeanNormProcessor
from aiearth.predict.processors.squeeze_ndim_processor import SqueezeNdimProcessor
from aiearth.predict.processors.rgb2gray_processor import RGB2GrayProcessor

__all__ = [
    "Processor",
    "ArgmaxProcessor",
    "Chw2HwcProcessor",
    "Hwc2ChwProcessor",
    "MaskBinarizationProcessor",
    "MeanNormProcessor",
    "SqueezeNdimProcessor",
    "RGB2GrayProcessor",
]
