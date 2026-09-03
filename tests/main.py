import asyncio

from dotenv import load_dotenv
load_dotenv()
from modelscope_api.models import ModelScopeClient

from collection import test_collection
from magicube import test_magicube
from studio import test_studio
from user import test_user



async def test():
    """
    测试全部
    """
    async with ModelScopeClient() as client:
        await test_user(client.user)
        await test_magicube(client.magicube)
        await test_studio(client.studio)
        await test_collection(client.collection)


if __name__ == '__main__':
    asyncio.run(test())
