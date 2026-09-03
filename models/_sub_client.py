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
        prefix: str
    ):
        self.super_client = super_client
        self.prefix = prefix


    @property
    def openapi_url(self) -> URL:
        """
        The URL of OpenAPI sub interface.

        Returns like:
            "https://modelscope.cn/openapi/v1/studios"
        """
        return self.super_client.openapi_url / self.prefix


    def get_openapi_url(self, subpath: Optional[str] = None) -> URL:
        """
        拼接完整的路由。
        """
        if subpath is None:
            return self.openapi_url
        return self.openapi_url / subpath


    async def request_openapi_data(
        self,
        subpath: Optional[str] = None,
        **kwargs
    ) -> Optional[JsonObject | List[JsonObject]]:
        """
        向 ModelScope OpenAPI 的子接口发送请求，并返回响应体中的 `data` 字段。
        如果响应体中没有 `data` 字段，则返回整个响应体。

        Args:
            subpath: 在 `self.openapi_url` 之后要拼接的子路径。
                不能以 `/` 开头。

        Raises:
            ParseException: 如果解析失败。
            ModelScopeException: 如果请求失败。
        """
        if subpath is None:
            subpath = self.prefix
        else:
            subpath = f"{self.prefix}/{subpath}"
        return await self.super_client.request_openapi_data(subpath=subpath, **kwargs)
