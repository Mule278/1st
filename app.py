import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from duckduckgo_search import DDGS

st.set_page_config(page_title="全球核心资产看板 (专业版)", page_icon="👔", layout="wide")
st.title("👔 全球核心资产看板 (高信噪比专业版)")
st.write("已启用【权威信源白名单】过滤机制，自动剔除自媒体与垃圾信息，只看真实可靠的财经要闻！")

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
    search_keyword = selected_name.split(" ")[0] 
with col2:
    chart_type = st.radio("📊 请选择图表类型：", ["专业 K线图", "简单折线图"])

# ================= 核心科技：权威信源白名单 =================
# 只有发布机构的名字里包含这些词，新闻才会被显示！
TRUSTED_SOURCES = [
    "新浪", "东方财富", "财联社", "第一财经", "证券时报", "中国基金报", 
    "华尔街见闻", "界面新闻", "经济观察网", "彭博", "路透", "Yahoo", 
    "Bloomberg", "Reuters", "CNBC", "WSJ"
]

if st.button("📡 跨洋抓取：行情 + 权威资讯"):
    
    # --- 通道一：行情数据 ---
    st.subheader("📊 行情数据区 (Yahoo Finance)")
    with st.spinner('正在获取全球行情...'):
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="3mo")
            if not df.empty:
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

    # --- 通道二：带“测谎仪”的新闻过滤 ---
    st.subheader(f"📰 权威资讯过滤：{search_keyword}")
    with st.spinner('🤖 AI 正在全网检索并进行【白名单交叉比对】...'):
        try:
            with DDGS() as ddgs:
                # 故意多搜一点（搜20条），因为我们要过滤掉很多垃圾信息
                raw_results = list(ddgs.news(search_keyword, max_results=20))
                
            if raw_results:
                # 核心过滤逻辑：比对白名单
                filtered_news = []
                for article in raw_results:
                    source_name = article.get('source', '')
                    # 如果新闻来源在我们的白名单里，就把它加到最终列表里
                    if any(trusted in source_name for trusted in TRUSTED_SOURCES):
                        filtered_news.append(article)
                
                if filtered_news:
                    st.success(f"🎉 过滤完成！从 {len(raw_results)} 条全网信息中，为您提纯出 {len(filtered_news)} 条权威报道。")
                    # 只展示前 5 条最权威的
                    for article in filtered_news[:5]:
                        with st.container():
                            st.markdown(f"#### [{article['title']}]({article['url']})")
                            # 用绿色高亮显示权威来源，让你看着放心
                            st.markdown(f"**✅ 权威信源认证: <span style='color:green'>{article['source']}</span>** | {article['date']}", unsafe_allow_html=True)
                            st.write(article['body'])
                            st.write("---")
                else:
                    st.warning("⚠️ 搜到了新闻，但没有一条来自权威媒体，为保证数据真实性，已全部拦截！")
            else:
                st.info("暂无最新资讯。")
        except Exception as e:
            st.error(f"资讯抓取报错：{e}")
