from app.core.minimax import minimax_client
from app.services.vectorstore import vector_store

def retrieve_documents(query: str, top_k: int = 5) -> list:
    """检索相关文档 - 使用简单关键词匹配"""
    try:
        # 尝试使用向量检索
        query_embedding = minimax_client.get_embedding(query)
        results = vector_store.query(query_embedding, n_results=top_k)
        
        documents = []
        if results["documents"] and results["documents"][0]:
            for i, (doc, metadata, distance) in enumerate(
                zip(results["documents"][0], results["metadatas"][0], results["distances"][0])
            ):
                documents.append({
                    "content": doc,
                    "metadata": metadata,
                    "distance": distance
                })
        return documents
    except Exception as e:
        print(f"向量检索失败: {e}，使用关键词匹配")
        # 回退到简单关键词匹配
        return keyword_search(query, top_k)

def keyword_search(query: str, top_k: int = 5) -> list:
    """简单的关键词搜索"""
    # 获取所有文档
    results = vector_store.collection.get(
        include=["documents", "metadatas"]
    )
    
    documents = []
    query_lower = query.lower()
    
    for doc, metadata in zip(results['documents'], results['metadatas']):
        # 简单的相关度评分
        score = 0
        doc_lower = doc.lower()
        
        # 检查是否包含查询词
        if query_lower in doc_lower:
            score += 10
        else:
            # 检查关键词
            keywords = query_lower.split()
            for keyword in keywords:
                if len(keyword) > 1 and keyword in doc_lower:
                    score += 1
        
        if score > 0:
            documents.append({
                "content": doc,
                "metadata": metadata,
                "distance": 1.0 / (1.0 + score)  # 转换为距离格式
            })
    
    # 按相关性排序
    documents.sort(key=lambda x: x["distance"])
    return documents[:top_k]

def generate_answer(query: str, context: str) -> str:
    """生成回答"""
    answer = minimax_client.get_completion(query, context)
    return answer
