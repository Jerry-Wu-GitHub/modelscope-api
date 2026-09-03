"""
异常类
"""

from typing import Any, ClassVar, Dict, Optional


class BusinessException(Exception):
    """
    业务异常基类，所有业务错误都继承自这里。
    
    Attributes:
        code: 错误代码
        message: 错误消息
        details: 附加详情（可选）
    """

    # 默认消息
    DEFAULT_MESSAGE     : ClassVar[str] = "Business Error"

    # 默认错误代码
    DEFAULT_CODE        : ClassVar[str] = "ERROR"

    def __init__(
        self,
        message: Optional[str] = None,
        *,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message : str = self.DEFAULT_MESSAGE if (message is None) else message
        self.code    : str = self.DEFAULT_CODE    if (code    is None) else code
        self.details : Dict[str, Any] = details or {}

        super().__init__(self.message)


class UpstreamException(BusinessException):
    """
    上游服务端异常。
    """
    DEFAULT_MESSAGE: ClassVar[str] = "UpstreamException"
    DEFAULT_CODE: ClassVar[str] = "UPSTREAM EXCEPTION"


class ParseException(UpstreamException):
    """
    解析上游的响应失败。
    """
    DEFAULT_MESSAGE: ClassVar[str] = "ParseException"
    DEFAULT_CODE: ClassVar[str] = "PARSE EXCEPTION"


class ModelScopeException(BusinessException):
    """
    ModelScope 业务错误。
    """
    DEFAULT_MESSAGE: ClassVar[str] = "ModelScopeError"
    DEFAULT_CODE: ClassVar[str] = "MODELSCOPE ERROR"
