"""
SDK 版本数据模型。
"""

from enum import StrEnum
from typing import Optional

from pydantic import Field
from pydantic.dataclasses import dataclass

from ..base import BaseDataClass



class SDKType(StrEnum):
    """
    创空间 SDK 类型。
    """
    GRADIO = "gradio"
    STREAMLIT = "streamlit"
    DOCKER = "docker"
    STATIC = "static"


@dataclass(frozen=True)
class SDKVersionInfo(BaseDataClass):
    """
    SDK 版本信息。
    """
    sdk_type: SDKType = Field(
        description="SDK 类型"
    )

    tag: Optional[str] = Field(
        description="版本标签",
        default=None
    )

    version: str = Field(
        description="SDK 版本"
    )
