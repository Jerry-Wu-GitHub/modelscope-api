"""
对单个合集的操作。
"""


from __future__ import annotations

from typing import Dict, Iterable, List, Optional, TYPE_CHECKING

from ..utils.regex import COLLECTION_SLUG_PATTERN
from ..utils.typing import JsonObject
from ..data_models.collection import CollectionInfo, CollectionTheme, CollectionVisibility
from ..data_models.collection_item import CollectionItemType, CollectionItemInfo
from ._sub_client import SubClient
from .collection_item import CollectionItem

if TYPE_CHECKING:
    from .collection_client import CollectionClient



class Collection(SubClient):
    """
    单个合集。
    """

    def __init__(self, collection_client: CollectionClient, slug: str):
        self._slug = slug
        assert COLLECTION_SLUG_PATTERN.fullmatch(self.slug), f"Invalid collection slug: {self.slug}"
        super().__init__(
            super_client=collection_client,
            prefix=self.slug
        )


    def __str__(self) -> str:
        return f"{type(self).__name__}<{self.slug}>"


    # ==== 只读属性 ====

    @property
    def slug(self) -> str:
        """
        Collection slug (owner/name)
        """
        return self._slug


    @property
    def owner(self) -> str:
        """
        拥有者（个人用户名或组织名）
        """
        return self._slug.split("/")[0]


    @property
    def name(self) -> str:
        """
        合集英文名。
        """
        return self._slug.split("/")[1]


    # ==== 合集操作 ====

    async def get_info(self, **kwargs) -> CollectionInfo:
        """
        获取当前 Collection 的详细信息。

        visibility=public 时可以不认证；visibility=private 时必须认证。
        """
        kwargs["method"] = "GET"
        kwargs["subpath"] = None
        data = await self.request_openapi_data(**kwargs)
        return CollectionInfo.from_json(data)


    async def update(
        self,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        owner: Optional[str] = None,
        visibility: Optional[CollectionVisibility] = None,
        theme: Optional[CollectionTheme] = None,
        **kwargs
    ) -> CollectionInfo:
        """
        更新 Collection 元数据。传入哪个字段即更新哪个字段，未传字段保持原值。

        open/close 语义映射为 visibility（public/private）。

        Args:
            title: Collection 标题（最长 128 字符）。
            description: Collection 描述（Markdown）。
            owner: 所有者（用户名或组织名）。
            visibility: 可见性：public / private。
            theme: 主题标签，枚举值：Blue/Pink/Purple/Cyan。
        """
        kwargs["method"] = "PATCH"
        kwargs["subpath"] = None
        kwargs.setdefault("json", {}).update({
            "title": title,
            "description": description,
            "owner": owner,
            "visibility": visibility,
            "theme": theme,
        })
        data = await self.request_openapi_data(**kwargs)
        self._slug = data["slug"]
        self.prefix = self._slug
        return await self.get_info()


    async def delete(self) -> None:
        """
        删除当前合集。
        """
        await self.super_client.delete_collection(self.slug)


    # ==== 条目操作 ====

    async def get_item_infos(
        self,
        item_type: Optional[CollectionItemType] = None,
        page_number: int = 1,
        page_size: int = 10,
        **kwargs
    ) -> List[CollectionItemInfo]:
        """
        分页获取指定 Collection 的条目列表，支持按资源类型过滤。

        visibility=public 时 Token 可选；private 时必填。

        Args:
            item_type: 按资源类型过滤：model / dataset / studio / paper / skill / mcp。
            page_number: 页码（≥1）。
            page_size: 每页大小（1~50）。
        """
        kwargs["method"] = "GET"
        kwargs["subpath"] = "items"
        kwargs.setdefault("params", {}).update({
            "item_type": item_type,
            "page_number": page_number,
            "page_size": page_size,
        })
        data = await self.request_openapi_data(**kwargs)
        collection_item_infos = list(map(
            CollectionItemInfo.from_json,
            data.get("items") or []
        ))
        return collection_item_infos


    @staticmethod
    def _extract_item_infos(items: Iterable[CollectionItemInfo | JsonObject]) -> List[Dict[str, str | int]]:
        """
        从给定的 items 列表中提取 item 的主要信息：
        - item_type （必须）
        - item_object_id （必须）
        - note （可选）
        - position （添加时必须，更新时可选）
        """
        item_list = []
        for item in items:
            # 统一转换为 CollectionItemInfo 类型
            if isinstance(item, dict):
                item_info = CollectionItemInfo.from_json(item)
            elif isinstance(item, CollectionItemInfo):
                item_info = item
            else:
                continue

            # 添加到列表中
            item_to_be_added = {
                "item_type": item_info.item_type,
                "item_object_id": item_info.item_object_id,
            }
            if item_info.note is not None:
                item_to_be_added["note"] = item_info.note
            if item_info.position is not None:
                item_to_be_added["position"] = item_info.position
            item_list.append(item_to_be_added)

        return item_list


    async def add_items(
        self,
        items: Iterable[CollectionItemInfo | JsonObject],
        **kwargs
    ) -> List[CollectionItemInfo]:
        """
        向 Collection 批量添加条目。传入 items 数组。

        Args:
            items: 条目信息列表。
                对于其中的每个条目，需要有 item_type, item_object_id, position 字段；note 字段是可选的。

        Returns:
            添加失败的条目列表。每个条目有 reason 属性指示其失败原因。
        """
        kwargs["method"] = "POST"
        kwargs["subpath"] = "items"

        # 往请求体中添加 items 列表
        item_list = kwargs.setdefault("json", {}).setdefault("items", [])
        item_list.extend(self._extract_item_infos(items))

        # 发送请求
        data = await self.request_openapi_data(**kwargs)

        # 失败的条目
        failed_item_infos = list(map(
            CollectionItemInfo.from_json,
            data.get("failed_items") or []
        ))
        return failed_item_infos


    async def update_items(
        self,
        items: Iterable[CollectionItemInfo | JsonObject],
        **kwargs
    ) -> List[CollectionItemInfo]:
        """
        批量更新 Collection 条目。

        通过每个条目的 item_type + item_object_id 定位，传入哪个字段就修改哪个字段。

        Args:
            items: 条目信息列表。
                对于其中的每个条目，需要有 item_type 和 item_object_id 字段；note 和 position 字段是可选的。

        Returns:
            更新失败的条目列表。每个条目有 reason 属性指示其失败原因。
        """
        kwargs["method"] = "PATCH"
        kwargs["subpath"] = "items"

        # 往请求体中添加 items 列表
        item_list = kwargs.setdefault("json", {}).setdefault("items", [])
        item_list.extend(self._extract_item_infos(items))

        # 如果没有要修改的条目，则直接返回
        if not item_list:
            return []

        # 发送请求
        data = await self.request_openapi_data(**kwargs)

        # 失败的条目
        failed_item_infos = list(map(
            CollectionItemInfo.from_json,
            data.get("failed_items") or []
        ))
        return failed_item_infos


    async def delete_item(
        self,
        item_type: str,
        item_object_id: str,
        **kwargs
    ) -> None:
        """
        通过 item_type + item_object_id 定位并从 Collection 中移除单个条目。

        Args:
            item_type: 资源类型：model / dataset / studio / paper / skill / mcp
            item_object_id: 资源标识，如 damo/nlp_bert_base。
                可包含 /（作为 items/{item_type}/ 之后的整段剩余路径），无需 URL 编码。
        """
        kwargs["method"] = "DELETE"
        kwargs["subpath"] = f"items/{item_type}/{item_object_id}"
        await self.request_openapi_data(**kwargs)


    # ==== 获得条目对象 ====

    def get_item(
        self,
        item_type: str,
        item_object_id: str,
    ) -> CollectionItem:
        """
        构造 CollectionItem 对象。
        """
        return CollectionItem(
            collection=self,
            item_type=item_type,
            item_object_id=item_object_id,
        )


    async def get_items(
        self,
        item_type: Optional[CollectionItemType] = None,
        page_number: int = 1,
        page_size: int = 10,
        **kwargs
    ) -> List[CollectionItem]:
        """
        分页获取指定 Collection 的条目列表，支持按资源类型过滤。

        visibility=public 时 Token 可选；private 时必填。

        Args:
            item_type: 按资源类型过滤：model / dataset / studio / paper / skill / mcp。
            page_number: 页码（≥1）。
            page_size: 每页大小（1~50）。
        """
        collection_item_infos = await self.get_item_infos(
            item_type=item_type,
            page_number=page_number,
            page_size=page_size,
            **kwargs
        )
        return [
            self.get_item(
                item_type=item_info.item_type,
                item_object_id=item_info.item_object_id
            )
            for item_info in collection_item_infos
        ]
