"""
对单个创空间的操作。
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import BinaryIO, List, Optional, TYPE_CHECKING

import aiofiles
import httpx
from yarl import URL

from ...config import STUDIO_API_DOMAIN
from ...utils.regex import STUDIO_ID_PATTERN
from ...data_models.studio import (
    StudioInfo, StudioRuntimeInfo, StudioVisibility,
    EnvironmentVariableType,
    SDKType,
    LogsInfo, LogsType
)
from .._sub_client import SubClient
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
            openapi_prefix=self.id
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


    async def delete(self) -> None:
        """
        删除当前创空间。
        """
        await self.super_client.delete_studio(self.id)


    # ==== 访问创空间 API ====

    @property
    def base_url(self) -> URL:
        """
        创空间的 API 调用根域名，服务的基础访问入口，不带接口路径。
        """
        host = (
            "studio-"
            f"{self.owner.lower()}-"
            f"{self.repo_name.lower()}."
            f"{STUDIO_API_DOMAIN}"
        ).replace('_', '-')
        return URL.build(scheme="https", host=host)


    async def request_studio_api(self, subpath: Optional[str] = None, **kwargs) -> httpx.Response:
        """
        调用当前创空间的 API。
        """
        if subpath is None:
            api_url = self.base_url
        else:
            api_url = self.base_url / subpath
        kwargs["url"] = str(api_url)
        return await self.super_client.modelscope_client.request(**kwargs)


    # ==== 操作创空间文件 ====

    async def upload_file(
        self,
        path_or_fileobj: str | Path | bytes | BinaryIO,
        path_in_repo: str,
        *,
        commit_message: str | None = None,
        commit_description: str | None = None,
        revision: str | None = None,
        buffer_size_mb: int = 16,
        disable_tqdm: bool = False,
    ) -> dict:
        """Upload a single file to a repository.

        LFS files upload/reuse their blob first, then commit an LFS pointer.
        Normal files are committed directly with inline base64 content.
        LFS mode is determined by file suffix and size threshold.

        Parameters
        ----------
        path_or_fileobj : str, Path, bytes or BinaryIO
            Local path, raw bytes, or a binary file-like object.
        path_in_repo : str
            Destination path inside the repository.
        commit_message : str, optional
            Commit message. Defaults to ``"Upload file"``.
        commit_description : str, optional
            Extended commit description.
        revision : str, optional
            Branch to commit on. Defaults to ``"master"``.
        buffer_size_mb : int, optional
            Buffer size in MiB for reading file data. Default 16.
        disable_tqdm : bool, optional
            Disable progress bar. Default False.

        Returns
        -------
        dict
            Commit info from the server.

        Raises
        ------
        AuthenticationError
            When the token is missing or invalid.
        NotExistError
            When the target repository does not exist.

        Examples
        --------
        >>> studio.upload_file(
        ...     path_or_fileobj="./pytorch_model.bin",
        ...     path_in_repo="pytorch_model.bin",
        ...     commit_message="Add fine-tuned weights",
        ... )
        """
        return await asyncio.to_thread(
            self.hub_api.upload_file,
            repo_id=self.id,
            repo_type="studio",
            path_or_fileobj=path_or_fileobj,
            path_in_repo=path_in_repo,
            commit_message=commit_message,
            commit_description=commit_description,
            revision=revision,
            buffer_size_mb=buffer_size_mb,
            disable_tqdm=disable_tqdm,
        )


    @staticmethod
    async def _load_ignore_file(path: str | Path, encoding: str = "utf-8") -> List[str]:
        """
        异步读取 ignore 文件中的 ignore_patterns。

        如果文件不存在，不会报错。
        """
        patterns = []
        try:
            async with aiofiles.open(path, mode="r", encoding=encoding) as file:
                # 异步读取所有行
                async for line in file:
                    line = line.strip()
                    # 跳过空行和注释行
                    if line and not line.startswith("#"):
                        patterns.append(line)
        except FileNotFoundError:
            pass
        return patterns


    async def upload_folder(
        self,
        folder_path: str | Path,
        *,
        path_in_repo: str = "",
        commit_message: str | None = None,
        commit_description: str | None = None,
        revision: str | None = None,
        allow_patterns: List[str] | None = None,
        ignore_patterns: List[str] | None = None,
        max_workers: int | None = None,
        use_cache: bool | None = None,
        disable_tqdm: bool = False,
        sync_remote_repo: bool = False,
        load_ignore: Optional[List[str]] = None,
    ) -> dict | List[dict] | None:
        """Upload an entire folder to a repository with resumable support.

        Files are walked recursively from ``folder_path`` and uploaded in
        parallel with adaptive batching, per-file retry, and ReAct progressive
        retry fallback.

        Parameters
        ----------
        folder_path : str or Path
            Local directory whose contents will be uploaded.
        path_in_repo : str, optional
            Destination prefix inside the repository. Defaults to the repo root.
        commit_message : str, optional
            Commit message. Defaults to ``"Upload folder"``.
        commit_description : str, optional
            Extended commit description.
        revision : str, optional
            Branch to commit on. Defaults to ``"master"``.
        allow_patterns : list of str, optional
            If given, only files matching at least one pattern are uploaded.
        ignore_patterns : list of str, optional
            Files matching any pattern are skipped.
        max_workers : int, optional
            Concurrency for parallel uploads. Defaults to adaptive.
        use_cache : bool, optional
            Use resumable upload caching. When omitted, read
            ``MODELSCOPE_UPLOAD_CACHE_ENABLED``. Explicit ``True`` or ``False``
            overrides the environment configuration.
        disable_tqdm : bool, optional
            Disable progress bars. Default False.
        sync_remote_repo : bool, optional
            If True, delete remote files that are not present locally after
            a successful upload (sync semantics). Default False.
        load_ignore: list[str], optional
            Each element is a relative path to ``folder_path``.
            The contents of this files will be imported and added to ``ignore_matterns``.

        Returns
        -------
        None
            If all files were already committed (nothing to do).
        dict
            If only one batch was committed.
        list of dict
            If multiple batches were committed.

        Examples
        --------
        >>> studio.upload_folder(
        ...     folder_path="./checkpoint-1000",
        ...     ignore_patterns=["*.optim", "events.out.*"],
        ...     max_workers=8,
        ... )
        """
        # Fill `ignore_patterns`
        if load_ignore:
            folder_path = Path(folder_path)
            ignore_patterns = ignore_patterns or []
            tasks = []
            for ignore_file_relative_path in load_ignore:
                ignore_file_path = folder_path / ignore_file_relative_path
                tasks.append(self._load_ignore_file(ignore_file_path))
            for patterns in await asyncio.gather(*tasks):
                ignore_patterns.extend(patterns)

        # Request
        return await asyncio.to_thread(
            self.hub_api.upload_folder,
            repo_id=self.id,
            repo_type="studio",
            folder_path=folder_path,
            path_in_repo=path_in_repo,
            commit_message=commit_message,
            commit_description=commit_description,
            revision=revision,
            allow_patterns=allow_patterns,
            ignore_patterns=ignore_patterns,
            max_workers=max_workers,
            use_cache=use_cache,
            disable_tqdm=disable_tqdm,
            sync_remote_repo=sync_remote_repo,
        )
