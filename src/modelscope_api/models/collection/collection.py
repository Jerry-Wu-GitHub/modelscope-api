"""
对单个合集的操作。
"""


from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from ...utils.regex import COLLECTION_SLUG_PATTERN
from ...data_models.collection import CollectionInfo, CollectionTheme, CollectionVisibility
from .._sub_client import SubClient
from .collection_item_client import CollectionItemClient

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
            openapi_prefix=self.slug
        )

        # 聚合子路由
        self.items = CollectionItemClient(self)


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
        self.openapi_prefix = self._slug
        return await self.get_info()


    async def delete(self) -> None:
        """
        删除当前合集。
        """
        await self.super_client.delete_collection(self.slug)
