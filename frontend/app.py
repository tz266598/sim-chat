import streamlit as st
import requests
import os
import time
import re

st.set_page_config(
    page_title="SIM-Chat · 信息管理学院智能问答",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== 自定义CSS ==========
custom_css = """
<style>
    /* ===== 全局变量 ===== */
    :root {
        --wuda-blue: #005DAA;
        --wuda-blue-light: #1A73C4;
        --wuda-blue-bg: #EDF2FC;
        --wuda-gold: #C4922E;
        --bg-primary: #F7F8FA;
        --bg-secondary: #FFFFFF;
        --text-primary: #1F2937;
        --text-secondary: #6B7280;
        --text-tertiary: #9CA3AF;
        --border-color: #E5E7EB;
        --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
        --shadow-md: 0 4px 12px rgba(0,0,0,0.08);
        --radius-sm: 8px;
        --radius-md: 16px;
        --radius-lg: 24px;
    }

    /* ===== 全局重置 ===== */
    .stApp {
        background: var(--bg-primary);
    }

    /* 隐藏默认元素 */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* 主内容区域 - 去掉 padding */
    .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        max-width: 900px !important;
    }

    /* ===== 侧边栏样式 ===== */
    [data-testid="stSidebar"] {
        background: #F0F2F6;
        border-right: 1px solid var(--border-color);
    }
    [data-testid="stSidebar"] .block-container {
        padding: 1.2rem 1rem;
    }

    /* 侧边栏品牌区 */
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 4px 16px 4px;
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 16px;
    }
    .sidebar-logo-icon {
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, var(--wuda-blue), var(--wuda-blue-light));
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 18px;
        font-weight: 700;
        flex-shrink: 0;
    }
    .sidebar-brand-text {
        font-size: 15px;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.2;
    }
    .sidebar-brand-sub {
        font-size: 11px;
        color: var(--text-secondary);
        font-weight: 400;
    }

    /* 侧边栏建议问题 */
    .sidebar-section-title {
        font-size: 11px;
        font-weight: 600;
        color: var(--text-tertiary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .sidebar-question-btn {
        width: 100%;
        padding: 10px 12px;
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-sm);
        font-size: 13px;
        color: var(--text-primary);
        cursor: pointer;
        text-align: left;
        transition: all 0.15s ease;
        margin-bottom: 6px;
    }
    .sidebar-question-btn:hover {
        border-color: var(--wuda-blue);
        background: var(--wuda-blue-bg);
        color: var(--wuda-blue);
    }

    /* ===== 顶部欢迎页 ===== */
    .welcome-container {
        text-align: center;
        padding: 60px 20px 30px 20px;
        animation: fadeInUp 0.6s ease;
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .welcome-logo {
        width: 64px;
        height: 64px;
        background: linear-gradient(135deg, var(--wuda-blue), #003D80);
        border-radius: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 20px auto;
        color: white;
        font-size: 28px;
        font-weight: 700;
        box-shadow: 0 8px 24px rgba(0,93,170,0.25);
    }
    .welcome-title {
        font-size: 28px;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 6px;
        letter-spacing: -0.5px;
    }
    .welcome-subtitle {
        font-size: 15px;
        color: var(--text-secondary);
        margin-bottom: 32px;
        line-height: 1.5;
    }
    .welcome-divider {
        width: 40px;
        height: 3px;
        background: var(--wuda-blue);
        border-radius: 2px;
        margin: 0 auto 24px auto;
        opacity: 0.6;
    }

    /* 欢迎页快捷问题卡片 */
    .quick-cards {
        display: flex;
        gap: 12px;
        justify-content: center;
        flex-wrap: wrap;
    }
    .quick-card {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        padding: 16px 20px;
        cursor: pointer;
        transition: all 0.2s ease;
        text-align: left;
        min-width: 220px;
        max-width: 260px;
        flex: 1;
    }
    .quick-card:hover {
        border-color: var(--wuda-blue);
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }
    .quick-card-icon {
        font-size: 22px;
        margin-bottom: 8px;
    }
    .quick-card-title {
        font-size: 14px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 4px;
    }
    .quick-card-desc {
        font-size: 12px;
        color: var(--text-tertiary);
        line-height: 1.4;
    }

    /* ===== 聊天消息区域 ===== */
    .chat-area {
        margin-bottom: 80px;
    }

    /* 用户消息 */
    .user-msg-wrapper {
        display: flex;
        justify-content: flex-end;
        margin: 8px 0;
    }
    .user-msg {
        background: var(--wuda-blue-bg);
        color: var(--text-primary);
        padding: 12px 18px;
        border-radius: var(--radius-lg) var(--radius-lg) 6px var(--radius-lg);
        max-width: 75%;
        font-size: 15px;
        line-height: 1.6;
        word-wrap: break-word;
        border: 1px solid #D6E2F8;
    }

    /* AI消息 */
    .ai-msg-wrapper {
        display: flex;
        margin: 8px 0;
        gap: 10px;
    }
    .ai-avatar {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        background: linear-gradient(135deg, var(--wuda-blue), var(--wuda-blue-light));
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 13px;
        font-weight: 700;
        flex-shrink: 0;
        margin-top: 4px;
    }
    .ai-msg {
        color: var(--text-primary);
        padding: 12px 18px;
        max-width: 75%;
        font-size: 15px;
        line-height: 1.7;
        word-wrap: break-word;
    }
    .ai-msg p {
        margin-bottom: 10px;
    }
    .ai-msg p:last-child {
        margin-bottom: 0;
    }
    .ai-msg code {
        background: #F3F4F6;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 13px;
        color: #D94678;
    }
    .ai-msg pre {
        background: #1E1E2E;
        border-radius: 12px;
        padding: 16px;
        overflow-x: auto;
        margin: 12px 0;
        border: 1px solid #2D2D3F;
    }
    .ai-msg pre code {
        background: transparent;
        color: #CDD6F4;
        padding: 0;
        font-size: 13px;
    }
    .ai-msg ul, .ai-msg ol {
        padding-left: 20px;
        margin: 8px 0;
    }
    .ai-msg li {
        margin-bottom: 4px;
    }
    .ai-msg strong {
        color: #111827;
    }
    .ai-msg blockquote {
        border-left: 3px solid var(--wuda-blue);
        padding-left: 12px;
        margin: 10px 0;
        color: var(--text-secondary);
        background: #F8FAFC;
        padding: 8px 12px;
        border-radius: 0 8px 8px 0;
    }
    .ai-msg table {
        border-collapse: collapse;
        width: 100%;
        margin: 12px 0;
        font-size: 14px;
    }
    .ai-msg th {
        background: #F1F5F9;
        padding: 8px 12px;
        text-align: left;
        font-weight: 600;
        border: 1px solid var(--border-color);
    }
    .ai-msg td {
        padding: 8px 12px;
        border: 1px solid var(--border-color);
    }

    /* ===== 来源引用 ===== */
    .source-ref {
        margin-top: 12px;
        padding: 10px 14px;
        background: #F8FAFC;
        border-radius: 10px;
        border: 1px solid var(--border-color);
        display: flex;
        align-items: flex-start;
        gap: 8px;
        font-size: 12px;
        color: var(--text-secondary);
        transition: all 0.2s ease;
    }
    .source-ref:hover {
        border-color: var(--wuda-blue);
        background: var(--wuda-blue-bg);
    }
    .source-icon {
        font-size: 14px;
        flex-shrink: 0;
        margin-top: 1px;
    }
    .source-link {
        color: var(--wuda-blue);
        text-decoration: none;
    }
    .source-link:hover {
        text-decoration: underline;
    }

    /* ===== 思考中动画 ===== */
    .thinking-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 14px;
        background: #F3F4F6;
        border-radius: 20px;
        font-size: 13px;
        color: var(--text-secondary);
        margin: 8px 0 8px 42px;
    }
    .thinking-dot {
        width: 6px;
        height: 6px;
        background: var(--wuda-blue);
        border-radius: 50%;
        animation: thinkingPulse 1.4s ease-in-out infinite;
    }
    .thinking-dot:nth-child(2) { animation-delay: 0.2s; }
    .thinking-dot:nth-child(3) { animation-delay: 0.4s; }
    @keyframes thinkingPulse {
        0%, 60%, 100% { opacity: 0.3; transform: scale(0.8); }
        30% { opacity: 1; transform: scale(1.2); }
    }

    /* ===== 底部输入区 ===== */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 12px 20px 20px 20px;
        background: linear-gradient(to top, var(--bg-primary) 80%, transparent);
        z-index: 100;
        max-width: 900px;
        margin: 0 auto;
    }
    .input-wrapper {
        display: flex;
        gap: 8px;
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        padding: 6px 6px 6px 16px;
        box-shadow: var(--shadow-md);
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .input-wrapper:focus-within {
        border-color: var(--wuda-blue);
        box-shadow: 0 4px 16px rgba(0,93,170,0.12);
    }
    .input-wrapper input {
        flex: 1;
        border: none;
        outline: none;
        font-size: 15px;
        background: transparent;
        color: var(--text-primary);
    }
    .input-wrapper input::placeholder {
        color: var(--text-tertiary);
    }
    .send-btn {
        background: var(--wuda-blue);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 10px 20px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        white-space: nowrap;
    }
    .send-btn:hover {
        background: var(--wuda-blue-light);
        box-shadow: 0 2px 8px rgba(0,93,170,0.3);
    }
    .send-btn:disabled {
        background: #CBD5E1;
        cursor: not-allowed;
        box-shadow: none;
    }

    /* Streamlit 原生聊天输入框美化 */
    [data-testid="stChatInput"] {
        position: fixed;
        bottom: 20px;
        z-index: 100;
        max-width: 860px !important;
        padding: 0 20px !important;
    }
    [data-testid="stChatInput"] textarea {
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        padding: 12px 16px !important;
        font-size: 15px !important;
        box-shadow: var(--shadow-md) !important;
        background: var(--bg-secondary) !important;
        min-height: 48px !important;
    }
    [data-testid="stChatInput"] textarea:focus {
        border-color: var(--wuda-blue) !important;
        box-shadow: 0 4px 16px rgba(0,93,170,0.12) !important;
    }

    /* ===== 清空按钮样式 ===== */
    .clear-btn {
        background: transparent;
        border: 1px solid var(--border-color);
        color: var(--text-secondary);
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 13px;
        cursor: pointer;
        transition: all 0.15s ease;
        width: 100%;
        text-align: center;
        margin-top: 4px;
    }
    .clear-btn:hover {
        border-color: #EF4444;
        color: #EF4444;
        background: #FEF2F2;
    }

    /* ===== 响应式 ===== */
    @media (max-width: 768px) {
        .welcome-title { font-size: 22px; }
        .quick-card { min-width: 100%; }
        .user-msg, .ai-msg { max-width: 90%; }
    }

    /* ===== 状态标签 ===== */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        margin-top: 12px;
    }
    .status-online {
        background: #ECFDF5;
        color: #059669;
    }
    .status-offline {
        background: #FEF2F2;
        color: #DC2626;
    }
    .status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
    }
    .status-dot-green { background: #10B981; }
    .status-dot-red { background: #EF4444; }

    /* 覆盖Streamlit默认按钮样式 */
    div.stButton > button {
        width: 100%;
        border-radius: var(--radius-sm) !important;
        border: 1px solid var(--border-color) !important;
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        font-size: 13px !important;
        padding: 10px 12px !important;
        text-align: left !important;
        transition: all 0.15s ease !important;
    }
    div.stButton > button:hover {
        border-color: var(--wuda-blue) !important;
        background: var(--wuda-blue-bg) !important;
        color: var(--wuda-blue) !important;
    }

    /* 隐藏stChatInput的默认边距 */
    .stChatInput {
        padding: 0 !important;
    }
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# ========== API配置 ==========
API_URL = os.getenv("BACKEND_URL", "http://localhost:8001")

# ========== 会话状态初始化 ==========
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thinking" not in st.session_state:
    st.session_state.thinking = False
if "backend_online" not in st.session_state:
    st.session_state.backend_online = None

# ========== 检查后端状态 ==========
def check_backend():
    try:
        r = requests.get(f"{API_URL}/api/health", timeout=3)
        st.session_state.backend_online = r.status_code == 200
    except Exception:
        st.session_state.backend_online = False

if st.session_state.backend_online is None:
    check_backend()

# ========== 侧边栏 ==========
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-logo-icon">SIM</div>
        <div>
            <div class="sidebar-brand-text">SIM-Chat</div>
            <div class="sidebar-brand-sub">武汉大学信息管理学院</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔄  新对话", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    if st.session_state.backend_online:
        st.markdown("""
        <div class="status-badge status-online">
            <span class="status-dot status-dot-green"></span> 后端服务正常
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-badge status-offline">
            <span class="status-dot status-dot-red"></span> 后端离线
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="height:16px;"></div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-title">💡 试试这些问题</div>', unsafe_allow_html=True)

    suggested_questions = [
        "《毕业实习》课程是几个学分？",
        "图书馆学专业的必修课程有哪些？",
        "学院2026年推免研究生有哪些要求？",
        "信息管理学院的国际合作项目有哪些？",
        "介绍一下彭斐章教授",
    ]

    for q in suggested_questions:
        if st.button(q, key=f"sq_{hash(q)}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": q})
            st.session_state.thinking = True
            st.rerun()

    st.markdown('<div style="height:24px;"></div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-title">ℹ️ 关于</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:12px;color:#9CA3AF;line-height:1.6;">
        <p><strong>SIM-Chat</strong> 是武汉大学信息管理学院的智能问答助手，基于 RAG 架构构建。</p>
        <p>技术栈：FastAPI + Streamlit + ChromaDB + MiniMax</p>
        <p style="margin-top:8px;">© 2026 武汉大学信息管理学院</p>
    </div>
    """, unsafe_allow_html=True)


# ========== 辅助函数 ==========
def render_markdown(text):
    """渲染Markdown文本为HTML"""
    text = re.sub(
        r'```(\w*)\n(.*?)```',
        r'<pre><code class="language-\1">\2</code></pre>',
        text, flags=re.DOTALL
    )
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" target="_blank">\1</a>', text)
    text = re.sub(r'^[\s]*[-*]\s(.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'^\d+\.\s(.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = text.replace('\n\n', '<br><br>')
    text = text.replace('\n', '<br>')
    return text


def show_thinking():
    """显示思考中动画"""
    st.markdown("""
    <div class="thinking-badge">
        <span>正在检索信息</span>
        <span class="thinking-dot"></span>
        <span class="thinking-dot"></span>
        <span class="thinking-dot"></span>
    </div>
    """, unsafe_allow_html=True)


# ========== 主内容区 ==========

if len(st.session_state.messages) == 0:
    st.markdown("""
    <div class="welcome-container">
        <div class="welcome-logo">SIM</div>
        <div class="welcome-title">你好，我是 SIM-Chat</div>
        <div class="welcome-subtitle">
            武汉大学信息管理学院智能问答助手<br>
            基于学院官网数据，为你提供准确的学术与管理信息
        </div>
        <div class="welcome-divider"></div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    quick_cards = [
        ("📚", "课程信息", "查询课程设置、学分要求和培养方案"),
        ("🎓", "招生政策", "了解推免、考研和转专业相关政策"),
        ("🔬", "学术科研", "探索研究平台、学术成果和科研动态"),
    ]
    for col, (icon, title, desc) in zip([col1, col2, col3], quick_cards):
        with col:
            st.markdown(f"""
            <div class="quick-card" onclick="document.querySelector('textarea').focus()">
                <div class="quick-card-icon">{icon}</div>
                <div class="quick-card-title">{title}</div>
                <div class="quick-card-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="margin-bottom:16px;"></div>
    """, unsafe_allow_html=True)

# ========== 聊天消息渲染 ==========
for idx, message in enumerate(st.session_state.messages):
    if message["role"] == "user":
        st.markdown(f"""
        <div class="user-msg-wrapper">
            <div class="user-msg">{message["content"]}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="ai-msg-wrapper">
            <div class="ai-avatar">AI</div>
            <div class="ai-msg">{render_markdown(message["content"])}</div>
        </div>
        """, unsafe_allow_html=True)

        if message.get("sources"):
            for i, source in enumerate(message["sources"], 1):
                source_name = source.get("metadata", {}).get("source", "未知文档")
                st.markdown(f"""
                <div class="source-ref">
                    <span class="source-icon">📄</span>
                    <span>参考来源 {i}：<span class="source-link">{source_name}</span></span>
                </div>
                """, unsafe_allow_html=True)

if st.session_state.thinking:
    show_thinking()

# ========== 消息发送逻辑 ==========
if st.session_state.thinking:
    thinking_messages = [m for m in st.session_state.messages if m["role"] == "user"]
    if thinking_messages:
        last_user_msg = thinking_messages[-1]["content"]
        st.session_state.thinking = False

        try:
            response = requests.post(
                f"{API_URL}/api/chat",
                json={"question": last_user_msg},
                timeout=60
            )
            if response.status_code == 200:
                result = response.json()
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": result.get("sources", [])
                })
            else:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"⚠️ 服务器返回错误（状态码 {response.status_code}），请稍后重试。"
                })
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"⚠️ 无法连接到后端服务，请检查服务是否正常运行。\n\n> 错误详情：{str(e)}"
            })
        st.rerun()

# ========== 聊天输入框 ==========
if prompt := st.chat_input("输入你的问题，按 Enter 发送..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.thinking = True
    st.rerun()
