from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat

app = FastAPI(
    title="SIM-Chat API",
    description="武汉大学信息管理学院智能问答助手后端API",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由注册
app.include_router(chat.router)

@app.get("/")
async def root():
    return {"message": "SIM-Chat API is running"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "SIM-Chat Backend"}
