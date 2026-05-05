"""
向量化入库脚本 - 本地模式
使用本地文件系统存储向量，无需Docker
"""
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

print("=" * 70)
print("开始向量化入库流程")
print("=" * 70)

# 检查必要的依赖
try:
    import chromadb
    print("✅ ChromaDB 已安装")
except ImportError:
    print("❌ 缺少 chromadb 依赖")
    print("请运行: pip install chromadb")
    sys.exit(1)

try:
    import httpx
    print("✅ httpx 已安装")
except ImportError:
    print("❌ 缺少 httpx 依赖")
    print("请运行: pip install httpx")
    sys.exit(1)

# 检查分块文件
CHUNK_FILE = "./chunks.json"
if not os.path.exists(CHUNK_FILE):
    print(f"\n❌ 未找到分块文件: {CHUNK_FILE}")
    print("请先运行 chunk.py 生成分块数据")
    sys.exit(1)

# 加载分块数据
print(f"\n加载分块数据: {CHUNK_FILE}")
with open(CHUNK_FILE, 'r', encoding='utf-8') as f:
    chunks = json.load(f)

print(f"✅ 成功加载 {len(chunks)} 个数据块")

# 检查API密钥
API_KEY = os.getenv("MINIMAX_API_KEY")
GROUP_ID = os.getenv("MINIMAX_GROUP_ID")

if not API_KEY or API_KEY == "your_minimax_api_key_here":
    print("\n⚠️  警告: 未配置 MiniMax API 密钥")
    print("请在 .env 文件中配置 MINIMAX_API_KEY 和 MINIMAX_GROUP_ID")
    print("\n为了演示，现在将使用本地向量数据库（不调用API）")
    USE_API = False
else:
    USE_API = True
    print(f"\n✅ MiniMax API 密钥已配置")

# 创建本地向量数据库
print("\n创建本地向量数据库...")
COLLECTION_NAME = "sim_chat_docs"
DB_DIR = "./chroma_db"

# 使用持久化客户端
client = chromadb.PersistentClient(path=DB_DIR)

# 创建或获取集合
try:
    collection = client.get_collection(name=COLLECTION_NAME)
    print(f"✅ 找到现有集合: {COLLECTION_NAME}")
except:
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )
    print(f"✅ 创建新集合: {COLLECTION_NAME}")

# 检查已有文档数量
existing_count = collection.count()
print(f"📊 集合中已有 {existing_count} 个文档")

if existing_count > 0:
    print("\n⚠️  集合中已有数据，是否要清空重新入库？")
    choice = input("输入 'y' 清空并继续，其他键跳过: ")
    if choice.lower() == 'y':
        client.delete_collection(name=COLLECTION_NAME)
        collection = client.create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        print("✅ 集合已清空")
    else:
        print("跳过入库流程")
        sys.exit(0)

# 向量化入库
print(f"\n开始向量化入库 (共 {len(chunks)} 个文档)...")

success_count = 0
error_count = 0

if USE_API:
    # 使用 MiniMax API 生成向量
    from embed import EmbeddingService
    embedding_service = EmbeddingService()
    
    for i, chunk in enumerate(chunks):
        try:
            if (i + 1) % 10 == 0:
                print(f"处理进度: {i + 1}/{len(chunks)}")
            
            # 生成向量
            embedding = embedding_service.get_embedding(chunk["content"])
            
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
        except Exception as e:
            print(f"❌ 处理块 {chunk['id']} 时出错: {e}")
            error_count += 1
else:
    # 演示模式：使用简单的TF-IDF向量
    print("\n📝 演示模式：使用本地特征（不调用API）")
    print("   实际使用时请配置 MiniMax API 密钥")
    
    for i, chunk in enumerate(chunks):
        try:
            if (i + 1) % 50 == 0:
                print(f"处理进度: {i + 1}/{len(chunks)}")
            
            # 生成简单的词频向量作为演示
            # 实际使用时会使用 MiniMax API
            content = chunk["content"]
            
            # 只存储文档，不生成向量（用于演示）
            collection.add(
                ids=[chunk["id"]],
                documents=[content],
                metadatas=[{
                    "heading": chunk["heading"],
                    "source": chunk["source"]
                }]
            )
            
            success_count += 1
        except Exception as e:
            print(f"❌ 处理块 {chunk['id']} 时出错: {e}")
            error_count += 1

# 统计结果
print("\n" + "=" * 70)
print("入库完成！")
print("=" * 70)
print(f"✅ 成功: {success_count} 个文档")
print(f"❌ 失败: {error_count} 个文档")
print(f"📊 集合总数: {collection.count()} 个文档")
print(f"💾 数据库位置: {os.path.abspath(DB_DIR)}")
print("=" * 70)

print("\n下一步:")
print("1. 配置 MiniMax API 密钥以启用真实的向量生成")
print("2. 启动后端服务: cd ../backend && uvicorn app.main:app --reload")
print("3. 启动前端服务: cd ../frontend && streamlit run app.py")
print("4. 访问应用: http://localhost:8501")
