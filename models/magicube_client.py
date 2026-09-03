"""
集成封装与魔粒体系有关的 API。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..data_models.magicube import MagicubeBalanceInfo
from ._sub_client import SubClient

if TYPE_CHECKING:
    from .modelscope_client import ModelScopeClient


class MagicubeClient(SubClient):
    """
    集成封装与魔粒（Magicube）有关的 API。
    """

    def __init__(
        self,
        modelscope_client: ModelScopeClient,
        *,
        prefix: str = "magicubes"
    ):
        super().__init__(
            super_client=modelscope_client,
            prefix=prefix
        )


    # ==== 查询魔粒余额 ====

    async def query_magicube_balance(self, **kwargs) -> MagicubeBalanceInfo:
        """
        查询当前用户的魔粒余额信息。

        Raises:
            ModelScopeException: 如果未登录。
        """
        kwargs["method"] = "GET"
        kwargs["subpath"] = "balance"
        data = await self.request_openapi_data(**kwargs)
        return MagicubeBalanceInfo.from_json(data)
