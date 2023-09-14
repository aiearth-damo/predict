import typing as t
from pydantic import BaseModel, Field


class InputArgs(BaseModel):
    working_dir: str
    temp_dir: str
    result_dir: str
    src: str
    out_filename: str
