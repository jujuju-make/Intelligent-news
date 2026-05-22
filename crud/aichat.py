import chromadb
import os

from dashscope import TextReRank
from openai import AsyncOpenAI
import json
from openai.types.chat.chat_completion import ChatCompletion
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv
from models.aichat import AIChat
from sync_data import get_embedding

load_dotenv()
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com" # 使用国内镜像
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")
# 使用这个绝对路径连接
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name="news_collection")

async def ai_chat(message):
    api_key = os.getenv("DASHSCOPE_API_KEY")
    # 后端去调大模型接口（比如 DeepSeek, OpenAI）
    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    # API Key 存在后端的环境变量里，不给前端看

    response = await client.chat.completions.create(
        model = "qwen-plus",
        messages = message,
        #stream = True,
        timeout = 600.0
    )

    ai_msg = response.choices[0].message.content
    return ai_msg

    """"
    #full_content = ""
    async for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            #full_content += content
            yield content
    """
    #return full_content
    """""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "qwen-plus",
                "messages": message
            }
        )
    """""
    #ai_msg = response.choices[0].message.content
    #return ai_msg

async def add_ai_chat(db:AsyncSession,new_chat:AIChat):
    db.add(new_chat)
    await db.commit()

async def get_history(db:AsyncSession, user_id:int):
    stmt = select(AIChat).where(AIChat.user_id == user_id).order_by(desc(AIChat.id)).limit(6)
    result = await db.execute(stmt)
    history_list:list = result.scalars().all()
    history_list.reverse()

    messages:list = [{"role": "system", "content": "你是一个新闻助手，请记住之前的对话内容。"}]
    for chat in history_list:
        messages.append({"role": "user", "content": chat.message})
        messages.append({"role": "assistant", "content": chat.response})

    return messages

async def get_intent(prompt:str):
    api_key = os.getenv("DASHSCOPE_API_KEY")
    # 后端去调大模型接口（比如 DeepSeek, OpenAI）
    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    system_prompt = """
        你是一个意图识别专家。根据用户输入，判断他想做什么。
        你必须只返回 JSON 格式，不要有任何多余的废话。
        格式：{"action": "search_id" | "search_name" | "chat", "value": "提取到的关键词或ID"}

        例子：
        1. "查看ID为5的新闻" -> {"action": "search_id", "value": "5"}
        2. "找找关于科技的消息" -> {"action": "search_name", "value": "科技"}
        3. "你好啊" -> {"action": "chat", "value": ""}
        """

    response = await client.chat.completions.create(
        model="qwen-turbo",  # 意图识别用最便宜最快的 turbo 即可
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        # 建议开启 json_object 模式（如果模型支持）或者强制要求返回
    )

    raw_content = response.choices[0].message.content
    clean_content = raw_content.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(clean_content)
    except:
        return {"action": "chat", "value": ""}

async def retrieve_ai_chat(prompt: str, top_k: int):  #将问题变成向量获取相关向量
    print(f"正在转换提问向量: {prompt}...")
    prompt_embedding = await get_embedding(prompt)

    print(f"正在向量库中检索前 {top_k} 条匹配项...")
    result = collection.query(
        query_embeddings=[prompt_embedding],
        n_results=top_k
    )

    # 计科生 Debug 秘籍：打印原始结果
    print(f"ChromaDB 返回的原始 IDs: {result['ids']}")

    if not result['documents'] or not result['documents'][0]:
        print("⚠️ 搜索结果为空！请检查库中是否有数据。")
        return []

    return result['documents'][0]

async def rerank(prompt:str, retrieved_chunks:list, top_k:int):
    resp = TextReRank.call(
        model = TextReRank.Models.gte_rerank,
        query = prompt,
        documents = retrieved_chunks,
        top_n = top_k,
        api_key = os.getenv("DASHSCOPE_API_KEY")
    )

    if resp.status_code == 200:
        reranked_results = [retrieved_chunks[item.index] for item in resp.output.results]
        return reranked_results
    else:
        print(f"Rerank失败: {resp.message}")
        return retrieved_chunks[:top_k]



async def main():
    # 1. 定义一个异步的主函数
    prompt = "告诉我关于国家的新闻"
    # 2. 在这里使用 await，支票才会兑现成真正的结果
    retrieved_chunks = await retrieve_ai_chat(prompt, top_k=6)
    print("召回新闻：")
    for i, chunk in enumerate(retrieved_chunks):
        print(f"[{i}] {chunk}\n")

    reranked_chunks = await rerank(prompt, retrieved_chunks, top_k=3)
    print("重排新闻：")
    for i,chunk in enumerate(reranked_chunks):
        print(f"[{i}] {chunk}\n")


if __name__ == "__main__":
    # 3. 使用 asyncio.run 来启动整个异步流程
    import asyncio

    asyncio.run(main())
