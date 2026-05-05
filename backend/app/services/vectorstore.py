import chromadb
from pathlib import Path
from app.core.config import settings

class VectorStore:
    def __init__(self):
        # 使用本地持久化数据库
        db_path = Path(__file__).parent.parent.parent.parent / "data_processing" / "chroma_db"
        self.client = chromadb.PersistentClient(path=str(db_path))
        self.collection = self.client.get_collection(
            name=settings.COLLECTION_NAME
        )
    
    def add_documents(self, ids: list, documents: list, metadatas: list = None):
        """添加文档到向量库"""
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
    
    def query(self, query_embedding: list, n_results: int = None) -> dict:
        """查询相似文档"""
        if n_results is None:
            n_results = settings.TOP_K
            
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
    
    def get_collections_info(self) -> dict:
        """获取集合信息"""
        return {
            "name": self.collection.name,
            "count": self.collection.count()
        }

vector_store = VectorStore()
