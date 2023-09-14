import json
from enum import Enum

from aiearth.predict.deploy.sdk.toolbox import Toolbox
from aiearth.predict.deploy.client import (
    ModelVersionClient,
    ToolboxClient,
)
from aiearth.predict.checkpoint import ModelCheckpoint, ModelConfig
from aiearth.predict.deploy.schema import (
    JobConfig,
    ToolboxRunConfig,
)


class SavedCodePackageType(Enum):
    JOB = 0
    TOOLBOX = 1
    SERVICE = 2


class Version:
    def __init__(self, version_id):
        self.version_id = version_id

    def __repr__(self):
        return json.dumps({"version_id": self.version_id})

    def delete_remote_version(self):
        return ModelVersionClient.delete(self.version_id)

    def save_model(self, ckpt: ModelCheckpoint):
        model_config: ModelConfig = ckpt.get_cfg()
        return ModelVersionClient.save_model(self.version_id, model_config)

    def list_saved_models(self):
        return ModelVersionClient.list_models(self.version_id)

    def deploy_as_toolbox(self, job_config: JobConfig, run_config: ToolboxRunConfig):
        working_dir = job_config.runtime_env.working_dir
        code_package_id = ModelVersionClient.save_package(
            self.version_id, working_dir, SavedCodePackageType.TOOLBOX.value
        )

        deploy_id = ToolboxClient.deploy(
            self.version_id,
            code_package_id,
            job_config,
            run_config,
        )
        return Toolbox(deploy_id)
