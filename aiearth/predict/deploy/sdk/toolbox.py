import json

from aiearth.predict.deploy.client import ToolboxClient


class Toolbox:
    def __init__(self, deploy_id):
        self.deploy_id = deploy_id

    def get_deploy_status(self):
        return ToolboxClient.get_deploy_status(self.deploy_id)

    def undeploy(self):
        return ToolboxClient.undeploy(self.deploy_id)

    def __repr__(self):
        return json.dumps({"deploy_id": self.deploy_id})
