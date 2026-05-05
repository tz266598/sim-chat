from fastapi import APIRouter
from pydantic import BaseModel
from app.services.retrieval import retrieve_documents, generate_answer

router = APIRouter(prefix="/api", tags=["chat"])

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    sources: list

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """聊天接口"""
    # 检索相关文档
    documents = retrieve_documents(request.question)
    
    # 构建上下文
    context = "\n\n".join([doc["content"] for doc in documents])
    
    # 生成回答
    answer = generate_answer(request.question, context)
    
    # 构建来源信息
    sources = [
        {
            "content": doc["content"][:200] + "...",
            "metadata": doc["metadata"],
            "relevance": 1 - doc["distance"]
        }
        for doc in documents
    ]
    
    return ChatResponse(answer=answer, sources=sources)

@router.get("/collections")
def get_collections():
    """获取集合信息"""
    from app.services.vectorstore import vector_store
    return vector_store.get_collections_info()
