"""
环境变量数据模型。
"""

from enum import StrEnum
from typing import Optional

from pydantic import Field
from pydantic.dataclasses import dataclass

from .base import BaseDataClass


class EnvironmentVariableType(StrEnum):
    """
    环境变量类型。
    """
    # 明文变量
    VARIABLE = "variable"

    # 密文变量
    SECRET = "secret"


@dataclass(frozen=True)
class EnvironmentVariableInfo(BaseDataClass):
    """
    环境变量信息。
    """
    key: str = Field(
        description="变量名称。"
    )

    value: Optional[str] = Field(
        description="变量值。密文变量为 None。",
        default=None
    )
