# routers/ai.py
from fastapi import APIRouter, Depends, Body
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_cong import get_db
from crud.aichat import ai_chat
from models.aichat import AIChat
from utils.auth import get_current_user
from models.users import User
from crud import aichat, news

router = APIRouter(prefix="/api/ai")

@router.post("/chat")
async def chat_with_ai(
        prompt: str,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    #获取历史记录
    message_list = await aichat.get_history(db, user.id)

    #message_list = []
    retrieved_chunks = await aichat.retrieve_ai_chat(prompt, 10) #召回
    reranked_chunks = await aichat.rerank(prompt, retrieved_chunks, 6) #重排

    #获取新闻内容
    news_data = ""
    for chunk in reranked_chunks:
        news_data += chunk

    if news_data:
        rag_system_message =\
        f"""你是一位新闻助手，请根据用户的问题和下列片段回答，同时你也可以发表自己的看法。
        相关片段:{news_data}
        要求：
        1.若用户没有问关于新闻的问题，正常回答即可
        2.若用户问了关于新闻的问题，你要这样回复：
        找到以下关于{"新闻类型"}的新闻
        1: .......
        2: .......
        3: .......
        """
    else:
        rag_system_message = f"""你是一位谈吐自然大方幽默的朋友，用自然幽默的语句回答用户的问题"""

    message_list.append({"role": "system", "content": rag_system_message})
    message_list.append({"role": "user", "content": prompt})

    #获取AI回复
    ai_msg = await aichat.ai_chat(message_list)

    #添加历史记录
    new_chat = AIChat(user_id=user.id, message = prompt, response=ai_msg)
    await aichat.add_ai_chat(db, new_chat)

    return ai_msg




