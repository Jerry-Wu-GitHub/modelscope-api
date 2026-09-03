# ModelScope API Python SDK

[![PyPI version](https://badge.fury.io/py/modelscope-api.svg)](https://badge.fury.io/py/modelscope-api)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

一个**异步**、**类型安全**的 Python SDK，用于调用 [ModelScope 开放 API](https://modelscope.cn/docs/openapi)。

它提供了直观的对象化接口，覆盖了合集、创空间、魔粒、用户等核心模块，让您能以 Pythonic 的方式与 ModelScope 平台交互。

## ✨ 特性

- 🚀 **全异步** – 基于 `httpx.AsyncClient`，支持高并发请求。
- 🧩 **模块化设计** – 按业务领域拆分：`User`、`Magicube`、`Studio`、`Collection` 等。
- 📦 **类型安全** – 使用 Pydantic 数据模型，提供 IDE 自动补全和校验。
- 🔐 **自动认证** – 通过环境变量或构造参数传入 API Token，自动注入请求头。
- 🛠️ **开箱即用** – 支持 `.env` 配置，内置随机 UA 伪装，简化开发。

## 📦 安装

```bash
pip install modelscope-api
```

或直接从源码安装：

```bash
git clone https://github.com/Jerry-Wu-GitHub/modelscope-api.git
cd modelscope-api
pip install -e .
```

## 🚀 快速开始

### 1. 获取 API Token

访问 [ModelScope 个人设置](https://www.modelscope.cn/my/settings/token) 生成您的 `MODELSCOPE_API_TOKEN`。

### 2. 配置环境变量（推荐）

在项目根目录创建 `.env` 文件：

```env
MODELSCOPE_API_TOKEN=your_token_here
```

也可以直接在代码中传入：

```python
from modelscope_api import ModelScopeClient

client = ModelScopeClient(api_key="your_token_here")
```

### 3. 基础用法

```python
import asyncio
from modelscope_api import ModelScopeClient

async def main():
    async with ModelScopeClient() as client:
        # 获取当前用户信息
        user_info = await client.user.get_current_user_info()
        print(f"当前用户: {user_info.username}")

        # 查询魔粒余额
        balance = await client.magicube.query_magicube_balance()
        print(f"可用魔粒: {balance.available_balance}")

        # 搜索创空间
        studios = await client.studio.search_studio_infos(search="chatbot", owner="iic")
        for studio in studios:
            print(f"- {studio.display_name} ({studio.id})")

if __name__ == "__main__":
    asyncio.run(main())
```

## 📖 API 概览

SDK 的所有功能通过 `ModelScopeClient` 聚合，您可以通过其属性访问各子客户端：

| 子客户端            | 说明         | 主要方法                                                     |
| ------------------- | ------------ | ------------------------------------------------------------ |
| `client.user`       | 用户信息     | `get_current_user_info()`                                    |
| `client.magicube`   | 魔粒（积分） | `query_magicube_balance()`                                   |
| `client.studio`     | 创空间管理   | `search_studio_infos()`, `create_studio()`, `get_studio()`   |
| `client.collection` | 合集管理     | `search_collection_infos()`, `create_collection()`, `get_collection()` |

每个子客户端返回的数据均为 Pydantic 模型，可直接访问属性。

### 详细示例：操作创空间

```python
async def studio_example(client):
    # 创建创空间
    studio = await client.studio.create_studio(
        repo_name="my-awesome-space",
        display_name="我的炫酷空间",
        visibility="public",
        sdk_type="gradio",
        hardware="platform/2v-cpu-16g-mem"
    )
    print(f"创建成功: {studio.id}")

    # 部署
    runtime = await studio.deploy(timeout=30)
    print(f"部署状态: {runtime.status}")

    # 查看日志
    logs = await studio.get_logs("run", page_size=50)
    for line in logs.logs:
        print(line)

    # 添加环境变量
    await studio.variables.add("MY_KEY", "my_value")
```

### 详细示例：操作合集

```python
async def collection_example(client):
    # 创建合集
    collection = await client.collection.create_collection(
        title="我的收藏",
        visibility="private"
    )

    # 添加条目（模型）
    failed = await collection.items.add_items([
        {
            "item_type": "model",
            "item_object_id": "Qwen/Qwen3.8-27B",
            "position": 1
        }
    ])
    if failed:
        print("添加失败:", failed)

    # 获取条目列表
    items = await collection.items.get_items()
    for item in items:
        print(f"- {item.item_object_id}")

    # 删除合集
    await collection.delete()
```

## 🧪 运行测试

项目包含完整的测试用例，位于 `tests/` 目录。运行前请确保已设置有效的 `MODELSCOPE_API_TOKEN`。

> [!CAUTION]
>
> 测试用例里包含“删除创空间”，这是一个危险的操作，请确保您没有会受影响的创空间。
>
> 要实现该操作，需要使用“管理员权限”的 API Token。

## 📄 许可证

本项目使用 [MIT](LICENSE) 许可证。