"""
魔粒数据模型。
"""

from pydantic import Field
from pydantic.dataclasses import dataclass

from ..utils.typing import Real
from .base import BaseDataClass


@dataclass(frozen=True)
class MagicubeBalanceInfo(BaseDataClass):
    """
    魔粒余额信息。
    """
    total_balance: Real = Field(
        description="总额度（可用额度 + 预扣额度）",
        ge=0
    )

    available_balance: Real = Field(
        description="可用额度",
        ge=0
    )

    frozen_amount: Real = Field(
        description="预扣额度（进行中任务未返回结果时预扣减）",
        ge=0
    )
