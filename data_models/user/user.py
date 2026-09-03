"""
用户数据模型。
"""

from typing import Optional

from pydantic import Field
from pydantic.dataclasses import dataclass

from ..base import BaseDataClass



@dataclass(frozen=True)
class UserInfo(BaseDataClass):
    """
    用户信息
    """
    username: str = Field(
        description="用户在平台上的唯一用户名。"
    )

    nickname: Optional[str] = Field(
        description="用户自定义的昵称。",
        default=None
    )

    description: Optional[str] = Field(
        description="个人介绍。文档节点 JSON 结构。",
        default=None
    )

    email: Optional[str] = Field(
        description="邮箱。",
        default=None
    )

    avatar_url: Optional[str] = Field(
        description="头像的 URL。",
        default=None
    )


    def __post_init__(self) -> None:
        # nickname 为空时，使用 username 填充
        if self.nickname is None:
            object.__setattr__(self, "nickname", self.username)
