"""
正则表达式。
"""

import re
from re import Pattern

# 创空间的 ID
STUDIO_ID_PATTERN: Pattern = re.compile(r"[\w\-]+\/[\w\-]+")

# 合集的唯一标识
COLLECTION_SLUG_PATTERN: Pattern = re.compile(r"[\w\-]+\/[\w\-]+")
