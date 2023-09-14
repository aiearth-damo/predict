from aiearth.predict.error import BizError, ErrorCode, ErrorMessage


class ToolboxDeployStatus:
    waiting = "waiting"
    deploying = "deploying"
    finished = "finished"
    failed = "failed"
    undeploying = "undeploying"
    undeployed = "undeployed"


def code_to_toolbox_deploy_status(code):
    if code == 0:
        return ToolboxDeployStatus.waiting
    elif code == 1:
        return ToolboxDeployStatus.deploying
    elif code == 2:
        return ToolboxDeployStatus.finished
    elif code == 3:
        return ToolboxDeployStatus.failed
    elif code == 4:
        return ToolboxDeployStatus.undeploying
    elif code == 5:
        return ToolboxDeployStatus.undeployed
    else:
        raise BizError(
            ErrorCode.TOOLBOX_GET_DEPLOY_STATUS_ERROR,
            f"{ErrorMessage.TOOLBOX_GET_DEPLOY_STATUS_ERROR}: 状态码 {code} 不支持",
        )
