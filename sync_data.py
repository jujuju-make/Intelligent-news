import os
import asyncio
from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from config.db_cong import ASYNC_DATABASE_URL
from models.news import News
import dashscope
from dashscope import TextEmbedding
import chromadb

load_dotenv()
DATABASE_URL = ASYNC_DATABASE_URL
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

#将句子转化为向量
async def get_embedding(text:str):
    print("正在连接数据库和向量库...", flush=True)  # 加上这行，看能不能打印出来
    resp = TextEmbedding.call(
        model=TextEmbedding.Models.text_embedding_v2,
        input=text
    )
    if resp.status_code == 200:
        return resp.output['embeddings'][0]['embedding']
    else:
        raise Exception(f"Error getting embedding: {resp.status_code}")

#将数据库里的数据转化为向量
chroma_client = chromadb.PersistentClient(path = "./chroma_db")
collection = chroma_client.get_or_create_collection("news_collection")
async def sync_data():
    print("开始RAG")

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(News))
        news_list = result.scalars().all()
        count = len(news_list)
        if count == 0:
            print("数据库为空，请先塞点数据")
            return
        for item in news_list:
            existing = collection.get(ids=[str(item.id)])
            if existing and existing['ids']:
                # print(f"跳过已存在的: {item.title}")
                continue
            print(f"正在为文章《{item.title}》计算向量")
            vector = await get_embedding(item.content)
            # 4. 存入向量数据库
            # 注意：ChromaDB 默认会自动调用内置模型帮你把文本转成向量（Embedding）
            collection.add(
                ids=[str(item.id)],
                embeddings=[vector],
                documents=[item.content],
                metadatas=[{"title": item.title, "author": item.author}]
            )
            print(f"已同步: {item.title}")

    print("✅ 同步完成！")

if __name__ == "__main__":
    # 运行异步脚本
    asyncio.run(sync_data())
