"""
验证向量数据库
检查入库结果并测试检索功能
"""
import chromadb
import json
import os

print("=" * 70)
print("验证向量数据库")
print("=" * 70)

# 连接到本地数据库
DB_DIR = "./chroma_db"
COLLECTION_NAME = "sim_chat_docs"

if not os.path.exists(DB_DIR):
    print("❌ 数据库目录不存在，请先运行 embed_local.py")
    exit(1)

client = chromadb.PersistentClient(path=DB_DIR)

# 获取集合
try:
    collection = client.get_collection(name=COLLECTION_NAME)
    print(f"✅ 成功连接到集合: {COLLECTION_NAME}")
except:
    print("❌ 集合不存在")
    exit(1)

# 统计信息
count = collection.count()
print(f"\n📊 数据库统计:")
print(f"   总文档数: {count}")

# 获取部分文档示例
print(f"\n前5个文档示例:")
results = collection.get(limit=5, include=["documents", "metadatas"])

for i, (doc, metadata) in enumerate(zip(results['documents'], results['metadatas']), 1):
    print(f"\n{i}. {metadata.get('heading', 'N/A')}")
    print(f"   来源: {metadata.get('source', 'N/A')}")
    print(f"   内容预览: {doc[:100]}...")

# 测试检索功能（使用内置embedding）
print("\n" + "=" * 70)
print("测试检索功能")
print("=" * 70)

test_queries = [
    "毕业实习学分",
    "研究生招生要求",
    "学院历史"
]

for query in test_queries:
    print(f"\n查询: {query}")
    try:
        results = collection.query(
            query_texts=[query],
            n_results=3,
            include=["documents", "metadatas", "distances"]
        )
        
        if results['documents'] and results['documents'][0]:
            print(f"  找到 {len(results['documents'][0])} 个相关文档:")
            for i, (doc, metadata, distance) in enumerate(
                zip(results['documents'][0], results['metadatas'][0], results['distances'][0]), 1):
                print(f"  {i}. [{metadata.get('source', 'N/A')}] 距离: {distance:.4f}")
                print(f"     {doc[:80]}...")
        else:
            print("  未找到相关文档")
    except Exception as e:
        print(f"  检索失败: {e}")

print("\n" + "=" * 70)
print("验证完成！")
print("=" * 70)
print(f"\n数据库位置: {os.path.abspath(DB_DIR)}")
print(f"文档总数: {count}")
print("\n下一步:")
print("1. 配置 MiniMax API 密钥以获得更好的向量检索效果")
print("2. 启动后端和前端服务")
print("3. 访问 http://localhost:8501 开始使用")
