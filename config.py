"""
配置
"""

import os
from typing import Optional

from dotenv import load_dotenv
from yarl import URL


# 加载 .env 文件
load_dotenv()

# 用于 ModelScope 用户进行身份验证的令牌
MODELSCOPE_API_TOKEN: Optional[str] = os.getenv("MODELSCOPE_API_TOKEN")

# OpenAPI 基础地址
MODELSCOPE_OPENAPI_VERSION: str = "v1"
MODELSCOPE_OPENAPI_BASE_URL: URL = URL(os.getenv(
    "MODELSCOPE_OPENAPI_BASE_URL",
    "https://modelscope.cn/openapi"
))
