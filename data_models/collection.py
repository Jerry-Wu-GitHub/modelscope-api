"""
合集（Collection）数据模型。
"""

from __future__ import annotations

from enum import StrEnum
from typing import List, Optional

from pydantic import Field
from pydantic.dataclasses import dataclass

from ..utils.regex import COLLECTION_SLUG_PATTERN
from .base import BaseDataClass
from .collection_item import CollectionItemInfo



class CollectionVisibility(StrEnum):
    """
    合集可见性。
    """
    PUBLIC  = "public"  # 公开
    PRIVATE = "private" # 私有


class CollectionTheme(StrEnum):
    """
    合集的主题色。
    """
    BLUE = "Blue"
    PINK = "Pink"
    PURPLE = "Purple"
    CYAN = "Cyan"


@dataclass(frozen=True)
class CollectionInfo(BaseDataClass):
    """
    合集（collection）信息。
    """

    slug: str = Field(
        description=(
            "Collection 唯一标识，格式 {owner}/{slug}。"
            "新建为 {owner}/{title_slug}；历史为 {owner}/{title_slug}-{short_id}"
        ),
        pattern=COLLECTION_SLUG_PATTERN.pattern
    )

    title: Optional[str] = Field(
        description="合集标题。",
        default=None
    )

    description: Optional[str] = Field(
        description="合集简介描述（Markdown）。",
        default=None
    )

    owner: str = Field(
        description="合集的所有者（用户名或组织名）。"
    )

    visibility: CollectionVisibility = Field(
        description="可见性：public（公开）/ private（私有）。"
    )

    theme: CollectionTheme = Field(
        description="合集页面主题样式标识。"
    )

    item_count: int = Field(
        description="喜欢数。",
        ge=0
    )

    likes: int = Field(
        description="合集点赞数",
        ge=0
    )

    view_count: int = Field(
        description="浏览量。",
        ge=0
    )

    items: list[CollectionItemInfo] = Field(
        description="合集内部条目列表，数组元素为合集子项对象，为空时返回空列表",
        default_factory=list
    )

    created_at: Optional[str] = Field(
        description="合集创建时间，ISO‑8601格式UTC时间字符串。",
        default=None
    )

    updated_at: Optional[str] = Field(
        description="合集最后更新时间，ISO‑8601格式UTC时间字符串。",
        default=None
    )

    url: str = Field(
        description="合集网页访问完整URL地址。"
    )

    install_command: List[str] = Field(
        description="当 items 包含 skill 时，返回下载命令数组。",
        default_factory=list
    )
