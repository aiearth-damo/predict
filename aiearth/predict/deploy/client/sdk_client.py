import requests

from aiearth.core.auth import Authenticate
from aiearth.core.client.endpoints import Endpoints
from aiearth.core.client.client import BaseClient as LocalClient

from aiearth.predict.config import constants, RuntimeEnvironment
from aiearth.predict.deploy.client.remote_client import RemoteClient
from aiearth.predict.error import BizError, ErrorCode, ErrorMessage


class SdkClient:
    host = (
        "http://hummer.default:10002"
        if constants.RUNTIME_ENVIRONMENT == RuntimeEnvironment.remote.value
        else Endpoints.HOST
    )

    client = (
        RemoteClient
        if constants.RUNTIME_ENVIRONMENT == RuntimeEnvironment.remote.value
        else LocalClient
    )

    @staticmethod
    def post(url, hdrs, data):
        return SdkClient.client.post(url, hdrs, data)

    @staticmethod
    def get(url, hdrs):
        return SdkClient.client.get(url, hdrs)

    @staticmethod
    def delete(url, hdrs):
        return SdkClient.client.delete(url, hdrs)
