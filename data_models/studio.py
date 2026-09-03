"""
创空间数据模型。
"""

from __future__ import annotations

from enum import StrEnum
from typing import List, Optional, override

from pydantic import Field
from pydantic.dataclasses import dataclass

from ..utils.regex import STUDIO_ID_PATTERN
from ..utils.typing import JsonObject
from .base import BaseDataClass
from .sdk import SDKType


class StudioRuntimeStatus(StrEnum):
    """
    创空间运行状态。
    """
    INITIALIZED = "Initialized"
    BUILDING = "Building"
    BUILDFAILED = "BuildFailed"
    DEPLOYING = "Deploying"
    DEPLOYFAILED = "DeployFailed"
    RUNNING = "Running"
    STOPPING = "Stopping"
    STOPPED = "Stopped"
    DUPLICATING = "Duplicating"
    SLEEPING = "Sleeping"


@dataclass(frozen=True)
class StudioActiveConfig(BaseDataClass):
    """当前生效的运行时配置"""
    hardware: Optional[str] = Field(
        description="硬件配置，修改后需重新部署才能生效。",
        default=None
    )

    base_image: Optional[str] = Field(
        description="基础镜像，仅 Docker 类型不支持，建议选用最新版本，修改后需重新部署才能生效。",
        default=None
    )

    sdk_type: Optional[SDKType] = Field(
        description="SDK 类型，修改后需重新部署才能生效。",
        default=None
    )

    sdk_version: Optional[str] = Field(
        description="SDK 版本（仅 gradio 类型返回）",
        default=None
    )


@dataclass(frozen=True)
class StudioRuntimeInfo(BaseDataClass):
    """创空间运行时状态信息"""
    status: StudioRuntimeStatus = Field(
        description="运行状态"
    )

    active_config: StudioActiveConfig = Field(
        description="当前生效的配置详情",
        default_factory=StudioActiveConfig
    )

    created_at: Optional[str] = Field(
        description="部署时间（ISO 8601 格式）",
        default=None
    )

    error_message: Optional[str] = Field(
        description="失败信息（仅在错误状态时返回）",
        default=None
    )


class StudioVisibility(StrEnum):
    """
    创空间可见性。
    """
    # 代码和体验都公开
    PUBLIC = "public"

    # 体验公开，代码仓库不可见
    PROTECTED = "protected"

    # 都不公开
    PRIVATE = "private"


@dataclass(frozen=True)
class StudioInfo(BaseDataClass):
    """
    描述魔搭社区创空间（Studio）的完整信息模型。

    该模型用于表示创空间的元数据、配置、运行时状态等所有公开属性，
    适用于 API 响应或内部数据传递。
    """
    id: str = Field(
        description="Studio ID (owner/repo_name)",
        pattern=STUDIO_ID_PATTERN.pattern
    )

    repo_name: str = Field(
        description="仓库名称，是创空间的唯一标识。"
    )

    display_name: Optional[str] = Field(
        description="中文或友好的显示名称，默认将使用英文名称。",
        default=None
    )

    owner: str = Field(
        description="所有者（包括组织、个人）"
    )

    description: Optional[str] = Field(
        description="描述",
        default=None
    )

    cover_image: Optional[str] = Field(
        description="封面图片的 URL 地址",
        default=None
    )

    created_at: Optional[str] = Field(
        description="部署时间（ISO 8601 格式）",
        default=None
    )

    likes: int = Field(
        description="获赞数量",
        ge=0
    )

    view_count: int = Field(
        description="访问量",
        ge=0
    )

    tags: List[str] = Field(
        description="关联的标签列表，用于分类和搜索",
        default_factory=list
    )

    visibility: StudioVisibility = Field(
        description="创空间可见性"
    )

    last_modified: Optional[str] = Field(
        description="最后修改时间（ISO 8601 格式）",
        default=None
    )

    sdk_type: Optional[SDKType] = Field(
        description="使用的 SDK 类型，如 gradio、streamlit",
        default=None
    )

    sdk_version: Optional[str] = Field(
        description="SDK 版本，仅对 Gradio 类型生效",
        default=None
    )

    hardware: Optional[str] = Field(
        description="硬件配置，修改后需重新部署才能生效。",
        default=None
    )

    base_image: Optional[str] = Field(
        description="基础镜像，仅 Docker 类型不支持。",
        default=None
    )

    license: Optional[str] = Field(
        description="许可证",
        default=None
    )

    host: str = Field(
        description="API 访问地址（base url）"
    )

    mcp_support: bool = Field(
        description="是否支持 MCP"
    )

    runtime: StudioRuntimeInfo = Field(
        description="运行时状态与配置的嵌套信息"
    )


    @override
    @classmethod
    def from_json(cls, data: JsonObject) -> StudioInfo:
        if "created_at" not in data:
            data["created_at"] = data.get("runtime", {}).get("created_at")
        return super().from_json(data)
