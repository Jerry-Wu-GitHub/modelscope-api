from pprint import pprint

from modelscope_api.models import UserClient
from _common import logger, log_passed


async def test_user(user_client: UserClient):
    """
    测试用户接口。
    """
    logger.info("==== Test User ====")

    logger.info("获取当前用户信息")
    user_info = await user_client.get_current_user_info()
    pprint(user_info)

    log_passed("User Test")
