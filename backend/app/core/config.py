import os
from pathlib import Path
from dotenv import load_dotenv

# 加载项目根目录的 .env 文件
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    MINIMAX_API_KEY: str = os.getenv("MINIMAX_API_KEY", "")
    MINIMAX_GROUP_ID: str = os.getenv("MINIMAX_GROUP_ID", "")
    MINIMAX_EMBEDDING_MODEL: str = os.getenv("MINIMAX_EMBEDDING_MODEL", "embo-01")
    MINIMAX_LLM_MODEL: str = os.getenv("MINIMAX_LLM_MODEL", "Text-01")
    CHROMA_HOST: str = os.getenv("CHROMA_HOST", "localhost")
    CHROMA_PORT: int = int(os.getenv("CHROMA_PORT", "8000"))
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "sim_chat_docs")
    TOP_K: int = int(os.getenv("TOP_K", "5"))
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "../data_processing/chroma_db")

settings = Settings()
