import streamlit as st
import requests
import os

# 页面配置
st.set_page_config(
    page_title="SIM-Chat 武汉大学信息管理学院智能问答",
    page_icon="🎓",
    layout="centered"
)

# 自定义CSS样式
custom_css = """
<style>
    /* 背景渐变 */
    .stApp {
        background: linear-gradient(135deg, #0D1F17 0%, #1A2F25 100%);
    }
    
    /* 主标题 */
    .main-title {
        color: #FFFFFF;
        text-align: center;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        color: #A8D5BA;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* 聊天容器 */
    .chat-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        max-height: 600px;
        overflow-y: auto;
    }
    
    /* 用户消息气泡 */
    .user-message {
        background: #2E7D52;
        color: white;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        margin: 10px 0 10px auto;
        max-width: 70%;
        word-wrap: break-word;
    }
    
    /* AI消息气泡 */
    .ai-message {
        background: #1A3A2A;
        color: #E0F0E8;
        padding: 12px 18px;
        border-radius: 18px 18px 18px 4px;
        margin: 10px 0 10px 0;
        max-width: 70%;
        word-wrap: break-word;
    }
    
    /* 输入框 */
    .stTextInput input {
        background: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid #2E7D52;
        border-radius: 20px;
        padding: 12px 20px;
    }
    
    /* 来源信息 */
    .source-info {
        background: rgba(46, 125, 82, 0.2);
        border-left: 3px solid #2E7D52;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
        font-size: 0.85rem;
        color: #A8D5BA;
    }
    
    /* 武汉大学校徽水印 */
    .watermark {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        opacity: 0.03;
        z-index: -1;
        font-size: 400px;
        color: white;
    }
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)
st.markdown('<div class="watermark">🎓</div>', unsafe_allow_html=True)

# 标题
st.markdown('<div class="main-title">SIM-Chat</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">武汉大学信息管理学院智能问答助手</div>', unsafe_allow_html=True)

# API配置
API_URL = os.getenv("BACKEND_URL", "http://localhost:8001")

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示聊天历史
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ai-message">{message["content"]}</div>', unsafe_allow_html=True)
            if message.get("sources"):
                for i, source in enumerate(message["sources"], 1):
                    st.markdown(
                        f'<div class="source-info">📄 参考来源 {i}: {source["metadata"].get("source", "未知文档")}</div>',
                        unsafe_allow_html=True
                    )

# 输入框
user_input = st.text_input("", placeholder="请输入您的问题...", key="user_input", label_visibility="collapsed")

if user_input and st.button("发送", key="send_button"):
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 调用后端API
    try:
        response = requests.post(
            f"{API_URL}/api/chat",
            json={"question": user_input},
            timeout=30
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
                "content": "抱歉，服务器出现错误，请稍后重试。"
            })
    except Exception as e:
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"抱歉，无法连接到后端服务。请检查服务是否正常运行。\n错误信息：{str(e)}"
        })
    
    # 清空输入框
    st.rerun()
