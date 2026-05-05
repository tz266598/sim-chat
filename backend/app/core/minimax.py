import httpx
from app.core.config import settings

class MiniMaxClient:
    def __init__(self):
        self.api_key = settings.MINIMAX_API_KEY
        self.group_id = settings.MINIMAX_GROUP_ID
        self.base_url = "https://api.minimax.chat/v1"
        self.embedding_model = settings.MINIMAX_EMBEDDING_MODEL
        self.llm_model = settings.MINIMAX_LLM_MODEL
    
    def get_embedding(self, text: str) -> list:
        """获取文本的向量表示"""
        url = f"{self.base_url}/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.embedding_model,
            "texts": [text],
            "type": "db"  # 使用 "db" 类型
        }
        
        response = httpx.post(url, json=payload, headers=headers, timeout=30)
        print(f"API Response Status: {response.status_code}")
        print(f"API Response: {response.text[:500]}")
        response.raise_for_status()
        result = response.json()
        
        # 尝试不同的响应格式
        if "embeddings" in result:
            return result["embeddings"][0]
        elif "vectors" in result:
            return result["vectors"][0]
        elif "data" in result and len(result["data"]) > 0:
            return result["data"][0].get("embedding", result["data"][0].get("vector"))
        else:
            raise ValueError(f"未知的API响应格式: {list(result.keys())}")
    
    def get_completion(self, prompt: str, context: str) -> str:
        """调用LLM生成回答"""
        url = f"{self.base_url}/text/chatcompletion_v2"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        system_prompt = f"""你是武汉大学信息管理学院智能助手。请根据以下上下文信息回答用户的问题。

上下文信息：
{context}

请基于上述上下文给出准确、简洁的回答。如果上下文中没有相关信息，请明确告知用户。"""
        
        payload = {
            "model": "MiniMax-M1",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000,
            "bot_setting": {
                "bot_name": "SIM-Chat助手",
                "content": "武汉大学信息管理学院智能问答助手"
            }
        }
        
        response = httpx.post(url, json=payload, headers=headers, timeout=60)
        print(f"LLM API Response Status: {response.status_code}")
        print(f"LLM API Response: {response.text[:500]}")
        response.raise_for_status()
        result = response.json()
        
        # 处理不同的响应格式
        if "choices" in result and result.get("choices"):
            return result["choices"][0]["message"]["content"]
        elif "reply" in result and result["reply"]:
            return result["reply"]
        else:
            return f"抱歉，AI服务暂时无法回答，但已为您找到相关文档。"

minimax_client = MiniMaxClient()
