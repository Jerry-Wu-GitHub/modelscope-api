"""
日志数据模型。
"""

from enum import StrEnum
from typing import List

from pydantic import Field
from pydantic.dataclasses import dataclass

from ..base import BaseDataClass



class LogsType(StrEnum):
    """
    日志类型。
    """
    BUILD = "build"
    RUN = "run"


@dataclass(frozen=True)
class LogsInfo(BaseDataClass):
    """
    日志信息。
    """
    logs: List[str] = Field(
        description="日志内容，每行为一条日志。",
        default_factory=list
    )

    page_num: int = Field(
        description="页码。",
        default=1,
        ge=1
    )

    page_size: int = Field(
        description="每页的日志条数。",
        default=100,
        ge=1,
        le=500
    )

    total_count: int = Field(
        description="日志总数。",
        ge=0
    )

    total_page_num: int = Field(
        description="页面总数。",
        ge=0
    )
