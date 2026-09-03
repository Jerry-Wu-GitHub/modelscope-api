"""
对单个创空间的环境变量的操作。
"""

from __future__ import annotations

from typing import List, TYPE_CHECKING

from ...data_models.studio import EnvironmentVariableInfo, EnvironmentVariableType
from .._sub_client import SubClient

if TYPE_CHECKING:
    from .studio import Studio


class EnvironmentVariableClient(SubClient):
    """
    操作单个创空间的环境变量。
    """

    def __init__(
        self,
        studio: Studio,
        type: EnvironmentVariableType,
    ):
        self.type: EnvironmentVariableType = EnvironmentVariableType(type)
        super().__init__(
            super_client=studio,
            prefix=f"{self.type}s"
        )


    async def get_all(self, **kwargs) -> List[EnvironmentVariableInfo]:
        """
        获取当前 Studio 的所有环境变量的 key 和 value。

        密文变量的值不可见。
        """
        kwargs["method"] = "GET"
        kwargs["subpath"] = None
        data = await self.request_openapi_data(**kwargs)
        environment_variable_infos = list(map(
            EnvironmentVariableInfo.from_json,
            data.get(self.prefix) or []
        ))
        return environment_variable_infos


    async def add(
        self,
        key: str,
        value: str,
        **kwargs
    ) -> None:
        """
        为当前的 Studio 添加一个环境变量.

        明文变量的 key 和 value 都公开可见，敏感信息请使用密文变量接口。

        Args:
            key: 变量名称。
            value: 变量值。
        """
        kwargs["method"] = "POST"
        kwargs["subpath"] = None
        kwargs.setdefault("json", {}).update({
            "key": key,
            "value": value,
        })
        await self.request_openapi_data(**kwargs)


    async def update(
        self,
        key: str,
        value: str,
        **kwargs
    ) -> None:
        """
        更新当前 Studio 的一个环境变量值。

        Args:
            key: 变量名称。
            value: 变量新值。
        """
        kwargs["method"] = "PUT"
        kwargs["subpath"] = None
        kwargs.setdefault("json", {}).update({
            "key": key,
            "value": value,
        })
        await self.request_openapi_data(**kwargs)


    async def delete(self, key: str, **kwargs) -> None:
        """
        删除当前 Studio 的一个环境变量。

        Args:
            key: 变量名称。
        """
        kwargs["method"] = "DELETE"
        kwargs["subpath"] = None
        kwargs.setdefault("json", {}).update({
            "key": key,
        })
        await self.request_openapi_data(**kwargs)
