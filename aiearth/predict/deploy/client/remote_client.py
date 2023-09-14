import os
import json
import requests

from aiearth.predict.config import constants, LogLevel
from aiearth.predict.error import BizError, ErrorCode, ErrorMessage
from aiearth.predict.logging import root_logger as logger


def append_extra_hdrs(hdrs):
    uid = os.environ.get("AIE_PREDICT_UID")
    if not uid:
        logger.error(f"{ErrorMessage.GET_ENV_ERROR}: AIE_PREDICT_UID")
        raise BizError(
            ErrorCode.GET_ENV_ERROR,
            f"{ErrorMessage.GET_ENV_ERROR}: AIE_PREDICT_UID",
        )
    hdrs["x-aie-uid"] = uid
    return hdrs


class RemoteClient:
    @staticmethod
    def post(url, hdrs, data):
        hdrs = append_extra_hdrs(hdrs)
        if constants.LOG_LEVEL == LogLevel.debug.value:
            logger.debug(
                f"RemoteClient::post request. url: {url}, headers: {json.dumps(hdrs)}, data: {json.dumps(data)}"
            )

        resp = requests.post(
            url=url, headers=hdrs, timeout=(600, 600), json=data, verify=False
        )

        if resp.status_code != 200:
            logger.error(f"{ErrorMessage.HTTP_REQUEST_ERROR}: {url}")
            raise BizError(
                ErrorCode.HTTP_REQUEST_ERROR,
                f"{ErrorMessage.HTTP_REQUEST_ERROR}",
            )

        if constants.LOG_LEVEL == LogLevel.debug.value:
            logger.debug(
                f"RemoteClient::post response. url: {url}, response: {resp.text}"
            )

        return resp

    @staticmethod
    def get(url, hdrs):
        hdrs = append_extra_hdrs(hdrs)

        if constants.LOG_LEVEL == LogLevel.debug.value:
            logger.debug(
                f"RemoteClient::get request. url: {url}, headers: {json.dumps(hdrs)}"
            )

        resp = requests.get(url=url, headers=hdrs, timeout=(600, 600), verify=False)

        if resp.status_code != 200:
            logger.error(f"{ErrorMessage.HTTP_REQUEST_ERROR}: {url}")
            raise BizError(
                ErrorCode.HTTP_REQUEST_ERROR,
                f"{ErrorMessage.HTTP_REQUEST_ERROR}",
            )

        if constants.LOG_LEVEL == LogLevel.debug.value:
            logger.debug(
                f"RemoteClient::get response. url: {url}, response: {resp.text}"
            )

        return resp

    @staticmethod
    def delete(url, hdrs, append_extra_hdrs=True):
        if append_extra_hdrs:
            hdrs = RemoteClient.__append_extra_hdrs(hdrs)

        if constants.LOG_LEVEL == LogLevel.debug.value:
            logger.debug(
                f"RemoteClient::delete request. url: {url}, headers: {json.dumps(hdrs)}"
            )

        resp = requests.delete(url=url, headers=hdrs, timeout=(600, 600), verify=False)

        if resp.status_code != 200:
            logger.error(f"{ErrorMessage.HTTP_REQUEST_ERROR}: {url}")
            raise BizError(
                ErrorCode.HTTP_REQUEST_ERROR,
                f"{ErrorMessage.HTTP_REQUEST_ERROR}",
            )

        if constants.LOG_LEVEL == LogLevel.debug.value:
            logger.debug(
                f"RemoteClient::delete response. url: {url}, response: {resp.text}"
            )

        return resp
