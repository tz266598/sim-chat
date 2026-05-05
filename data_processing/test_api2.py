import httpx
import os
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MINIMAX_API_KEY")
GROUP_ID = os.getenv("MINIMAX_GROUP_ID")

# 尝试不同的API端点和参数格式
endpoints = [
    {
        "url": f"https://api.minimax.chat/v1/embeddings?GroupId={GROUP_ID}",
        "payload": {
            "model": "embo-01",
            "texts": ["测试文本"],
            "type": "document"
        }
    },
    {
        "url": "https://api.minimax.chat/v1/embeddings",
        "payload": {
            "model": "embo-01",
            "texts": ["测试文本"],
            "type": "db"  # 尝试不同的type
        }
    },
]

for i, ep in enumerate(endpoints, 1):
    print(f"\n测试端点 {i}: {ep['url']}")
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = httpx.post(ep['url'], json=ep['payload'], headers=headers, timeout=30)
    print(f"Status: {response.status_code}")
    result = response.json()
    
    if "vectors" in result and result["vectors"]:
        print(f"✅ 成功! vectors 维度: {len(result['vectors'][0])}")
        break
    else:
        print(f"❌ 失败: {result.get('base_resp', result)}")
