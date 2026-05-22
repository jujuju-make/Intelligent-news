from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models.favorite import Favorite
from models.news import News
async def is_favorite(db:AsyncSession, user_id, news_id):
    query = select(Favorite).where(Favorite.user_id == user_id).where(Favorite.news_id == news_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def add_favorite(db:AsyncSession, user_id:int, news_id:int):
    query = select(News).where(News.id == news_id)
    result = await db.execute(query)
    if result.scalars().one() is None:
        return None

    query = select(Favorite).where(Favorite.user_id == user_id).where(Favorite.news_id == news_id)
    result = await db.execute(query)
    if result.scalars().first():
        return None


    favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite


async def remove_favorite(db: AsyncSession, user_id: int, news_id: int):
    # 直接构造删除 SQL 语句
    stmt = delete(Favorite).where(
        Favorite.user_id == user_id,
        Favorite.news_id == news_id
    )
    # 执行
    result = await db.execute(stmt)
    # 提交
    await db.commit()
    # rowcount 可以告诉你实际上删除了多少行
    if result.rowcount == 0:
        return None  # 说明本来就没这条数据，删了个寂寞
    return True