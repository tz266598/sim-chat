"""
重新向量化入库 - 使用新的集合名称
"""
import json
import os
import sys
from dotenv import load_dotenv
import shutil

load_dotenv()

print("=" * 70)
print("开始向量化入库 - 使用 MiniMax API (新集合)")
print("=" * 70)

import chromadb
import httpx
import time

# 加载分块数据
CHUNK_FILE = "./chunks.json"
with open(CHUNK_FILE, 'r', encoding='utf-8') as f:
    chunks = json.load(f)

print(f"✅ 加载 {len(chunks)} 个数据块")

# 配置
API_KEY = os.getenv("MINIMAX_API_KEY")
COLLECTION_NAME = "sim_chat_docs_v2"  # 使用新集合名
DB_DIR = "./chroma_db_v2"

# 如果存在就删除
if os.path.exists(DB_DIR):
    time.sleep(1)  # 等待文件释放
    try:
        shutil.rmtree(DB_DIR)
        print("✅ 已清空旧数据库")
    except:
        pass

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
        "type": "db"  # 使用 "db" 而不是 "document"
    }
    
    response = httpx.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    result = response.json()
    
    # 处理不同的响应格式
    if "vectors" in result:
        return result["vectors"][0]
    elif "embeddings" in result:
        return result["embeddings"][0]
    elif "data" in result and len(result["data"]) > 0:
        return result["data"][0].get("embedding", result["data"][0].get("vector"))
    else:
        raise ValueError(f"未知的API响应格式: {list(result.keys())}")

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
print(f"💾 数据库位置: {os.path.abspath(DB_DIR)}")
print("=" * 70)
