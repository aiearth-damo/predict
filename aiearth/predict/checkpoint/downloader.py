import os
import json
import zipfile
import requests
import typing as t
from tqdm import tqdm

from aiearth.predict.utils import Package
from aiearth.predict.checkpoint.model_config import ModelAttachedFile
from aiearth.predict.deploy.client import ModelVersionClient
from aiearth.predict.error import BizError, ErrorCode, ErrorMessage
from aiearth.predict.logging import root_logger as logger


META_JSON = ".model_meta.json"
ATTACHED_FILES_DIR = "attached_files"


def http_get(url: str, file) -> None:
    req = requests.get(url, stream=True)
    content_length = req.headers.get("Content-Length")
    total = int(content_length) / 1024 if content_length is not None else None
    name = os.path.basename(file)
    with open(file, "wb") as f:
        for data in tqdm(
            iterable=req.iter_content(1024),
            total=total,
            unit="k",
            desc=f"download {name}",
        ):
            f.write(data)


def write_meta(working_dir, builder):
    json_object = json.dumps(builder, indent=4)
    path = os.path.join(working_dir, META_JSON)
    with open(path, "w", encoding="utf-8") as outfile:
        outfile.write(json_object)


def load_from_cache(working_dir):
    path = os.path.join(working_dir, META_JSON)
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as openfile:
                json_object = json.load(openfile)
            return json_object
    except:
        return None
    return None


def get_from_remote(tag: str, working_dir):
    os.makedirs(working_dir, exist_ok=True)

    builder = load_from_cache(working_dir)
    if builder:
        return builder
    else:
        model = ModelVersionClient.get_model(tag)

        builder = {"name": model["name"]}
        if "modelPath" not in model:
            raise BizError(
                ErrorCode.GET_MODEL_ERROR,
                f"{ErrorMessage.GET_MODEL_ERROR}: 返回缺少modelPath",
            )
        model_cached_path = os.path.join(working_dir, model["modelPath"]["fileName"])
        if not os.path.exists(model_cached_path):
            http_get(model["modelPath"]["downloadableLink"], model_cached_path)
        if zipfile.is_zipfile(model_cached_path):
            target_dir = os.path.join(
                working_dir, os.path.basename(model_cached_path).split()[0]
            )
            Package.unzip(
                model_cached_path,
                target_dir,
                remove_top_level_directory=True,
            )
            model_cached_path = target_dir
        builder["path"] = model_cached_path

        if "attachedFiles" in model:
            attached_files_args = {}
            for attached_file in model["attachedFiles"]:
                file_cached_path = os.path.join(
                    os.path.join(working_dir, ATTACHED_FILES_DIR),
                    attached_file["fileName"],
                )
                if not os.path.exists(file_cached_path):
                    os.makedirs(
                        os.path.join(working_dir, ATTACHED_FILES_DIR), exist_ok=False
                    )
                    http_get(attached_file["downloadableLink"], file_cached_path)

                args = ModelAttachedFile(
                    path=file_cached_path,
                    accelerator_type=attached_file["acceleratorType"],
                    params=attached_file["params"],
                )
                attached_files_args[attached_file["fileName"]] = args.dict()
            builder["attached_files"] = attached_files_args

        builder["params"] = model["params"]

        write_meta(working_dir, builder)

        return builder
