from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union, Callable, Tuple

from aiearth.predict.deploy.schema.runtime_env import RuntimeEnv


class JobConfig(BaseModel):
    entrypoint: str
    runtime_env: RuntimeEnv
