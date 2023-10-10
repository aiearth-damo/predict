import os
import sys
import oss2
import tqdm
import json
import urllib
import requests
from enum import Enum
from tempfile import NamedTemporaryFile, gettempdir

from aiearth.core.auth import Authenticate
from aiearth.predict.config import constants, LogLevel
from aiearth.predict.utils import Package
from aiearth.predict.deploy.client.sdk_client import SdkClient
from aiearth.predict.error import BizError, ErrorCode, ErrorMessage
from aiearth.predict.logging import root_logger as logger


class UriResource:
    create = "sdk/model_version/create"
    delete = "sdk/model_version/delete"
    upload_package = "sdk/model_version/upload_package"
    upload_model = "sdk/model_version/upload_model"
    upload_model_finished = "sdk/model_version/upload_model_finished"
    list_models = "sdk/model_version/list_models"
    get_model = "sdk/model_version/get_model"


class UploadModelStatus(Enum):
    WAITING = 0
    FINISHED = 1
    FAILED = 2


class ModelVersionClient:
    @staticmethod
    def create(model_project_id, version_name):
        url = f"{SdkClient.host}/{UriResource.create}"
        hdrs = {"Content-Type": "application/json"}

        version = {
            "modelProjectId": model_project_id,
            "versionName": version_name,
        }
        reply = SdkClient.post(url, hdrs, version).json()
        if reply["code"] != 0:
            message = reply["message"]
            raise BizError(
                ErrorCode.MODEL_VERSION_CREATE_ERROR,
                f"{ErrorMessage.MODEL_VERSION_CREATE_ERROR}: {message}",
            )
        return reply["data"]

    @staticmethod
    def delete(model_version_id):
        url = f"{SdkClient.host}/{UriResource.create}?modelVersionId={model_version_id}"
        hdrs = {"Content-Type": "application/json"}

        reply = SdkClient.delete(url, hdrs).json()
        if reply["code"] != 0:
            message = reply["message"]
            raise BizError(
                ErrorCode.MODEL_VERSION_DELETE_ERROR,
                f"{ErrorMessage.MODEL_VERSION_DELETE_ERROR}: {message}",
            )

    @staticmethod
    def upload_pacakge(model_version_id, zip_file, file_name_without_ext, deploy_type):
        url = f"{SdkClient.host}/{UriResource.upload_package}"
        data = {
            "modelVersionId": model_version_id,
            "fileNameWithoutExt": file_name_without_ext,
            "type": deploy_type,
        }
        files = {"file": open(zip_file, "rb")}
        hdrs = {"x-aie-auth-token": Authenticate.getCurrentUserToken()}

        if constants.LOG_LEVEL == LogLevel.debug.value:
            logger.debug(
                f"upload_pacakge request. url: {url}, headers: {json.dumps(hdrs)}, data: {json.dumps(data)}"
            )
        resp = requests.post(
            url=url,
            headers=hdrs,
            timeout=(600, 600),
            data=data,
            files=files,
            verify=False,
        )
        if constants.LOG_LEVEL == LogLevel.debug.value:
            logger.debug(f"upload_pacakge response. url: {url}, response: {resp.text}")

        if resp.status_code != 200:
            if "401 Authorization Required" in resp.text:
                raise BizError(
                    ErrorCode.PACKAGE_UPLOAD_ERROR,
                    f"{ErrorMessage.PACKAGE_UPLOAD_ERROR}: {ErrorMessage.UNAUTHORIZED}",
                )
            else:
                raise BizError(
                    ErrorCode.PACKAGE_UPLOAD_ERROR,
                    f"{ErrorMessage.PACKAGE_UPLOAD_ERROR}: {resp.text}",
                )

        reply = resp.json()
        if reply["code"] != 0:
            message = reply["message"]
            raise BizError(
                ErrorCode.PACKAGE_UPLOAD_ERROR,
                f"{ErrorMessage.PACKAGE_UPLOAD_ERROR}: {message}",
            )
        return reply["data"]

    @staticmethod
    def save_package(model_version_id, local_working_dir, deploy_type):
        if not os.path.exists(local_working_dir):
            raise BizError(
                ErrorCode.PATH_EXIST_HINT_ERROR,
                f"{ErrorMessage.PATH_EXIST_HINT_ERROR}:{local_working_dir}",
            )
        if not os.path.isdir(local_working_dir):
            raise BizError(
                ErrorCode.DIRECTORY_HINT_ERROR,
                f"{ErrorMessage.DIRECTORY_HINT_ERROR}:{local_working_dir}",
            )

        file_name_without_ext = os.path.basename(local_working_dir)
        tempdir = gettempdir() + os.sep
        with NamedTemporaryFile(prefix=tempdir, suffix=".zip", delete=True) as fp:
            local_package_path = fp.name
            Package.zip_directory(local_working_dir, local_package_path)
            saved_code_package = ModelVersionClient.upload_pacakge(
                model_version_id,
                local_package_path,
                file_name_without_ext,
                deploy_type,
            )
        return saved_code_package["id"]

    @staticmethod
    def upload(file, params):
        auth = oss2.StsAuth(
            params["accessKeyId"],
            params["accessKeySecret"],
            params["securityToken"],
        )
        bucket = oss2.Bucket(
            auth,
            "http://{}.aliyuncs.com".format(params["region"]),
            params["bucket"],
        )
        headers = {
            "Content-Disposition": f"attachment;filename={urllib.parse.quote(os.path.basename(file))}"
        }

        name = os.path.basename(file)

        def percentage(consumed_bytes, total_bytes):
            if total_bytes:
                rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
                print(f"\rsave {name} {rate}% ", end="")
                sys.stdout.flush()

        bucket.put_object_from_file(
            params["fileKey"], file, headers, progress_callback=percentage
        )

    @staticmethod
    def upload_model(model_version_id, name, path, attached_files, params):
        url = f"{SdkClient.host}/{UriResource.upload_model}"
        hdrs = {"Content-Type": "application/json"}
        path_file_name = os.path.basename(path)
        if os.path.isdir(path):
            path_file_name = path_file_name + ".zip"
        sign = {
            "modelVersionId": model_version_id,
            "modelName": name,
            "path": path,
            "fileName": path_file_name,
            "params": params,
        }

        if attached_files:
            sign["attachedFiles"] = attached_files

        reply = SdkClient.post(url, hdrs, sign).json()
        if reply["code"] != 0:
            message = reply["message"]
            raise BizError(
                ErrorCode.MODEL_UPLOAD_ERROR,
                f"{ErrorMessage.MODEL_UPLOAD_ERROR}: {message}",
            )
        return reply["data"]

    @staticmethod
    def upload_model_finished(model_version_id, model_storage_id, status):
        url = f"{SdkClient.host}/{UriResource.upload_model_finished}"
        hdrs = {"Content-Type": "application/json"}
        fin = {
            "modelVersionId": model_version_id,
            "modelStorageId": model_storage_id,
            "status": status,
        }

        reply = SdkClient.post(url, hdrs, fin).json()
        if reply["code"] != 0:
            message = reply["message"]
            raise BizError(
                ErrorCode.MODEL_UPLOAD_ERROR,
                f"{ErrorMessage.MODEL_UPLOAD_ERROR}: {message}",
            )
        return reply["data"]

    @staticmethod
    def save_model(model_version_id, model_config):
        if model_config.build_type == "local_path":
            ModelVersionClient.save_local_path_model(model_version_id, model_config)
        else:
            raise BizError(
                ErrorCode.NOT_SUPPORT_SAVE_MODEL,
                f"{ErrorMessage.NOT_SUPPORT_SAVE_MODEL} Checkpoint BuildType: {model_config.build_type}",
            )

    @staticmethod
    def save_model_scope_model(model_version_id, model_config):
        name = model_config.name
        if name is None:
            name = os.path.basename(model_config.path)
            if not os.path.isdir(model_config.path):
                name = os.path.splitext(name)[0]

        attached_files = {}
        if model_config.attached_files:
            for k, v in model_config.attached_files.items():
                attached_files[k] = v.dict()
        signed = ModelVersionClient.upload_model(
            model_version_id,
            name,
            model_config.path,
            attached_files,
            model_config.params.dict(),
        )

        model_id = signed.pop("id")
        model_tag = signed.pop("tag")
        if "path" not in signed:
            raise BizError(
                ErrorCode.MODEL_UPLOAD_ERROR,
                f"{ErrorMessage.MODEL_UPLOAD_ERROR}: signed response lack path",
            )

        try:
            params = signed["path"]
            raw_path = params.pop("rawPath")
            if os.path.isdir(raw_path):
                tempdir = gettempdir() + os.sep
                with NamedTemporaryFile(
                    prefix=tempdir, suffix=".zip", delete=True
                ) as fp:
                    package_path = fp.name
                    Package.zip_directory(raw_path, package_path)
                    ModelVersionClient.upload(package_path, params)
            else:
                ModelVersionClient.upload(raw_path, params)

            if "attachedFiles" in signed:
                for params in signed["attachedFiles"]:
                    raw_file_path = params.pop("rawPath")
                    ModelVersionClient.upload(raw_file_path, params)

            ModelVersionClient.upload_model_finished(
                model_version_id, model_id, UploadModelStatus.FINISHED.value
            )
        except Exception as e:
            import traceback

            message = str(e).replace("\n", " ")
            logger.error(f"{message}")

            ModelVersionClient.upload_model_finished(
                model_version_id, model_id, UploadModelStatus.FAILED.value
            )

            sys.exit(-1)

        return model_tag

    @staticmethod
    def save_local_path_model(model_version_id, model_config):
        name = model_config.name
        if name is None:
            name = os.path.basename(model_config.path)
            if not os.path.isdir(model_config.path):
                name = os.path.splitext(name)[0]

        attached_files = {}
        if model_config.attached_files:
            for k, v in model_config.attached_files.items():
                attached_files[k] = v.dict()
        signed = ModelVersionClient.upload_model(
            model_version_id,
            name,
            model_config.path,
            attached_files,
            model_config.params.dict(),
        )

        model_id = signed.pop("id")
        model_tag = signed.pop("tag")
        if "path" not in signed:
            raise BizError(
                ErrorCode.MODEL_UPLOAD_ERROR,
                f"{ErrorMessage.MODEL_UPLOAD_ERROR}: signed response lack path",
            )

        try:
            params = signed["path"]
            raw_path = params.pop("rawPath")
            if os.path.isdir(raw_path):
                tempdir = gettempdir() + os.sep
                with NamedTemporaryFile(
                    prefix=tempdir, suffix=".zip", delete=True
                ) as fp:
                    package_path = fp.name
                    Package.zip_directory(raw_path, package_path)
                    ModelVersionClient.upload(package_path, params)
            else:
                ModelVersionClient.upload(raw_path, params)

            if "attachedFiles" in signed:
                for params in signed["attachedFiles"]:
                    raw_file_path = params.pop("rawPath")
                    ModelVersionClient.upload(raw_file_path, params)

            ModelVersionClient.upload_model_finished(
                model_version_id, model_id, UploadModelStatus.FINISHED.value
            )
        except Exception as e:
            import traceback

            message = str(e).replace("\n", " ")
            logger.error(f"{message}")

            ModelVersionClient.upload_model_finished(
                model_version_id, model_id, UploadModelStatus.FAILED.value
            )

            sys.exit(-1)

        return model_tag

    @staticmethod
    def list_models(model_version_id):
        url = f"{SdkClient.host}/{UriResource.list_models}?modelVersionId={model_version_id}"
        hdrs = {"Content-Type": "application/json"}

        reply = SdkClient.get(url, hdrs).json()
        if reply["code"] != 0:
            message = reply["message"]
            raise BizError(
                ErrorCode.LIST_MODELS_ERROR,
                f"{ErrorMessage.LIST_MODELS_ERROR}: {message}",
            )
        return reply["data"]

    @staticmethod
    def get_model(model_tag):
        url = f"{SdkClient.host}/{UriResource.get_model}?modelTag={model_tag}"
        hdrs = {"Content-Type": "application/json"}

        reply = SdkClient.get(url, hdrs).json()
        if reply["code"] != 0:
            message = reply["message"]
            raise BizError(
                ErrorCode.GET_MODEL_ERROR,
                f"{ErrorMessage.GET_MODEL_ERROR}: {message}",
            )
        return reply["data"]
