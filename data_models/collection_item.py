"""
合集（Collection）数据模型。
"""

from __future__ import annotations

from enum import StrEnum
from typing import Optional

from pydantic import Field
from pydantic.dataclasses import dataclass

from .base import BaseDataClass



class CollectionItemType(StrEnum):
    """
    合集中的条目的资源类型。
    """
    MODEL = "model"
    DATASET = "dataset"
    STUDIO = "studio"
    PAPER = "paper"
    SKILL = "skill"
    MCP = "mcp"


class CollectionItemVisibility(StrEnum):
    """
    合集中的条目的可见性。
    """
    PUBLIC    = "public"    # 公开
    PROTECTED = "protected" # 仅公开体验
    PRIVATE   = "private"   # 私有


@dataclass(frozen=True)
class CollectionItemInfo(BaseDataClass):
    """
    合集中的条目信息。
    """
    item_type: CollectionItemType = Field(
        description="资源类型：model / dataset / studio / paper / skill / mcp，用于定位"
    )

    item_object_id: str = Field(
        description="资源标识，用于定位，如 damo/nlp_bert_base 或论文 ID"
    )

    note: Optional[str] = Field(
        description="用户对该条目的备注说明（Markdown）。",
        default=None
    )

    position: Optional[int] = Field(
        description="排序位置（从 1 开始）。",
        default=None,
        ge=1
    )

    created_at: Optional[str] = Field(
        description="添加时间，ISO 8601 UTC。",
        default=None
    )

    visibility: Optional[CollectionItemVisibility] = Field(
        description="可见性：public / protected / private。",
        default=None
    )

    gated: Optional[bool] = Field(
        description="visibility 为 public 时，是否需先申请并经同意后才可访问。",
        default=None
    )

    protected_mode: Optional[int] = Field(
        description=(
            "protected（仅公开体验）模式标识；"
            "用于表达条目/资源的仅公开体验语义，具体取值含义以产品后端实现为准（如 0=无、2=仅公开体验）。"
        ),
        default=None
    )

    reason: Optional[str] = Field(
        description=(
            "失败原因错误码，如 ResourceNotFound、ItemAlreadyInCollection、ItemNotInCollection、PermissionDenied。"
            "仅当添加或更新条目失败时有效。"
        ),
        default=None
    )
