from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union, Callable, Tuple


class RuntimeEnv(BaseModel):
    working_dir: str
