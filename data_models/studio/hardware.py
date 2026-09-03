"""
硬件数据模型。
"""

from typing import List, Literal, Optional

from pydantic import Field
from pydantic.dataclasses import dataclass

from ..base import BaseDataClass



@dataclass(frozen=True)
class HardwareInfo(BaseDataClass):
    """
    硬件资源配置详细信息，用于描述运行环境的具体规格、库存及成本。
    """
    name: str = Field(
        description="OpenAPI hardware 参数值。付费资源格式为 paid/<InstanceType>。"
    )

    resource_type: Literal["free", "paid"] = Field(
        description="资源类型，free 表示平台免费资源，paid 表示使用用户自己的云账号付费部署。"
    )

    instance_type: Optional[str] = Field(
        description="ECS 规格名，仅付费资源返回，例如 ecs.gn7i-c8g1.2xlarge。",
        default=None
    )

    cpu: Optional[int] = Field(
        description="CPU 核数，仅付费资源返回",
        default=None,
        ge=0
    )

    gpu: Optional[int] = Field(
        description="GPU 数量，仅付费资源返回",
        default=None,
        ge=0
    )

    memory: Optional[int] = Field(
        description="内存大小（GB），仅付费资源返回",
        default=None,
        ge=0
    )

    gpu_type: Optional[str] = Field(
        description="GPU 类型，仅付费资源返回，如 NVIDIA A100、V100 等",
        default=None
    )

    gpu_memory: Optional[int] = Field(
        description="显存（GB），仅付费资源返回",
        default=None,
        ge=0
    )

    supported_sdk_types: List[str] = Field(
        description="该硬件所支持的 SDK 类型列表，例如 ['gradio', 'streamlit']",
        default_factory=list
    )

    has_stock: Optional[bool] = Field(
        description="是否有库存，仅付费资源返回",
        default=None
    )

    stock: Optional[int] = Field(
        description="库存数量",
        default=None,
        ge=0
    )

    cost_after_discount: Optional[float] = Field(
        description="折后价格，仅付费资源返回",
        default=None,
        ge=0.0
    )

    original_cost: Optional[float] = Field(
        description="原价，仅付费资源返回",
        default=None,
        ge=0.0
    )
