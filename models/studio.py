"""
对单个创空间的操作。
"""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from ..utils.regex import STUDIO_ID_PATTERN
from ..data_models.environment_variable import EnvironmentVariableType
from ..data_models.studio import StudioInfo, StudioRuntimeInfo, StudioVisibility
from ..data_models.sdk import SDKType
from ..data_models.logs import LogsInfo, LogsType
from ._sub_client import SubClient
from .environment_variable_client import EnvironmentVariableClient

if TYPE_CHECKING:
    from .studio_client import StudioClient


class Studio(SubClient):
    """
    单个创空间。
    """

    def __init__(self, studio_client: StudioClient, id: str):
        self._id = id
        assert STUDIO_ID_PATTERN.fullmatch(self.id), f"Invalid studio ID: {self.id}"
        super().__init__(
            super_client=studio_client,
            prefix=self.id
        )

        # 明文变量
        self.variables = EnvironmentVariableClient(
            studio=self,
            type=EnvironmentVariableType.VARIABLE
        )

        # 密文变量
        self.secrets = EnvironmentVariableClient(
            studio=self,
            type=EnvironmentVariableType.SECRET
        )


    def __str__(self) -> str:
        return f"{type(self).__name__}<{self.id}>"


    # ==== 只读属性 ====

    @property
    def id(self) -> str:
        """
        Studio ID (owner/repo_name)
        """
        return self._id


    @property
    def owner(self) -> str:
        """
        拥有者（个人用户名或组织名）
        """
        return self._id.split("/")[0]


    @property
    def repo_name(self) -> str:
        """
        仓库名。
        """
        return self._id.split("/")[1]


    # ==== 创空间操作 ====

    async def get_info(self, **kwargs) -> StudioInfo:
        """
        获取当前 Studio 的详细信息。

        公开（public）和公开体验（protected）类型的创空间无需认证即可访问；私有（private）创空间需要认证。
        """
        kwargs["method"] = "GET"
        kwargs["subpath"] = None
        data = await self.request_openapi_data(**kwargs)
        return StudioInfo.from_json(data)


    async def update_settings(
        self,
        *,
        display_name: Optional[str] = None,
        license: Optional[str] = None,
        visibility: Optional[StudioVisibility] = None,
        description: Optional[str] = None,
        cover_image: Optional[str] = None,
        sdk_type: Optional[SDKType] = None,
        sdk_version: Optional[str] = None,
        base_image: Optional[str] = None,
        hardware: Optional[str] = None,
        **kwargs
    ) -> StudioInfo:
        """
        更新当前 Studio 的设置，传入哪个字段修改哪个字段，不传的字段不修改。

        注意：sdk_type、sdk_version、base_image、hardware 修改后需重新部署才能生效。

        Args:
            display_name: 显示名称。
                display_name.length <= 128
            license: 许可证。
            visibility: 创空间可见性。
            description: 描述。
                description.length <= 2000。
            cover_image: 封面图 URL。
            sdk_type: SDK 类型，修改后需重新部署才能生效。
            sdk_version: SDK 版本，仅对 Gradio 类型生效，默认最新版，建议选用最新版本，修改后需重新部署才能生效。
            base_image: 基础镜像，仅 Docker 类型不支持，建议选用最新版本，修改后需重新部署才能生效。
            hardware: 硬件配置，修改后需重新部署才能生效。默认为 "platform/2v-cpu-16g-mem"。
                免费资源常见格式为 platform/...、xgpu/...、amd/...；
                付费资源格式为 paid/<InstanceType>，例如 paid/ecs.gn7i-c8g1.2xlarge。
        """
        kwargs["method"] = "PATCH"
        kwargs["subpath"] = "settings"
        kwargs.setdefault("json", {}).update({
            "display_name": display_name,
            "license": license,
            "visibility": visibility,
            "description": description,
            "cover_image": cover_image,
            "sdk_type": sdk_type,
            "sdk_version": sdk_version,
            "base_image": base_image,
            "hardware": hardware,
        })
        data = await self.request_openapi_data(**kwargs)
        return StudioInfo.from_json(data)


    async def deploy(self, **kwargs) -> StudioRuntimeInfo:
        """
        部署当前的 Studio（会重新拉取代码并重建），无论当前状态是停止还是运行中均可调用。
        """
        kwargs["method"] = "POST"
        kwargs["subpath"] = "deploy"
        data = await self.request_openapi_data(**kwargs)
        return StudioRuntimeInfo.from_json(data)


    async def stop(self, **kwargs) -> StudioRuntimeInfo:
        """
        停止当前的 Studio。
        """
        kwargs["method"] = "POST"
        kwargs["subpath"] = "stop"
        data = await self.request_openapi_data(**kwargs)
        return StudioRuntimeInfo.from_json(data)


    async def get_logs(
        self,
        log_type: LogsType,
        *,
        page_num: int = 1,
        page_size: int = 100,
        keyword: Optional[str] = None,
        start_timestamp: Optional[int] = None,
        end_timestamp: Optional[int] = None,
        **kwargs
    ) -> LogsInfo:
        """
        获取当前 Studio 的运行日志。

        Args:
            log_type: 日志类型：build（构建日志）或 run（运行日志）。
            page_num: 页码，默认 1。
            page_size: 每页数量，默认 100，最大 500。
            keyword: 关键字过滤，可选。
            start_timestamp: 开始时间戳（秒），可选，自动根据 end_timestamp 计算。
            end_timestamp: 结束时间戳（秒），可选，默认当前时间。
        """
        kwargs["method"] = "GET"
        kwargs["subpath"] = f"logs/{log_type}"
        kwargs.setdefault("params", {}).update({
            "page_num": page_num,
            "page_size": page_size,
            "keyword": keyword,
            "start_timestamp": start_timestamp,
            "end_timestamp": end_timestamp,
        })
        data = await self.request_openapi_data(**kwargs)
        return LogsInfo.from_json(data)
