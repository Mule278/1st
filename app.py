import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="全球核心资产看板 (云端版)", page_icon="🌍", layout="wide")
st.title("🌍 全球核心资产看板 (云端直连版)")
st.write("当前运行环境：美国云服务器 | 数据源：Yahoo Finance (海外直连，无视国内防火墙)")

# 雅虎财经的 A股代码规则：上交所加 .SS，深交所加 .SZ
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
with col2:
    chart_type = st.radio("📊 请选择图表类型：", ["专业 K线图", "简单折线图"])

if st.button("📡 跨洋抓取真实数据"):
    with st.spinner('云服务器正在向华尔街发送请求...'):
        try:
            # 使用 yfinance 抓取过去 3 个月的真实数据
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="3mo")
            
            if not df.empty:
                st.success(f"🎉 抓取成功！这是来自全球金融数据库的【真实数据】！")
                
                # 处理时区和日期格式
                df.index = df.index.strftime("%Y-%m-%d")
                
                fig = go.Figure()
                if chart_type == "专业 K线图":
                    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="K线"))
                else:
                    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines+markers', line=dict(color='red', width=2), name="收盘价"))
                
                fig.update_xaxes(type='category', tickangle=45)
                fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # 展示最新新闻 (雅虎财经自带的英文新闻)
                st.subheader("📰 华尔街视野：最新相关资讯")
                news = ticker.news
                if news:
                    for article in news[:5]:
                        with st.container():
                            st.markdown(f"#### [{article['title']}]({article['link']})")
                            st.caption(f"来源: {article['publisher']}")
                            st.write("---")
                else:
                    st.info("暂无该资产的最新海外资讯。")
            else:
                st.error("抓取失败：数据为空。")
                
        except Exception as e:
            st.error(f"抓取报错：{e}")
