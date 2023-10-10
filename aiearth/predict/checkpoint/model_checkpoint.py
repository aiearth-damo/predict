import os
import typing as t
from pydantic import BaseModel, Field

from ray.air.checkpoint import Checkpoint

from aiearth.predict.checkpoint.downloader import get_from_remote
from aiearth.predict.checkpoint.model_config import (
    ModelConfig,
    ModelAttachedFile,
    ModelParams,
    BuildType,
)
from aiearth.predict.error import BizError, ErrorCode, ErrorMessage


class ModelCheckpoint(Checkpoint):
    def get_cfg(self):
        return ModelConfig(**self.to_dict())

    @classmethod
    def from_local_path(
        cls,
        path: str,  # dir or file
        image_size: int = 1024,
        bound: int = 128,
        use_quant: bool = False,
        attached_files: t.Optional[t.Dict[str, ModelAttachedFile]] = None,
        **kwargs,
    ):
        if not os.path.exists(path):
            raise BizError(
                ErrorCode.PATH_EXIST_HINT_ERROR,
                f"{ErrorMessage.PATH_EXIST_HINT_ERROR}: {path}",
            )

        if attached_files is not None:
            for key, value in attached_files.items():
                if not os.path.exists(value.path):
                    raise BizError(
                        ErrorCode.PATH_EXIST_HINT_ERROR,
                        f"{ErrorMessage.PATH_EXIST_HINT_ERROR}: {value.path}",
                    )
                if not os.path.isfile(value.path):
                    raise BizError(
                        ErrorCode.FILE_HINT_ERROR,
                        f"{ErrorMessage.FILE_HINT_ERROR}: {value.path}",
                    )

        return cls.from_dict(
            {
                "path": path,
                "build_type": BuildType.local_path,
                "attached_files": attached_files,
                "params": {
                    "image_size": image_size,
                    "bound": bound,
                    "use_quant": use_quant,
                    "additional_args": kwargs,
                },
            }
        )

    @classmethod
    def from_model_scope(
        cls,
        path: str,
        image_size: int = 1024,
        bound: int = 128,
        **kwargs,
    ):
        return cls.from_dict(
            {
                "path": path,
                "build_type": BuildType.model_scope,
                "params": {
                    "image_size": image_size,
                    "bound": bound,
                    "additional_args": kwargs,
                },
            }
        )

    @classmethod
    def from_hugging_face(
        cls,
        path: str,
        image_size: int = 1024,
        bound: int = 128,
        **kwargs,
    ):
        return cls.from_dict(
            {
                "path": path,
                "build_type": BuildType.hugging_face,
                "params": {
                    "image_size": image_size,
                    "bound": bound,
                    "additional_args": kwargs,
                },
            }
        )

    @classmethod
    def from_remote_tag(
        cls,
        tag,
        model_cache_dir=None,
    ):
        split = tag.split(":")
        if len(split) != 2:
            raise BizError(
                ErrorCode.ARGS_FORMAT_ERROR,
                f"{ErrorMessage.ARGS_FORMAT_ERROR}: tag格式应为 name:tag",
            )

        if model_cache_dir is None:
            cache_home = os.environ.get("WORKING_DIR", os.path.expanduser("~"))
            cache_dir = os.path.join(cache_home, ".cache")
            model_cache_dir = os.path.join(cache_dir, "models")

        builder = get_from_remote(
            tag, os.path.join(model_cache_dir, tag.replace(":", "-"))
        )
        return cls.from_dict(builder)
