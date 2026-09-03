"""
数据类基类。
"""

from __future__ import annotations

from ..utils.typing import JsonObject


class BaseDataClass:
    """
    数据模型基类，提供从 JSON 构造的通用方法。
    """

    @classmethod
    def from_json(cls, data: JsonObject) -> BaseDataClass:
        """
        从 JSON 对象构造。
        """
        return cls(**data)
