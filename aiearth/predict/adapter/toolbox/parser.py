import os
import json

from aiearth.predict.adapter.toolbox.input_args import InputArgs
from aiearth.predict.error import BizError, ErrorCode, ErrorMessage


def parse_input_args():
    working_dir = os.environ.get("WORKING_DIR")
    if not working_dir:
        raise BizError(
            ErrorCode.GET_ENV_ERROR,
            f"{ErrorMessage.GET_ENV_ERROR}:WORKING_DIR",
        )

    result_dir = os.path.join(working_dir, "result")
    temp_dir = os.path.join(working_dir, "tempdir")
    input_json = os.path.join(result_dir, "input.json")
    with open(input_json, "r", encoding="utf-8") as openfile:
        inps = json.load(openfile)

    src = inps["job_input"]["src"]
    src = src.replace("vsioss://", "/vsioss/")

    out_filename = "result"

    return InputArgs(
        working_dir=working_dir,
        result_dir=result_dir,
        temp_dir=temp_dir,
        src=src,
        out_filename=out_filename,
    )
