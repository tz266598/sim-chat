# SIM-Chat 武汉大学信息管理学院智能问答助手

基于 RAG（检索增强生成）架构的智能问答系统，为武汉大学信息管理学院学生提供准确的学院信息咨询服务。

## 📋 项目简介

SIM-Chat 是一个面向武汉大学信息管理学院学生的智能问答助手，能够帮助学生快速查询：

- ✅ 培养方案与课程设置
- ✅ 师资队伍介绍
- ✅ 学院新闻与通知公告
- ✅ 科学研究成果
- ✅ 年级群通知

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户 (学生)                          │
│                    网页对话界面 (Streamlit)                  │
│                   深绿色 + 白色主题                          │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP
┌──────────────────────────▼──────────────────────────────────┐
│                     FastAPI 后端                            │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  检索模块   │───▶│  LLM 模块   │───▶│  回答生成   │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                                        ▲          │
│         ▼                                        │          │
│  ┌─────────────┐                           ┌─────────────┐  │
│  │  ChromaDB  │◀──────────────────────────│ MiniMax API │  │
│  │ 向量数据库  │     (Embedding & LLM)     │             │  │
│  └─────────────┘                           └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 核心技术栈

| 组件 | 技术选型 | 说明 |
|------|---------|------|
| **前端框架** | Streamlit | Python 原生 Web 框架 |
| **后端框架** | FastAPI | 轻量异步 API 框架 |
| **向量数据库** | ChromaDB | 轻量级向量数据库 |
| **Embedding** | MiniMax embo-01 | 中文文本向量化 |
| **LLM** | MiniMax Text-01 | 国产大语言模型 |
| **部署方案** | Docker Compose | 一键部署 |

## 📁 项目结构

```
sim-chat/
├── backend/                  # 后端服务
│   ├── app/
│   │   ├── main.py          # FastAPI 入口
│   │   ├── api/
│   │   │   └── chat.py     # 聊天 API
│   │   ├── core/
│   │   │   ├── config.py   # 配置管理
│   │   │   └── minmax.py   # MiniMax API 调用
│   │   └── services/
│   │       ├── vectorstore.py  # ChromaDB 操作
│   │       └── retrieval.py    # 检索逻辑
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                 # 前端服务
│   ├── app.py              # Streamlit 入口
│   ├── requirements.txt
│   └── Dockerfile
├── data_processing/         # 数据处理脚本
│   ├── clean.py            # 数据清洗
│   ├── chunk.py            # 数据分块
│   ├── embed.py            # 向量化入库
│   └── requirements.txt
├── docs/                   # 项目文档
├── docker-compose.yml      # 一键部署配置
├── .env.example            # 环境变量示例
└── README.md               # 项目说明
```

## 🚀 快速开始

### 前置条件

- Docker >= 20.10
- Docker Compose >= 2.0
- MiniMax API Key 和 Group Key（从 [MiniMax 官网](https://www.minimax.chat/) 获取）

### 安装步骤

#### 1. 克隆项目

```bash
git clone <repository-url>
cd sim-chat
```

#### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 MiniMax API 密钥：

```env
MINIMAX_API_KEY=your_api_key_here
MINIMAX_GROUP_ID=your_group_id_here
```

#### 3. 准备数据

将学院相关的 Markdown 文档放入 `data_processing/raw_docs/` 目录：

```bash
mkdir -p data_processing/raw_docs
# 复制你的 .md 文件到 data_processing/raw_docs/
```

#### 4. 数据处理

```bash
cd data_processing
pip install -r requirements.txt

# 步骤 1: 数据清洗
python clean.py

# 步骤 2: 数据分块
python chunk.py

# 步骤 3: 向量化入库（确保 ChromaDB 已启动）
python embed.py
```

#### 5. 启动服务

**方式一：Docker Compose（推荐）**

```bash
# 一键启动所有服务
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

**方式二：本地开发**

启动 ChromaDB：
```bash
docker-compose -f docker-compose.chroma.yml up -d
```

启动后端：
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

启动前端：
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

### 访问应用

- **前端界面**: http://localhost:8501
- **后端 API**: http://localhost:8001
- **API 文档**: http://localhost:8001/docs
- **ChromaDB**: http://localhost:8000

## 💡 使用示例

在浏览器中打开 http://localhost:8501，尝试以下问题：

### 测试问题 1：毕业实习学分
```
《毕业实习》课程是几个学分？
```

### 测试问题 2：新闻查询
```
2026年4月3日吴江教授团队发布了什么？
```

### 测试问题 3：课程查询
```
图书馆学专业的必修课程有哪些？
```

### API 调用示例

```bash
# 健康检查
curl http://localhost:8001/api/health

# 查看已加载数据
curl http://localhost:8001/api/collections

# 发送聊天请求
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "《毕业实习》课程是几个学分？"}'
```

## 🎨 界面特点

- **深墨绿渐变背景** (`#0D1F17` → `#1A2F25`)
- **低饱和度绿色气泡**（用户右侧 / AI 左侧）
- **武汉大学校徽**作为背景装饰
- **极简学术风格**，无多余装饰
- **来源追溯**：回答附带参考文档来源

## 🔧 开发指南

### 后端开发

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

访问 Swagger API 文档：http://localhost:8000/docs

### 前端开发

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

### 数据处理流程

1. **数据清洗** (`clean.py`): 去除网页残留、规范化 Markdown
2. **数据分块** (`chunk.py`): 基于标题层级智能分块（最大 500 字符，重叠 50 字符）
3. **向量化入库** (`embed.py`): 调用 MiniMax API 生成向量并存入 ChromaDB

## 📊 系统架构

### RAG 工作流程

```
用户提问
    │
    ▼
┌─────────────────────────────────────────┐
│  1. 问题向量化 (Embedding)              │
│     用户问题 → MiniMax API → 向量       │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  2. 向量检索 (Retrieval)                │
│     查询向量 → ChromaDB → Top-5 相关文档 │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  3. 回答生成 (Generation)               │
│     上下文 + 问题 → MiniMax LLM → 回答  │
└─────────────────┬───────────────────────┘
                  │
                  ▼
               返回回答
```

## 🔮 未来改进

- [ ] 支持多轮对话上下文
- [ ] 增加实时数据更新机制
- [ ] 优化回答来源展示
- [ ] 增加语音输入功能
- [ ] 支持移动端适配
- [ ] 增加用户反馈机制
- [ ] 支持多语言

## 📝 许可证

本项目仅供学习和研究使用。

## 👥 团队

武汉大学信息管理学院

## 📞 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。

---

**武汉大学信息管理学院 · SIM-Chat 智能问答助手**
