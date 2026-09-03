"""
各测试样例的共用部分。
"""

import logging


TEST_PROMPT_PREFIX = "[\033[34mTEST\033[0m]"
TEST_PASSED_MASSAGE = "\033[92mPASSED\033[0m"

# 创建 Logger
logger = logging.getLogger("test")
logger.setLevel(logging.DEBUG)

# 创建 Handler
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)

# 定义格式：前缀 + 时间 + 级别 + 消息
formatter = logging.Formatter(f"{TEST_PROMPT_PREFIX} %(message)s")
console.setFormatter(formatter)

# 将 Handler 添加到 Logger
logger.addHandler(console)


def log_passed(messages: str) -> None:
    """
    打印“PASSED”
    """
    logger.info(f"{messages} {TEST_PASSED_MASSAGE}")


if __name__ == '__main__':
    log_passed("test")
