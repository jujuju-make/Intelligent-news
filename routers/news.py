from fastapi import APIRouter, Depends, HTTPException
from crud import news
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_cong import get_db
#创建APIRouter实例，到时候在main.py中挂载
#prefix:路由前缀
#tags: 标签
router = APIRouter(prefix = "/api/news", tags=["news"])

@router.get("/categorys") #获取分类
async def get_categories(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    categories = await news.get_categories(db, skip, limit)
    return {
        "code": 200,
        "message": "success",
        "data": categories,
    }

@router.get("/category_lists") #获取某个分类新闻
async def get_category_list(category_id:int = 1, page:int = 1, page_size:int = 5, db: AsyncSession = Depends(get_db)):
    new = await news.get_news(db, category_id, page, page_size)
    total = await news.get_count(db, category_id)
    has_more = True if (page-1)*page_size < total else False
    return{
        "code": 200,
        "message": "success",
        "data": {
            "list":new,
            "total":total,
            "has_more":has_more,
        }
    }

@router.get("/news_detail") #获取新闻内容
async def get_news_detail(news_id: int, db: AsyncSession = Depends(get_db)):
    detail = await news.get_details(db, news_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Not Found")

    vies_res = await news.increase_views(db, news_id)
    if not vies_res:
        raise HTTPException(status_code=404, detail="Not Found")

    related_news = await news.get_recommendations(db, detail.category_id, detail.id, limit=4)
    return{
        "code": 200,
        "message": "success",
        "data": {
            "content": detail,
            "related_news": related_news
        }
    }

@router.get("/search") #寻找某个分类的新闻
async def search_news(category:str, db: AsyncSession = Depends(get_db)):
    searched_news = await news.get_news_by_category(db, category)
    if not news:
        raise HTTPException(status_code=404, detail="Not Found")
    return {
        "code": 200,
        "message": "success",
        "data": searched_news
    }

