import uuid
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.users import User, UserToken
from schemas.users import UserRequest
from utils import security
from jose import jwt

async def get_user_by_username(db:AsyncSession, username:str):
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def create_user(db:AsyncSession, user_data:UserRequest):
    hashed_pwd = security.get_password_hash(user_data.password)
    user = User(username=user_data.username, password=hashed_pwd)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

SECRET_KEY = "your-secret-key-sysu" # 随便写个复杂的字符串
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24小时

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire}) # 设置过期时间
    # 核心：使用 jwt.encode 生成三段式字符串
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

