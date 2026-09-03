"""
对所有 API 的聚合。
"""

import json
from typing import Any, Dict, List, Optional, Union

from fake_useragent import UserAgent
import httpx
from typing_extensions import Self
from yarl import URL

from ..config import (
    MODELSCOPE_API_TOKEN,
    MODELSCOPE_API_VERSION,
    MODELSCOPE_API_BASE_URL,
    MODELSCOPE_OPENAPI_BASE_URL,
    MODELSCOPE_OPENAPI_VERSION,
)
from ..exceptions import ParseException, ModelScopeException
from ..utils.typing import JsonObject
from .collection import CollectionClient
from .magicube import MagicubeClient
from .studio import StudioClient
from .user import UserClient


class ModelScopeClient:
    """Client that requests APIs of ModelScope."""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        api_base_url     : Optional[Union[str, URL]] = None,
        api_version      : Optional[str]             = None,
        openapi_base_url : Optional[Union[str, URL]] = None,
        openapi_version  : Optional[str]             = None,
        http_client: Optional[httpx.AsyncClient] = None,
        **kwargs
    ):
        """
        Args:
            api_key: to obtain: https://www.modelscope.cn/my/settings/token
                It can be passed in through the environment variable `MODELSCOPE_API_TOKEN`.
                This will overwrite the header::Authorization in http_cient.
            api_base_url: The base URL of ModelScope webpage API,
                defaults to `"https://www.modelscope.cn/api"`.
            api_version: The version of the API, defaults to `"v1"`.
            openapi_base_url: to obtain: https://www.modelscope.cn/docs/openapi
                The base URL of ModelScope OpenAPI,
                defaults to `"https://modelscope.cn/openapi"`.
            openapi_version: The version of the OpenAPI, defaults to `"v1"`.
            http_client: An HTTP‑client object with the same methods
                as `httpx.AsyncClient.request`, used for sending network requests.
            kwargs: The initialization parameters passed to `http_client`.
        """
        # API Token
        if api_key is None:
            api_key = MODELSCOPE_API_TOKEN

        self.api_key: Optional[str] = api_key

        # API URL
        if api_base_url is None:
            api_base_url = MODELSCOPE_API_BASE_URL
        if api_version is None:
            api_version = MODELSCOPE_API_VERSION

        self.api_base_url: URL = URL(api_base_url)
        self.api_version: str = api_version

        # Open API URL
        if openapi_base_url is None:
            openapi_base_url = MODELSCOPE_OPENAPI_BASE_URL
        if openapi_version is None:
            openapi_version = MODELSCOPE_OPENAPI_VERSION

        self.openapi_base_url: URL = URL(openapi_base_url)
        self.openapi_version: str = openapi_version

        # HTTP Client
        self._http_client_is_local: bool = http_client is None
        if self._http_client_is_local:
            http_client = httpx.AsyncClient(**kwargs)
        self._http_client = http_client
        self._kwargs: Dict[str, Any] = kwargs.copy()

        # 添加伪造的 User-Agent 头
        headers = self._kwargs.setdefault("headers", {})
        if "user-agent" not in headers:
            headers["user-agent"] = UserAgent().random # 生成随机 UA

        # 聚合子路由
        self.collection = CollectionClient(self)
        self.magicube = MagicubeClient(self)
        self.studio = StudioClient(self)
        self.user = UserClient(self)


    async def __aenter__(self) -> Self:
        if self._http_client_is_local:
            await self._http_client.__aenter__()
        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._http_client_is_local:
            await self._http_client.__aexit__(exc_type, exc_val, exc_tb)


    async def aclose(self) -> None:
        """Close the client within the instance."""
        if self._http_client_is_local:
            await self._http_client.aclose()


    @property
    def api_url(self) -> URL:
        """
        The URL of API interface.

        Returns like:
            "https://www.modelscope.cn/api/v1"
        """
        return self.api_base_url / self.api_version


    def get_api_url(self, subpath: Optional[str] = None) -> URL:
        """
        拼接完整的 API 路由。
        """
        if subpath is None:
            return self.api_url
        return self.api_url / subpath


    @property
    def openapi_url(self) -> URL:
        """
        The URL of OpenAPI interface.

        Returns like:
            "https://modelscope.cn/openapi/v1"
        """
        return self.openapi_base_url / self.openapi_version


    def get_openapi_url(self, subpath: Optional[str] = None) -> URL:
        """
        拼接完整的 OpenAPI 路由。
        """
        if subpath is None:
            return self.openapi_url
        return self.openapi_url / subpath


    # ==== 发送请求 ====

    def _get_kwargs(self, kwargs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        将给定的关键字参数与本客户端的合并并输出。

        具体来说，该方法会合并以下内容（按优先级从大到小排序）并返回：
        - 调用本方法时输入的 `kwargs`
        - "headers": {"Authorization": "Bearer api_key"} （如果 self.api_key 存在）
        - 初始化本客户端时输入的 `kwargs`
        """
        result = self._kwargs.copy()
        if self.api_key:
            result.setdefault("headers", {}).update({
                "Authorization": f"Bearer {self.api_key}"
            })
        if kwargs:
            for key, value in kwargs.items():
                if isinstance(value, dict):
                    result.setdefault(key, {}).update(value)
                else:
                    result[key] = value
        return result


    async def request(self, **kwargs) -> httpx.Response:
        """
        用该客户端发送请求。
        """
        kwargs = self._get_kwargs(kwargs)
        response = await self._http_client.request(**kwargs)
        return response


    async def request_data(
        self,
        *,
        data_field: str = "data",
        **kwargs
    ) -> Optional[JsonObject | List[JsonObject]]:
        """
        发送请求，并返回响应体中的字段 `data_field` （默认为 `"data"`）的值。
        如果响应体中没有 `data_field` 字段，则返回整个响应体。

        Raises:
            ParseException: 如果解析失败。
            ModelScopeException: 如果请求失败。
        """
        response = await self.request(**kwargs)

        # 解析响应体
        try:
            resp_json = response.json()
        except json.JSONDecodeError as exp:
            raise ParseException(
                code="JSON DECODE ERROR",
                message=f"unexpected json string: {response.text}"
            ) from exp

        # 把响应体的字段名一律改成小写
        resp_json = {key.lower(): value for key, value in resp_json.items()}

        # 判断请求是否失败
        if not resp_json.get("success", True):
            raise ModelScopeException(
                code=str(resp_json.get("code")),
                message=resp_json.get("message")
            )

        if data_field in resp_json:
            return resp_json[data_field]
        return resp_json


    async def request_api_data(
        self,
        subpath: Optional[str] = None,
        *,
        data_field="data",
        **kwargs
    ) -> Optional[JsonObject | List[JsonObject]]:
        """
        向 ModelScope API 发送请求，并返回响应体中的字段 `data_field` （默认为 "data"）的值。
        如果响应体中没有 `data_field` 字段，则返回整个响应体。

        Args:
            subpath: 在 `self.api_url` 之后要拼接的子路径。
                不能以 `/` 开头。

        Raises:
            ParseException: 如果解析失败。
            ModelScopeException: 如果请求失败。
        """
        kwargs["url"] = str(self.get_api_url(subpath))
        return await self.request_data(data_field=data_field, **kwargs)


    async def request_openapi_data(
        self,
        subpath: Optional[str] = None,
        *,
        data_field="data",
        **kwargs
    ) -> Optional[JsonObject | List[JsonObject]]:
        """
        向 ModelScope OpenAPI 发送请求，并返回响应体中的字段 `data_field` （默认为 "data"）的值。
        如果响应体中没有 `data_field` 字段，则返回整个响应体。

        Args:
            subpath: 在 `self.openapi_url` 之后要拼接的子路径。
                不能以 `/` 开头。

        Raises:
            ParseException: 如果解析失败。
            ModelScopeException: 如果请求失败。
        """
        kwargs["url"] = str(self.get_openapi_url(subpath))
        return await self.request_data(data_field=data_field, **kwargs)
