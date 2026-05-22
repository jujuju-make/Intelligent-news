from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_cong import get_db # 导入你之前的 get_db
from models.users import User # 导入你的用户模型
from sqlalchemy import select

# 这个工具会自动去请求头的 Authorization 字段找 "Bearer <TOKEN>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/user/login")

SECRET_KEY = "your-secret-key-sysu" # 随便写个复杂的字符串
ALGORITHM = "HS256"

#获取当前用户
async def get_current_user(
        token: str = Depends(oauth2_scheme),  # 1. 先拿 Token
        db: AsyncSession = Depends(get_db)  # 2. 拿数据库连接
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的登录状态",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 3. 解码 Token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")  # 之前登录时存入的用户名
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 4. 从数据库查出这个用户
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()

    if user is None:
        raise credentials_exception

    return user  # 5. 返回用户对象