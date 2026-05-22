from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.news import Category, News

async def get_categories(db: AsyncSession,skip: int = 0, limit: int = 100):
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_category_by_name(db: AsyncSession, category_name:str):
    stmt = select(Category).where(Category.name.contains(category_name))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_news(db: AsyncSession, category_id:int = 1, skip: int = 0, limit: int = 100):
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_news_by_category(db: AsyncSession, category_name:str):
    category = await get_category_by_name(db,category_name)

    if category is None:
        # 如果找不到这个分类，直接返回空列表，防止后面报错
        print(f"DEBUG: 找不到名为 {category_name} 的分类")
        return []
        # 3. 第三步：【直接通过 .id 访问属性】
        # 此时 category 是一个 AIChat 或 Category 对象，它不是 JSON，直接点 id 出来
    stmt = select(News).where(News.category_id == category.id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_count(db: AsyncSession, category_id:int = 1):
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()

async def get_details(db: AsyncSession, news_id = 1):
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def increase_views(db: AsyncSession, news_id: int = 1):
    stmt = update(News).where(News.id == news_id).values(views = News.views + 1)
    result = await db.execute(stmt)
    await db.commit()

    return result.rowcount > 0

async def get_recommendations(db: AsyncSession, category_id:int = 1, news_id = 1, limit: int = 4):
    stmt = select(News).where(News.id != news_id, News.category_id == category_id).order_by(News.views.desc(),News.publish_time.desc()).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

