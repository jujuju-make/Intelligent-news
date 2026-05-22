
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_cong import get_db
from crud import favorite
from models.users import User
from utils.auth import get_current_user

router = APIRouter(
    prefix="/api/favorite",
    tags=["favorite"],
)

@router.get("/check") #是否收藏
async def check_favorite(news_id: int, user:User = Depends(get_current_user), db:AsyncSession = Depends(get_db)):
    is_favorite = await (favorite.is_favorite(db, user.id, news_id))
    return {
        "code": 200,
        "message": "success",
        "data": {
            "is_favorite": is_favorite
        }
    }

@router.post("/add") #添加收藏
async def add_favorite(news_id: int , user:User = Depends(get_current_user), db:AsyncSession = Depends(get_db)):
    added_favorite = await favorite.add_favorite(db, user.id, news_id)
    if added_favorite is None:
        raise HTTPException(status_code=404, detail="新闻不存在或已收藏过")
    return {
        "code": 200,
        "message": "收藏成功",
        "data": {
            "id": added_favorite.id,
            "user_id": added_favorite.user_id,
            "news_id": added_favorite.news_id
        }
    }
@router.delete("/remove") #移除收藏
async def delete_favorite(news_id: int, user:User = Depends(get_current_user), db:AsyncSession = Depends(get_db)):
    deleted = await favorite.remove_favorite(db, user.id, news_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="未收藏该新闻")

    return {
        "code": 200,
        "message": "取消收藏成功",
        "data": {}
    }
