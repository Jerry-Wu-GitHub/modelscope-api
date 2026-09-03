"""
集成封装与合集（Collection）有关的 API。
"""

from __future__ import annotations

from typing import List, Literal, Optional, TYPE_CHECKING

from ..data_models.collection import CollectionInfo, CollectionTheme, CollectionVisibility
from ._sub_client import SubClient
from .collection import Collection

if TYPE_CHECKING:
    from .modelscope_client import ModelScopeClient


class CollectionClient(SubClient):
    """
    集成封装与合集（Collection）有关的 API。
    """

    def __init__(
        self,
        modelscope_client: ModelScopeClient,
        *,
        prefix: str = "collections"
    ):
        super().__init__(
            super_client=modelscope_client,
            prefix=prefix
        )


    # ==== 查询合集信息 ====

    async def search_collection_infos(
        self,
        search: Optional[str] = None,
        owner: Optional[str] = None,
        *,
        sort: Optional[Literal["default", "last_modified", "likes"]] = None,
        page_number: int = 1,
        page_size: int = 10,
        **kwargs
    ) -> List[CollectionInfo]:
        """
        获取 Collection 列表，支持搜索、按所有者过滤与排序、分页。

        公开列表无需用户认证；查询私有 Collection 需要认证。

        Args:
            search: 针对标题、描述的子字符串搜索。
            owner: 所有者过滤。
                仅允许过滤当前 Token 所属用户自己的 Collection，过滤他人（或匿名使用）返回 403 OperationNotAllowed。
            sort: 排序方式：default（默认综合）/ last_modified（最近更新）/ likes（喜欢数）。
            page_number: 页码（≥ 1，默认 1）
            page_size: 每页大小（1 ~ 50，默认 10）
        """
        kwargs["method"] = "GET"
        kwargs["subpath"] = None
        kwargs.setdefault("params", {}).update({
            "search": search,
            "owner": owner,
            "sort": sort,
            "page_number": page_number,
            "page_size": page_size,
        })
        data = await self.request_openapi_data(**kwargs)
        collection_infos = list(map(
            CollectionInfo.from_json,
            data.get("collection_list") or []
        ))
        return collection_infos


    # ==== 创建合集 ====

    def get_collection(self, collection_slug: str) -> Collection:
        """
        构造一个 Collection 对象。
        """
        return Collection(collection_client=self, slug=collection_slug)


    async def create_collection(
        self,
        title: str,
        owner: Optional[str] = None,
        *,
        description: Optional[str] = None,
        visibility: Optional[CollectionVisibility] = None,
        theme: Optional[CollectionTheme] = None,
        **kwargs
    ) -> Collection:
        """
        创建一个新的 Collection。

        Args:
            title: Collection 标题（最长 128 字符）。
            owner: 所有者（用户名或组织名）。默认使用当前登录的用户。
            description: Collection 描述（Markdown）。
            visibility: 可见性：public / private，默认 public。
            theme: 主题标签，枚举值：Blue/Pink/Purple/Cyan。默认 Blue。
        """
        # 补全 `owner` 参数
        if not owner:
            current_user_info = await self.super_client.user.get_current_user_info()
            owner = current_user_info.username

        kwargs["method"] = "POST"
        kwargs["subpath"] = None
        kwargs.setdefault("json", {}).update({
            "title": title,
            "owner": owner,
            "description": description,
            "visibility": visibility,
            "theme": theme,
        })
        data = await self.request_openapi_data(**kwargs)
        return self.get_collection(data["slug"])


    # ==== 删除合集 ====

    async def delete_collection(self, collection_slug: str, **kwargs) -> None:
        """
        删除指定的 Collection。需具备 admin 权限的 Bearer Token。
        """
        kwargs["method"] = "DELETE"
        kwargs["subpath"] = collection_slug
        await self.request_openapi_data(**kwargs)
