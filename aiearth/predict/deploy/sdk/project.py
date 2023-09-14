import json

from aiearth.predict.deploy.client import (
    ModelProjectClient,
    ModelVersionClient,
    ToolboxClient,
)
from aiearth.predict.deploy.schema import (
    JobConfig,
    ToolboxRunConfig,
)
from aiearth.predict.deploy.sdk.version import Version
from aiearth.predict.error import BizError, ErrorCode


class Project:
    def __init__(self, project_id):
        self.project_id = project_id

    @classmethod
    def create(cls, project_name):
        project_id = ModelProjectClient.create(project_name)
        return cls(project_id)

    def delete_remote_project(self):
        return ModelProjectClient.delete(self.project_id)

    def create_version(self, version_name):
        version_id = ModelVersionClient.create(self.project_id, version_name)
        return Version(version_id)

    def __repr__(self):
        return json.dumps({"project_id": self.project_id})
