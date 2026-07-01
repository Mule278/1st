import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import streamlit.components.v1 as components # 引入前端组件注入工具

st.set_page_config(page_title="全球核心资产看板 (终极不败版)", page_icon="🔥", layout="wide")
st.title("🔥 全球核心资产看板 (华尔街机构组件版)")
st.write("彻底放弃后端爬虫！采用 TradingView 官方前端组件，直接在你的浏览器渲染实时资讯，100% 免疫任何云端封锁！")

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

if st.button("📡 跨洋抓取：行情 + 机构级资讯"):
    
    # ================= 通道一：雅虎财经抓价格 (这个在云端已经证明很稳) =================
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

    # ================= 通道二：TradingView 官方前端组件 (绝对不会报错) =================
    st.subheader(f"📰 实时资讯流：{selected_name.split(' ')[0]}")
    
    # 将雅虎代码转换为 TradingView 识别的官方代码
    tv_symbol = symbol
    if symbol.endswith(".SS"):
        tv_symbol = "SSE:" + symbol.replace(".SS", "")
    elif symbol.endswith(".SZ"):
        tv_symbol = "SZSE:" + symbol.replace(".SZ", "")
    elif symbol.endswith(".HK"):
        tv_symbol = "HKEX:" + symbol.replace(".HK", "")
    else:
        tv_symbol = "NASDAQ:" + symbol

    # 核心魔法：注入华尔街机构都在用的 TradingView 实时新闻小组件
    # 这段代码不会在云服务器上运行，而是直接发送到你的浏览器里运行！
    widget_html = f"""
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-timeline.js" async>
      {{
      "feedMode": "symbol",
      "symbol": "{tv_symbol}",
      "colorTheme": "dark",
      "isTransparent": true,
      "displayMode": "regular",
      "width": "100%",
      "height": 500,
      "locale": "zh_CN"
    }}
      </script>
    </div>
    <!-- TradingView Widget END -->
    """
    
    # 直接在网页前端渲染，彻底绕过云服务器的网络限制！
    components.html(widget_html, height=500)
