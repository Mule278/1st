import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from duckduckgo_search import DDGS # 引入强大的搜索引擎工具

st.set_page_config(page_title="全球核心资产看板 (AI智能体版)", page_icon="🤖", layout="wide")
st.title("🤖 全球核心资产看板 (AI 搜索引擎直连版)")
st.write("彻底抛弃传统爬虫！采用 AI 智能体同款技术：调用搜索引擎实时检索全网最新资讯！")

stock_dict = {
    "贵州茅台 (A股)": "600519.SS",
    "五粮液 (A股)": "000858.SZ",
    "腾讯控股 (港股)": "0700.HK",
    "特斯拉 (美股)": "TSLA",
    "英伟达 (美股)": "NVDA"
}

col1, col2 = st.columns(2)
with col1:
    selected_name = st.selectbox("🎯 请选择要查询的资产：", list(stock_dict.keys()))
    symbol = stock_dict[selected_name]
    # 提取纯中文名字用于搜索引擎检索 (例如把 "特斯拉 (美股)" 变成 "特斯拉")
    search_keyword = selected_name.split(" ")[0] 
with col2:
    chart_type = st.radio("📊 请选择图表类型：", ["专业 K线图", "简单折线图"])

if st.button("📡 跨洋抓取：行情 + 全网资讯"):
    
    # ================= 通道一：雅虎财经抓价格 =================
    st.subheader("📊 行情数据区 (Yahoo Finance)")
    with st.spinner('正在获取全球行情...'):
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="3mo")
            
            if not df.empty:
                st.success(f"🎉 行情抓取成功！")
                df.index = df.index.strftime("%Y-%m-%d")
                
                fig = go.Figure()
                if chart_type == "专业 K线图":
                    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="K线"))
                else:
                    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines+markers', line=dict(color='red', width=2), name="收盘价"))
                
                fig.update_xaxes(type='category', tickangle=45)
                fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("行情抓取失败：数据为空。")
        except Exception as e:
            st.error(f"行情报错：{e}")

    st.divider()

    # ================= 通道二：DuckDuckGo 搜索引擎抓新闻 =================
    st.subheader(f"📰 全网实时资讯：{search_keyword}")
    with st.spinner('🤖 AI 正在调用搜索引擎全网检索...'):
        try:
            # 核心魔法：直接让搜索引擎去搜这个公司的名字！
            with DDGS() as ddgs:
                results = list(ddgs.news(search_keyword, max_results=5))
                
            if results:
                st.success("🎉 资讯抓取成功！(基于搜索引擎实时聚合)")
                for article in results:
                    with st.container():
                        st.markdown(f"#### [{article['title']}]({article['url']})")
                        st.caption(f"来源: {article['source']} | 发布时间: {article['date']}")
                        # 搜索引擎返回的摘要
                        st.write(article['body'])
                        st.write("---")
            else:
                st.warning("⚠️ 搜索引擎未返回最新资讯。")
        except Exception as e:
            st.error(f"资讯抓取报错：{e}")
            st.info("极客提示：云服务器的搜索请求可能过于频繁，请稍后再试。")
