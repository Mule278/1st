import os
import socket # 引入底层网络控制工具

# 【关键修复】给 Python 设定“耐心值”：全局网络请求最多等 3 秒！
# 如果 3 秒没连上，强制抛出异常，瞬间触发我们的容灾机制！
socket.setdefaulttimeout(3.0) 

os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""

import streamlit as st
import pandas as pd
# ... 下面保留你原来的所有代码 ...
import os
os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 尝试导入 akshare，如果失败也不影响网页运行
try:
    import akshare as ak
    HAS_AK = True
except ImportError:
    HAS_AK = False

st.set_page_config(page_title="中国核心资产看板 (终极防御版)", page_icon="🛡️", layout="wide")
st.title("🛡️ 核心资产：A股全景看板 (终极防御版)")
st.write("已启用【军工级容灾机制】：如果网络拦截了真实数据，系统将自动切换至模拟数据，保证网页永不崩溃！")

stock_dict = {
    "贵州茅台 (白酒)": "600519",
    "五粮液 (白酒)": "000858",
    "中国海油 (能源)": "600938", 
    "招商银行 (金融)": "600036",
    "比亚迪 (新能源)": "002594"
}

col1, col2 = st.columns(2)
with col1:
    selected_name = st.selectbox("🎯 请选择要查询的资产：", list(stock_dict.keys()))
    symbol = stock_dict[selected_name]
with col2:
    chart_type = st.radio("📊 请选择图表类型：", ["专业 K线图 (蜡烛图)", "简单折线图 (收盘价)"])

# ================= 容灾核心：生成逼真的模拟数据 =================
def generate_mock_kline(days=90):
    """当真实网络被墙时，生成逼真的模拟K线数据"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='B')
    close = 100 + np.random.randn(days).cumsum() * 2
    open_p = close + np.random.randn(days)
    high = np.maximum(open_p, close) + np.abs(np.random.randn(days))
    low = np.minimum(open_p, close) - np.abs(np.random.randn(days))
    return pd.DataFrame({'日期': dates.strftime("%Y-%m-%d"), '开盘': open_p, '最高': high, '最低': low, '收盘': close})

def generate_mock_news():
    """当真实新闻接口失效时，生成模拟新闻"""
    now = datetime.now()
    return pd.DataFrame([
        {"时间": (now - timedelta(minutes=5)).strftime("%H:%M:%S"), "内容": f"【突发】{selected_name} 获主力资金净流入超5亿元，机构持续看好。"},
        {"时间": (now - timedelta(minutes=15)).strftime("%H:%M:%S"), "内容": "【行业】相关产业链上下游企业订单饱满，预计三季度业绩将超预期。"},
        {"时间": (now - timedelta(minutes=32)).strftime("%H:%M:%S"), "内容": "【宏观】央行今日开展1000亿元逆回购操作，市场流动性保持合理充裕。"},
        {"时间": (now - timedelta(minutes=45)).strftime("%H:%M:%S"), "内容": f"【研报】中金公司发布最新研报，维持 {selected_name} “跑赢行业”评级。"},
        {"时间": (now - timedelta(minutes=60)).strftime("%H:%M:%S"), "内容": "【市场】北向资金今日早盘净买入超30亿元，核心资产受外资青睐。"}
    ])

# ================= 抓取与展示逻辑 =================
if st.button("📡 全面抓取：行情 + 实时电报"):
    
    # --- 通道一：行情数据 ---
    st.subheader("📊 行情数据区")
    with st.spinner('正在尝试突破防火墙获取真实行情...'):
        df = pd.DataFrame()
        is_mock_kline = False
        
        if HAS_AK:
            try:
                end_date = datetime.now().strftime("%Y%m%d")
                start_date = (datetime.now() - timedelta(days=90)).strftime("%Y%m%d")
                df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
                if df.empty: raise ValueError("数据为空")
            except Exception:
                # 真实请求失败，瞬间切换到模拟数据
                df = generate_mock_kline()
                is_mock_kline = True
        else:
            df = generate_mock_kline()
            is_mock_kline = True

        if is_mock_kline:
            st.warning("⚠️ 真实网络请求被您的校园网/防火墙拦截。已自动启用【容灾机制】，展示模拟演示数据。")
        else:
            st.success("🎉 成功突破网络封锁，获取到真实行情数据！")
            
        df['日期'] = df['日期'].astype(str) 
        fig = go.Figure()
        if chart_type == "专业 K线图 (蜡烛图)":
            fig.add_trace(go.Candlestick(x=df['日期'], open=df['开盘'], high=df['最高'], low=df['最低'], close=df['收盘'], name="K线"))
        else:
            fig.add_trace(go.Scatter(x=df['日期'], y=df['收盘'], mode='lines+markers', line=dict(color='red', width=2), name="收盘价"))
        
        fig.update_xaxes(type='category', tickangle=45)
        fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # --- 通道二：新闻数据 ---
    st.subheader("⚡ 财联社：全市场实时电报")
    with st.spinner('正在尝试连接新闻专线...'):
        news_df = pd.DataFrame()
        is_mock_news = False
        
        if HAS_AK:
            try:
                # 尝试用最新的全局新闻接口
                news_df = ak.stock_info_global_cls()
                if news_df.empty: raise ValueError("数据为空")
                if '发布时间' in news_df.columns and '标题' in news_df.columns:
                    news_df = news_df[['发布时间', '标题']].rename(columns={'发布时间': '时间', '标题': '内容'})
            except Exception:
                is_mock_news = True
                news_df = generate_mock_news()
        else:
            is_mock_news = True
            news_df = generate_mock_news()

        if is_mock_news:
            st.warning("⚠️ 真实新闻接口被拦截或发生变更。已自动启用【容灾机制】，展示模拟演示数据。")
        else:
            st.success("🎉 成功获取真实新闻数据！")
            
        st.dataframe(news_df.head(5), use_container_width=True)