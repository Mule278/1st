import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import google.generativeai as genai

# ================= 1. 页面基础设置 =================
st.set_page_config(page_title="AI 投资智能体", page_icon="🤖", layout="wide")

# ================= 2. 第一道防盗门：密码锁 =================
def check_password():
    """检查用户是否输入了正确的密码"""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.title("🔒 欢迎来到专属 AI 投资看板")
        pwd = st.text_input("请输入访问密码：", type="password")
        if st.button("解锁"):
            # 从云端保险箱读取密码进行比对
            if pwd == st.secrets["APP_PASSWORD"]:
                st.session_state["password_correct"] = True
                st.rerun() # 密码正确，重新加载页面
            else:
                st.error("密码错误，请重试！")
        st.stop() # 密码不正确时，停止运行后面的所有代码

check_password() # 启动密码锁

# ================= 3. 初始化 Gemini AI =================
# 从云端保险箱读取 API Key，绝对安全！
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# ================= 4. 侧边栏：全局控制台 =================
with st.sidebar:
    st.header("⚙️ 智能体控制台")
    
    # 股票选择 (已更新为你专属的核心资产池)
    stock_dict = {
        "贵州茅台 (白酒)": {"yahoo": "600519.SS", "code": "600519", "market": "SH"},
        "五粮液 (白酒)": {"yahoo": "000858.SZ", "code": "000858", "market": "SZ"},
        "中国海油 (能源)": {"yahoo": "600938.SS", "code": "600938", "market": "SH"},
        "招商银行 (金融)": {"yahoo": "600036.SS", "code": "600036", "market": "SH"},
        "中国平安 (保险)": {"yahoo": "601318.SS", "code": "601318", "market": "SH"},
        "比亚迪 (新能源)": {"yahoo": "002594.SZ", "code": "002594", "market": "SZ"},
        "特斯拉 (美股)": {"yahoo": "TSLA", "code": "TSLA", "market": "US"}
    }
    selected_name = st.selectbox("🎯 选择当前关注资产：", list(stock_dict.keys()))
    stock_info = stock_dict[selected_name]
    
    st.divider()
    
    # AI 模型选择 (动态切换大脑)
    # AI 模型选择 (基于你亲自检索出的 2026 年最新真实代号)
    model_dict = {
        "Flash Lite 3.1 (极速轻量)": "gemini-3.1-flash-lite",
        "Flash 3.5 (最新主力大脑)": "gemini-3.5-flash",
        "Pro 3.1 (深度推理预览版)": "gemini-3.1-pro-preview"
    }
    selected_model_name = st.radio("🧠 选择 AI 大脑：", list(model_dict.keys()))
    actual_model_id = model_dict[selected_model_name]
    
    if st.button("🗑️ 清空 AI 聊天记录"):
        st.session_state.messages = []
        st.rerun()

# ================= 5. 主界面：图表与新闻直连 =================
st.title(f"📈 {selected_name} 核心看板")

# --- 行情图表 (云端直连雅虎) ---
with st.expander("📊 展开/收起 K线图表", expanded=True):
    try:
        ticker = yf.Ticker(stock_info["yahoo"])
        df = ticker.history(period="3mo")
        if not df.empty:
            df.index = df.index.strftime("%Y-%m-%d")
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("暂无行情数据")
    except Exception as e:
        st.error("行情加载失败")

# --- 新闻直连 (本地 Wi-Fi 秒开，已适配美股路由) ---
st.write("📰 **深度资讯直达 (点击免翻墙秒开)：**")
code = stock_info["code"]
market = stock_info["market"]

# 智能路由：根据不同市场拼接正确的国内网站链接
if market == "SH":
    em_code, xq_code, sina_url = f"sh{code}", f"SH{code}", f"https://finance.sina.com.cn/realstock/company/sh{code}/nc.shtml"
elif market == "SZ":
    em_code, xq_code, sina_url = f"sz{code}", f"SZ{code}", f"https://finance.sina.com.cn/realstock/company/sz{code}/nc.shtml"
elif market == "US":
    em_code, xq_code, sina_url = f"us{code.lower()}", f"{code}", f"https://stock.finance.sina.com.cn/usstock/quotes/{code}.html"

btn_col1, btn_col2, btn_col3 = st.columns(3)
with btn_col1:
    st.markdown(f'<a href="http://quote.eastmoney.com/{em_code}.html" target="_blank"><button style="width:100%; padding:10px; background-color:#FF4B4B; color:white; border:none; border-radius:5px;">🔴 东方财富 (研报)</button></a>', unsafe_allow_html=True)
with btn_col2:
    st.markdown(f'<a href="https://xueqiu.com/S/{xq_code}" target="_blank"><button style="width:100%; padding:10px; background-color:#0066FF; color:white; border:none; border-radius:5px;">🔵 雪球 (大V讨论)</button></a>', unsafe_allow_html=True)
with btn_col3:
    st.markdown(f'<a href="{sina_url}" target="_blank"><button style="width:100%; padding:10px; background-color:#FF9900; color:white; border:none; border-radius:5px;">🟠 新浪财经 (新闻)</button></a>', unsafe_allow_html=True)

st.divider()

# ================= 6. 核心灵魂：全局记忆 AI 助理 =================
st.subheader(f"🤖 Gemini 投资助理 ({selected_model_name})")
st.caption("💡 提示：聊天记录是全局共享的。你可以先问茅台，再切换到特斯拉让 AI 进行对比分析！")

# 初始化全局聊天记录 (Session State 保证切换股票时不失忆)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 在界面上展示历史聊天记录
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 聊天输入框
if prompt := st.chat_input(f"向 Gemini 提问关于 {selected_name.split(' ')[0]} 的问题..."):
    
    # 1. 把用户的问题显示在界面上，并存入记忆
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 2. 准备调用 Gemini
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner(f'Gemini {selected_model_name.split(" ")[0]} 正在思考...'):
            try:
                # 将 Streamlit 的记忆格式转换为 Gemini 认识的格式
                gemini_history = []
                for m in st.session_state.messages[:-1]: 
                    role = "user" if m["role"] == "user" else "model"
                    gemini_history.append({"role": role, "parts": [m["content"]]})
                
                model = genai.GenerativeModel(actual_model_id)
                chat = model.start_chat(history=gemini_history)
                
                # 【核心破壁魔法】：开启 stream=True，把大段文本拆成碎片发送！
                response = chat.send_message(prompt, stream=True)
                
                full_response = ""
                # 像打字机一样，收到一个碎片就立刻显示在网页上
                for chunk in response:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌") # 加上闪烁的光标
                
                # 最终显示完整内容，去掉光标
                message_placeholder.markdown(full_response)
                
                # 把 AI 的回答存入记忆
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                message_placeholder.error(f"AI 接口调用失败，请检查 API Key 是否正确。错误信息：{e}")
