from pprint import pprint

from modelscope_api.models import MagicubeClient

from _common import logger, log_passed


async def test_magicube(magicube_client: MagicubeClient):
    """
    测试魔粒接口。
    """
    logger.info("==== Test Magicube ====")

    logger.info("查询魔粒余额")
    magicube_balance_info = await magicube_client.query_magicube_balance()
    pprint(magicube_balance_info)

    log_passed("Magicube Test")
