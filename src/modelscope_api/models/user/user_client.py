"""
集成封装与用户（User）有关的 API。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...data_models.user import UserInfo
from .._sub_client import SubClient

if TYPE_CHECKING:
    from ..modelscope_client import ModelScopeClient



class UserClient(SubClient):
    """
    集成封装与用户（User）有关的 API。
    """

    def __init__(
        self,
        modelscope_client: ModelScopeClient,
        *,
        prefix: str = "users"
    ):
        super().__init__(
            super_client=modelscope_client,
            prefix=prefix
        )


    # ==== 查询用户信息 ====

    async def get_current_user_info(self, **kwargs) -> UserInfo:
        """
        获取当前已认证用户的个人信息。

        Raises:
            ModelScopeException: 如果未登录。
        """
        kwargs["method"] = "GET"
        kwargs["subpath"] = "me"
        data = await self.request_openapi_data(**kwargs)
        return UserInfo.from_json(data)
