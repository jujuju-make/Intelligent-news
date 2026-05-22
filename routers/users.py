
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from config.db_cong import get_db
from utils import security

from schemas.users import UserRequest
from crud import users

router = APIRouter(prefix = "/api/user", tags = ["users"])

@router.post("/register") #注册
async def register(user: UserRequest, db: AsyncSession = Depends(get_db)):
    existing_user = await (users.get_user_by_username(db, user.username))
    if existing_user:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail="用户已存在")
    new_user = await users.create_user(db, user)
    token = await (users.create_token(db, new_user.id))
    return {
        "code": 200,
        "message": "注册成功",
        "data": {
            "token": token,
            "userInfo": {
                "id": new_user.id,
                "username": new_user.username,
                "bio": new_user.bio,
                "avatar": new_user.avatar,
            }
        }
    }

@router.post("/login") #登录
async def login(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    existing_user = await (users.get_user_by_username(db, user_data.username))

    if not existing_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户未注册")

    confirm_password = security.verify_password(user_data.password, existing_user.password)

    if not confirm_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

    token = users.create_access_token(data={"sub": existing_user.username})

    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "token": token,
            "userInfo": {
                "id": existing_user.id,
                "username": existing_user.username,
                "bio": existing_user.bio,
                "avatar": existing_user.avatar,
            }
        }
    }

