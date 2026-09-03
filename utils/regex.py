"""
正则表达式。
"""

import re
from re import Pattern

STUDIO_ID_PATTERN: Pattern = re.compile(r"[\w\-]+\/[\w\-]+")
