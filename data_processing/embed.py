"""
向量化入库脚本
调用MiniMax API生成Embedding向量并存入ChromaDB
"""
import json
import os
import httpx
import chromadb
from typing import List
from dotenv import load_dotenv

load_dotenv()

class EmbeddingService:
    def __init__(self):
        self.api_key = os.getenv("MINIMAX_API_KEY")
        self.group_id = os.getenv("MINIMAX_GROUP_ID")
        self.model = os.getenv("MINIMAX_EMBEDDING_MODEL", "embo-01")
        self.base_url = "https://api.minimax.chat/v1"
    
    def get_embedding(self, text: str) -> List[float]:
        """获取文本向量"""
        url = f"{self.base_url}/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "texts": [text],
            "type": "document"
        }
        
        response = httpx.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result["embeddings"][0]

def load_chunks(chunk_file: str) -> List[dict]:
    """加载分块数据"""
    with open(chunk_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def store_to_chromadb(chunks: List[dict], collection_name: str = "sim_chat_docs"):
    """将数据存入ChromaDB"""
    # 连接ChromaDB
    client = chromadb.HttpClient(
        host=os.getenv("CHROMA_HOST", "localhost"),
        port=int(os.getenv("CHROMA_PORT", "8000"))
    )
    
    # 创建或获取集合
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    
    # 准备数据
    ids = []
    documents = []
    metadatas = []
    
    print("生成向量并入库...")
    embedding_service = EmbeddingService()
    
    for i, chunk in enumerate(chunks):
        if i % 10 == 0:
            print(f"处理进度: {i}/{len(chunks)}")
        
        try:
            # 生成向量
            embedding = embedding_service.get_embedding(chunk["content"])
            
            ids.append(chunk["id"])
            documents.append(chunk["content"])
            metadatas.append({
                "heading": chunk["heading"],
                "source": chunk["source"]
            })
            
            # 添加向量（带embedding参数）
            collection.add(
                ids=[chunk["id"]],
                documents=[chunk["content"]],
                metadatas=[metadatas[-1]],
                embeddings=[embedding]
            )
        except Exception as e:
            print(f"处理块 {chunk['id']} 时出错: {e}")
            continue
    
    print(f"入库完成！共处理 {len(ids)} 个文档")

if __name__ == "__main__":
    CHUNK_FILE = "./chunks.json"
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "sim_chat_docs")
    
    if not os.path.exists(CHUNK_FILE):
        print(f"请先运行 chunk.py 生成分块数据")
    else:
        chunks = load_chunks(CHUNK_FILE)
        store_to_chromadb(chunks, COLLECTION_NAME)
