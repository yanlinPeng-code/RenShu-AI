import asyncio

from backend.app.src.common.config.setting_config import settings
from openai import AsyncOpenAI,OpenAI
async def t():
    try:
        client = AsyncOpenAI(
            api_key=settings.DASHSCOPE_API_KEY,
            base_url=settings.DASHSCOPE_BASE_URL,
            timeout=10.0
        )

        # 方法1: 尝试获取模型列表
        models =await client.models.with_raw_response.list()
        if models.status_code==200:
            return True

        # model_list = [model.id for model in models.data]
    except Exception as e:
        pass


if __name__ == '__main__':
   asyncio.run(t())