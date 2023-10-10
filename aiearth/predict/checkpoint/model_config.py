import typing as t
from enum import Enum
from pydantic import BaseModel, Field


class AcceleratorType(Enum):
    t4 = "t4"


class ModelAttachedFile(BaseModel):
    path: str
    accelerator_type: t.Optional[AcceleratorType]
    params: t.Optional[t.Dict]

    class Config:
        use_enum_values = True


class ModelParams(BaseModel):
    image_size: t.Optional[int]
    bound: t.Optional[int]
    use_quant: t.Optional[bool]
    additional_args: t.Optional[dict]


class BuildType(Enum):
    local_path = "local_path"
    model_scope = "model_scope"
    hugging_face = "hugging_face"


class ModelConfig(BaseModel):
    name: t.Optional[str]
    path: str
    build_type: BuildType
    attached_files: t.Optional[t.Dict[str, ModelAttachedFile]]
    params: ModelParams

    class Config:
        use_enum_values = True
