from fastapi import  FastAPI
from routers import  news, users, favorite, ai
from fastapi.staticfiles import StaticFiles
app = FastAPI()

@app.get("/")
async def root():
    return {"root has been created!"}

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(news.router) #挂载路由
app.include_router(users.router)
app.include_router(favorite.router)
app.include_router(ai.router)
