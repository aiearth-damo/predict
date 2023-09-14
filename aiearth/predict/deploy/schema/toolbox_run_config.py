from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from enum import Enum


class JobOutType(Enum):
    RASTER = "raster"
    VECTOR = "vector"


class ToolboxRunConfig(BaseModel):
    out_type: JobOutType

    class Config:
        use_enum_values = True
