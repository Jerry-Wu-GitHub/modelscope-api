"""
集成封装子路由的 API。
"""

from __future__ import annotations

from typing import List, Optional, Union, TYPE_CHECKING

from yarl import URL

if TYPE_CHECKING:
    from .modelscope_client import ModelScopeClient, JsonObject


class SubClient:
    """
    集成封装子路由的 API。
    """

    def __init__(
        self,
        super_client: Union[ModelScopeClient, SubClient],
        *,
        api_prefix: Optional[str] = None,
        openapi_prefix: Optional[str] = None,
    ):
        """
        Args:
            super_client: 上一级路由的 HTTP 客户端。
            api_prefix: 要接在父级 api_url 后的前缀。
            openapi_prefix: 要接在父级 openapi_prefix 后的前缀。
        """
        self.super_client = super_client
        self.api_prefix: Optional[str] = api_prefix
        self.openapi_prefix: Optional[str] = openapi_prefix


    # ==== API ====

    @property
    def api_url(self) -> URL:
        """
        The URL of API sub interface.

        Returns like:
            "https://www.modelscope.cn/api/v1/studio"
        """
        if self.api_prefix is None:
            return self.super_client.api_url
        return self.super_client.api_url / self.api_prefix


    def get_api_url(self, subpath: Optional[str] = None) -> URL:
        """
        拼接完整的 API 路由。
        """
        if subpath is None:
            return self.api_url
        return self.api_url / subpath


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
        if subpath is None:
            subpath = self.api_prefix
        else:
            subpath = f"{self.api_prefix}/{subpath}"
        return await self.super_client.request_api_data(
            subpath=subpath,
            data_field=data_field,
            **kwargs
        )


    # ==== OpenAPI ====

    @property
    def openapi_url(self) -> URL:
        """
        The URL of OpenAPI sub interface.

        Returns like:
            "https://modelscope.cn/openapi/v1/studios"
        """
        if self.openapi_prefix is None:
            return self.super_client.openapi_url
        return self.super_client.openapi_url / self.openapi_prefix


    def get_openapi_url(self, subpath: Optional[str] = None) -> URL:
        """
        拼接完整的 OpenAPI 路由。
        """
        if subpath is None:
            return self.openapi_url
        return self.openapi_url / subpath


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
        if subpath is None:
            subpath = self.openapi_prefix
        else:
            subpath = f"{self.openapi_prefix}/{subpath}"
        return await self.super_client.request_openapi_data(
            subpath=subpath,
            data_field=data_field,
            **kwargs
        )
