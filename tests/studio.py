from pprint import pprint

from modelscope_api.models import StudioClient

from _common import logger, log_passed


async def test_studio(studio_client: StudioClient):
    """
    测试创空间接口。
    """
    logger.info("==== Test Studio ====")

    logger.info("查询创空间信息")
    studio_infos = await studio_client.search_studio_infos(
        search="chatbot",
        owner="iic"
    )
    pprint(studio_infos)

    logger.info("查询创空间可用的硬件信息")
    hardware_infos = await studio_client.search_available_hardwares(
        sdk_type="docker"
    )
    pprint(hardware_infos)

    logger.info("查询可用的 SDK 版本信息")
    sdk_version_infos = await studio_client.query_available_sdk_versions(
        sdk_type=None
    )
    pprint(sdk_version_infos)

    logger.info("查询可用的基础镜像信息")
    base_image_infos = await studio_client.query_available_base_images()
    pprint(base_image_infos)

    logger.info("创建创空间")
    studio = await studio_client.create_studio(
        "hello_world04",
        # owner="JerryWuModelScope",
        timeout=30
    )
    logger.info(studio)

    logger.info("操作创空间")
    studio = studio_client.get_studio("JerryWuModelScope/hello_world04")
    studio_info = await studio.get_info()
    pprint(studio_info)

    logger.info("修改展示名")
    studio_info = await studio.update_settings(display_name="你好，世界！04")
    pprint(studio_info)

    logger.info("部署创空间")
    studio_runtime_info = await studio.deploy(timeout=30)
    pprint(studio_runtime_info)

    logger.info("查看日志")
    logs_info = await studio.get_logs("run")
    pprint(logs_info)

    logger.info("停止创空间")
    studio_runtime_info = await studio.stop(timeout=30)
    pprint(studio_runtime_info)

    logger.info("添加环境变量")
    await studio.variables.add("VARIABLE_NAME", "variable value")

    logger.info("查看环境变量")
    variable_infos = await studio.variables.get_all()
    pprint(variable_infos)

    logger.info("删除环境变量")
    await studio.variables.delete("VARIABLE_NAME")

    logger.info("删除创空间")
    await studio.delete()

    logger.info("调用创空间 API")
    studio = studio_client.get_studio("JerryWuModelScope/httpbin")
    print("Base URL:", studio.base_url)
    response = await studio.request_studio_api(method="GET")
    try:
        pprint(response.json())
    except:
        print(response.text)

    log_passed("Studio Test")
