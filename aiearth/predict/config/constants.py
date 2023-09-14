import os

from aiearth.predict.config.runtime_environment import RuntimeEnvironment
from aiearth.predict.config.log_level import LogLevel

RUNTIME_ENVIRONMENT = os.environ.get(
    "RUNTIME_ENVIRONMENT", RuntimeEnvironment.local.value
)
LOG_LEVEL = os.environ.get("AIE_PREDICT_LOG_LEVEL", LogLevel.info.value)
