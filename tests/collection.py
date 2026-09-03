from pprint import pprint

from modelscope_api.models import CollectionClient

from _common import logger, log_passed


async def test_collection(collection_client: CollectionClient):
    """
    测试合集接口。
    """
    logger.info("==== Test Collection ====")

    logger.info("查询合集信息")
    collection_infos = await collection_client.search_collection_infos("标题")
    pprint(collection_infos)

    logger.info("创建合集")
    collection = await collection_client.create_collection(
        "test",
        # owner="JerryWuModelScope",
        visibility="private"
    )
    logger.info(collection)

    logger.info("查看合集信息")
    # collection = collection_client.get_collection("JerryWuModelScope/test")
    collection_info = await collection.get_info()
    pprint(collection_info)

    logger.info("更新合集")
    collection_info = await collection.update(title="test01")
    pprint(collection_info)

    logger.info("删除合集")
    await collection.delete()
    logger.info("成功")

    logger.info("查看合集内的条目")
    collection = collection_client.get_collection("JerryWuModelScope/ai_server")
    collection_item_infos = await collection.items.get_item_infos()
    pprint(collection_item_infos)

    logger.info("向合集内添加条目")
    failed_item_infos = await collection.items.add_items([
        {
            "item_type": "model",
            "item_object_id": "Qwen/Qwen3.8-27B",
            "position": 1,
        }
    ])
    pprint(failed_item_infos)

    logger.info("获取合集内的条目对象")
    collection_items = await collection.items.get_items()
    pprint(collection_items)

    logger.info("更新第一个条目的描述")
    collection_item = collection_items[0]
    await collection_item.update(note="AI")

    logger.info("从合集中删除第一个条目")
    await collection_item.delete()

    log_passed("Collection Test")
