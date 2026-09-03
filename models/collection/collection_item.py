"""
对单个合集条目的操作。
"""


from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from ...data_models.collection import CollectionItemInfo
from .._sub_client import SubClient

if TYPE_CHECKING:
    from .collection_item_client import CollectionItemClient



class CollectionItem(SubClient):
    """
    单个合集。
    """

    def __init__(
        self,
        collection_item_client: CollectionItemClient,
        item_type: str,
        item_object_id: str,
    ):
        self._item_type = item_type
        self._item_object_id = item_object_id
        super().__init__(
            super_client=collection_item_client,
            prefix=f"{self.item_type}/{self.item_object_id}"
        )


    def __str__(self) -> str:
        return f"{type(self).__name__}<{self.item_type}/{self.item_object_id}>"


    # ==== 只读属性 ====

    @property
    def item_type(self) -> str:
        """
        资源类型：model / dataset / studio / paper / skill / mcp
        """
        return self._item_type


    @property
    def item_object_id(self) -> str:
        """
        资源标识
        """
        return self._item_object_id


    # ==== 对条目的操作 ====

    async def update(
        self,
        *,
        note: Optional[str] = None,
        position: Optional[int] = None,
        **kwargs
    ) -> CollectionItemInfo:
        """
        更新单个条目。传入哪个字段即更新哪个字段。

        Args:
            note: 备注（Markdown）。
            position: 排序位置（从 1 开始）。
        """
        kwargs["method"] = "PATCH"
        kwargs["subpath"] = None
        kwargs.setdefault("json", {}).update({
            "note": note,
            "position": position,
        })
        data = await self.request_openapi_data(**kwargs)
        return CollectionItemInfo.from_json(data)


    async def delete(self) -> None:
        """
        从合集中删除本条目。
        """
        await self.super_client.delete_item(
            item_type=self.item_type,
            item_object_id=self.item_object_id,
        )
