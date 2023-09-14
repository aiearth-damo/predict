from aiearth.predict.error import BizError, ErrorCode, ErrorMessage
from aiearth.predict.deploy.client.sdk_client import SdkClient


class UriResource:
    create = "sdk/model_project/create"
    delete = "sdk/model_project/delete"


class ModelProjectClient:
    @staticmethod
    def create(name):
        url = f"{SdkClient.host}/{UriResource.create}"
        hdrs = {"Content-Type": "application/json"}

        project = {
            "name": name,
        }
        reply = SdkClient.post(url, hdrs, project).json()
        if reply["code"] != 0:
            message = reply["message"]
            raise BizError(
                ErrorCode.MODEL_PROJECT_CREATE_ERROR,
                f"{ErrorMessage.MODEL_PROJECT_CREATE_ERROR}: {message}",
            )
        return reply["data"]

    @staticmethod
    def delete(model_project_id):
        url = f"{SdkClient.host}/{UriResource.delete}?modelProjectId={model_project_id}"
        hdrs = {"Content-Type": "application/json"}

        reply = SdkClient.delete(url, hdrs).json()
        if reply["code"] != 0:
            message = reply["message"]
            raise BizError(
                ErrorCode.MODEL_PROJECT_DELETE_ERROR,
                f"{ErrorMessage.MODEL_PROJECT_DELETE_ERROR}: {message}",
            )
