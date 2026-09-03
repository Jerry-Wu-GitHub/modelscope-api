"""
自定义数据类型。
"""

from typing import Dict, Union
from pydantic import JsonValue

# JSON 结构的字典对象
JsonObject = Dict[str, JsonValue]

# 实数
Real = Union[int, float]
