"""
基础镜像数据模型。
"""

from typing import Optional

from pydantic import Field
from pydantic.dataclasses import dataclass

from ..base import BaseDataClass



@dataclass(frozen=True)
class BaseImageInfo(BaseDataClass):
    """
    基础镜像信息。
    """
    name: str = Field(
        description="镜像名称，例如 ubuntu22.04-py311-torch2.9.1-modelscope1.35.0。"
    )

    tag: Optional[str] = Field(
        description="标签，例如 latest",
        default=None
    )
