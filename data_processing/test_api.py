import httpx
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MINIMAX_API_KEY")
url = "https://api.minimax.chat/v1/embeddings"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
payload = {
    "model": "embo-01",
    "texts": ["测试文本"],
    "type": "document"
}

print("调用 MiniMax Embedding API...")
response = httpx.post(url, json=payload, headers=headers, timeout=30)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:1000]}")

result = response.json()
print(f"\nKeys: {list(result.keys())}")

if "vectors" in result:
    print(f"✅ vectors 维度: {len(result['vectors'][0])}")
elif "embeddings" in result:
    print(f"✅ embeddings 维度: {len(result['embeddings'][0])}")
else:
    print(f"❌ 未找到向量数据")
    print(f"完整响应: {result}")
