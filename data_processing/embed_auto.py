"""
自动向量化入库脚本 - 使用真实MiniMax API
"""
import json
import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("开始向量化入库 - 使用 MiniMax API")
print("=" * 70)

import chromadb
import httpx

# 加载分块数据
CHUNK_FILE = "./chunks.json"
with open(CHUNK_FILE, 'r', encoding='utf-8') as f:
    chunks = json.load(f)

print(f"✅ 加载 {len(chunks)} 个数据块")

# 配置
API_KEY = os.getenv("MINIMAX_API_KEY")
COLLECTION_NAME = "sim_chat_docs"
DB_DIR = "./chroma_db"

# 清空并创建新数据库
import shutil
if os.path.exists(DB_DIR):
    shutil.rmtree(DB_DIR)
    print("✅ 已清空旧数据库")

client = chromadb.PersistentClient(path=DB_DIR)
collection = client.create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"}
)
print(f"✅ 创建新集合: {COLLECTION_NAME}")

# MiniMax Embedding API
def get_embedding(text):
    url = "https://api.minimax.chat/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": os.getenv("MINIMAX_EMBEDDING_MODEL", "embo-01"),
        "texts": [text],
        "type": "document"
    }
    
    response = httpx.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    result = response.json()
    return result["embeddings"][0]

# 向量化入库
print(f"\n开始向量化入库 (共 {len(chunks)} 个文档)...\n")

success_count = 0
error_count = 0

for i, chunk in enumerate(chunks):
    try:
        if (i + 1) % 10 == 0:
            print(f"处理进度: {i + 1}/{len(chunks)}")
        
        # 生成向量
        embedding = get_embedding(chunk["content"])
        
        # 添加到集合
        collection.add(
            ids=[chunk["id"]],
            documents=[chunk["content"]],
            metadatas=[{
                "heading": chunk["heading"],
                "source": chunk["source"]
            }],
            embeddings=[embedding]
        )
        
        success_count += 1
        
        # 避免API限流
        import time
        time.sleep(0.2)
        
    except Exception as e:
        print(f"❌ 处理块 {chunk['id']} 时出错: {e}")
        error_count += 1

print("\n" + "=" * 70)
print("入库完成！")
print("=" * 70)
print(f"✅ 成功: {success_count} 个文档")
print(f"❌ 失败: {error_count} 个文档")
print(f"📊 集合总数: {collection.count()} 个文档")
print("=" * 70)
