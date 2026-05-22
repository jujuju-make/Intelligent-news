from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from urllib.parse import quote_plus

# 1. 你的原始密码
raw_password = "Ilikeyou1031@"

# 2. 对密码进行转义（它会把 @ 变成 %40）
safe_password = quote_plus(raw_password)

# 3. 拼接连接字符串
ASYNC_DATABASE_URL = f"mysql+aiomysql://root:{safe_password}@localhost:3306/news_app"

#创建异步引擎
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,
    pool_size=10,
    max_overflow=20
)

#创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession
)

#依赖项，用于获取数据库会话
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()