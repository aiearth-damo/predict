from aiearth.core.env import set_log_level

import aiearth.predict.config.constants
from aiearth.predict.config.runtime_environment import RuntimeEnvironment
from aiearth.predict.config.log_level import LogLevel

if constants.LOG_LEVEL == LogLevel.debug.value:
    set_log_level("debug")


__all__ = [
    "constants",
    "RuntimeEnvironment",
    "LogLevel",
]
