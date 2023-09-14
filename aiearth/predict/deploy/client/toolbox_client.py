import requests

from aiearth.predict.deploy.client.sdk_client import SdkClient
from aiearth.predict.deploy.schema import JobConfig, ToolboxRunConfig
from aiearth.predict.deploy.client.toolbox_deploy_status import (
    ToolboxDeployStatus,
    code_to_toolbox_deploy_status,
)
from aiearth.predict.error import ErrorCode, ErrorMessage, BizError


class UriResource:
    deploy = "sdk/toolbox/deploy"
    get_deploy_status = "sdk/toolbox/get_deploy_status"
    undeploy = "sdk/toolbox/undeploy"


class ToolboxClient:
    @staticmethod
    def deploy(
        model_version_id,
        remote_package_id,
        job_config: JobConfig,
        run_config: ToolboxRunConfig,
    ):
        url = f"{SdkClient.host}/{UriResource.deploy}"
        hdrs = {"Content-Type": "application/json"}
        job = {
            "modelVersionId": model_version_id,
            "codePackageId": remote_package_id,
            "jobConfig": job_config.dict(),
            "runConfig": run_config.dict(),
        }

        reply = SdkClient.post(url, hdrs, job).json()
        if reply["code"] != 0:
            message = reply["message"]
            raise BizError(
                ErrorCode.TOOLBOX_DEPLOY_ERROR,
                f"{ErrorMessage.TOOLBOX_DEPLOY_ERROR}: {message}",
            )
        return reply["data"]

    @staticmethod
    def get_deploy_status(deploy_id):
        url = f"{SdkClient.host}/{UriResource.get_deploy_status}?deployId={deploy_id}"
        hdrs = {"Content-Type": "application/json"}
        reply = SdkClient.get(url, hdrs).json()
        if reply["code"] != 0:
            message = reply["message"]
            raise BizError(
                ErrorCode.TOOLBOX_GET_DEPLOY_STATUS_ERROR,
                f"{ErrorMessage.TOOLBOX_GET_DEPLOY_STATUS_ERROR}: {message}",
            )
        status_response = reply["data"]
        deploy_status = code_to_toolbox_deploy_status(status_response["deployStatus"])

        if deploy_status == ToolboxDeployStatus.failed:
            return deploy_status, (
                status_response["errorCode"],
                status_response["errorMsg"],
            )
        else:
            return deploy_status, (0, "")

    @staticmethod
    def undeploy(deploy_id):
        url = f"{SdkClient.host}/{UriResource.stop}?deployId={deploy_id}"
        hdrs = {"Content-Type": "application/json"}
        reply = SdkClient.delete(url, hdrs).json()
        if reply["code"] != 0:
            message = reply["message"]
            raise BizError(
                ErrorCode.TOOLBOX_UNDEPLOY_ERROR,
                f"{ErrorMessage.TOOLBOX_UNDEPLOY_ERROR}: {message}",
            )
