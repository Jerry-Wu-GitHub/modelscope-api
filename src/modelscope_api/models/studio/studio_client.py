"""
集成封装与创空间（Studios）有关的 API。
"""

from __future__ import annotations

from typing import List, Literal, Optional, TYPE_CHECKING

from ...data_models.studio import (
    BaseImageInfo,
    HardwareInfo,
    SDKType, SDKVersionInfo,
    StudioInfo, StudioVisibility,
)
from .._sub_client import SubClient
from .studio import Studio

if TYPE_CHECKING:
    from ..modelscope_client import ModelScopeClient



class StudioClient(SubClient):
    """
    集成封装与创空间（Studios）有关的 API。
    """

    def __init__(
        self,
        modelscope_client: ModelScopeClient,
        *,
        api_prefix="studio",
        openapi_prefix: str = "studios",
    ):
        self.modelscope_client = modelscope_client
        super().__init__(
            super_client=self.modelscope_client,
            api_prefix=api_prefix,
            openapi_prefix=openapi_prefix
        )


    # ==== 查询创空间信息 ====

    async def search_studio_infos(
        self,
        search: Optional[str] = None,
        owner: Optional[str] = None,
        *,
        sort: Literal["default", "last_modified", "view_num", "likes"] = "default",
        page_number: int = 1,
        page_size: int = 10,
        status: Optional[Literal["running", "all"]] = None,
        mcp_support: Optional[bool] = None,
        hardware_type: Optional[Literal["xgpu", "amd"]] = None,
        **kwargs
    ) -> List[StudioInfo]:
        """
        列出创空间信息。

        Args:
            search: 针对创空间名称、展示名称、作者（包括组织、个人）的子字符串关键词进行搜索。
                max length: 100.
            owner: 针对创空间作者（包括组织、个人）进行搜索。
            sort: 排序方式。
            page_number: 页码，限制 page_number * page_size <= 3000, page_number >= 1。
            page_size: 每页大小（1~50），限制 page_number * page_size <= 3000。
            status: 按创空间运行状态筛选。正常搜索仅支持 running；当按 owner 筛选时，默认为 all。
            mcp_support: 是否支持通过MCP使用。
            hardware_type: 根据创空间硬件类型筛选，当前仅支持筛选 xGPU。
        """
        kwargs["method"] = "GET"
        kwargs["subpath"] = None
        kwargs.setdefault("params", {}).update({
            "search": search,
            "owner": owner,
            "sort": sort,
            "page_number": page_number,
            "page_size": page_size,
            "status": status,
            "mcp_support": mcp_support,
            "hardware_type": hardware_type,
        })
        data = await self.request_openapi_data(**kwargs)
        studio_infos = list(map(
            StudioInfo.from_json,
            data.get("studios") or []
        ))
        return studio_infos


    # ==== 查询硬件信息 ====

    async def search_available_hardwares(
        self,
        *,
        sdk_type: Optional[SDKType] = None,
        studio_id: Optional[str] = None,
        **kwargs
    ) -> List[HardwareInfo]:
        """
        查询创空间可用的硬件配置列表。

        - 未登录：返回默认免费硬件
        - 已登录：返回用户可用的免费硬件和带价格的付费硬件
        - 已登录且指定创空间：免费硬件以该创空间的可用免费资源为准
        - 付费资源：使用 paid/<InstanceType> 作为创建或更新 Studio 时的 hardware 参数值

        Args:
            sdk_type: 按 supported_sdk_types 过滤硬件配置。
            studio_id: 创空间 ID（owner/repo_name），指定后返回该创空间可选的硬件。
        """
        kwargs["method"] = "GET"
        kwargs["subpath"] = "hardware"
        kwargs.setdefault("params", {}).update({
            "sdk_type": sdk_type,
            "studio": studio_id,
        })
        data = await self.request_openapi_data(**kwargs)
        hardware_infos = list(map(
            HardwareInfo.from_json,
            data.get("hardware") or []
        ))
        return hardware_infos


    # ==== 查询 SDK 版本 ====

    async def query_available_sdk_versions(
        self,
        sdk_type: SDKType,
        **kwargs
    ) -> List[SDKVersionInfo]:
        """
        查询创空间可用的 SDK 版本列表。
        仅当 sdk_type=gradio 时返回 Gradio 版本列表；其他 SDK 类型或未传 sdk_type 时返回空列表。

        Args:
            sdk_type: SDK 类型，仅 gradio 返回版本列表。
        """
        kwargs["method"] = "GET"
        kwargs["subpath"] = "sdk-versions"
        kwargs.setdefault("params", {}).update({
            "sdk_type": sdk_type,
        })
        data = await self.request_openapi_data(**kwargs)
        sdk_version_infos = list(map(
            SDKVersionInfo.from_json,
            data.get("sdk_versions") or []
        ))
        return sdk_version_infos


    # ==== 查询基础镜像 ====

    async def query_available_base_images(self, **kwargs) -> List[BaseImageInfo]:
        """
        查询创空间可用的基础镜像列表，登录与否返回结果一致。
        """
        kwargs["method"] = "GET"
        kwargs["subpath"] = "base-images"
        data = await self.request_openapi_data(**kwargs)
        base_image_infos = list(map(
            BaseImageInfo.from_json,
            data.get("base_images") or []
        ))
        return base_image_infos


    # ==== 创建创空间 ====

    def get_studio(self, studio_id: str) -> Studio:
        """
        构造一个 Studio 对象。
        """
        return Studio(studio_client=self, id=studio_id)


    async def create_studio(
        self,
        repo_name: str,
        owner: Optional[str] = None,
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
    ) -> Studio:
        """
        创建一个新的 Studio（创空间）。

        Args:
            repo_name: 仓库名称。
                repo_name.length <= 64
            owner: 所有者（用户名或组织名）（大小写敏感）。默认使用当前登录的用户。
            display_name: 显示名称。
                display_name.length <= 128
            license: 许可证，默认 apache-2.0。
            visibility: 创空间可见性，默认 public。
            description: 描述。
                description.length <= 2000。
            cover_image: 封面图 URL，为空时使用平台默认图。
            sdk_type: SDK 类型，修改后需重新部署才能生效。默认 gradio。
            sdk_version: SDK 版本，仅对 Gradio 类型生效，默认最新版，建议选用最新版本，修改后需重新部署才能生效。
                可用版本会随平台更新，请通过 self.query_available_sdk_versions("gradio") 查询当前可用的 Gradio 版本列表。
            base_image: 基础镜像，仅 Docker 类型不支持，建议选用最新版本，修改后需重新部署才能生效。
                可用值不固定，请通过 self.query_available_base_images() 查询当前可用的基础镜像列表。
            hardware: 硬件配置，修改后需重新部署才能生效。默认为 "platform/2v-cpu-16g-mem"。
                可用值不固定，请通过 self.search_available_hardwares() 查询当前可用的硬件配置列表。
                免费资源常见格式为 platform/...、xgpu/...、amd/...；
                付费资源格式为 paid/<InstanceType>，例如 paid/ecs.gn7i-c8g1.2xlarge。
        """
        # 补全 `owner` 参数
        if not owner:
            current_user_info = await self.super_client.user.get_current_user_info()
            owner = current_user_info.username

        kwargs["method"] = "POST"
        kwargs["subpath"] = None
        kwargs.setdefault("json", {}).update({
            "repo_name": repo_name,
            "owner": owner,
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
        return self.get_studio(data["id"])


    # ==== 删除创空间 ====

    async def delete_studio(self, studio_id: str, **kwargs) -> None:
        """
        删除一个创空间。

        Args:
            studio_id: owner/repo_name
        """
        kwargs["method"] = "DELETE"
        kwargs["subpath"] = studio_id
        await self.request_api_data(**kwargs)
