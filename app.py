import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="中国核心资产看板 (国内直连版)", page_icon="⚡", layout="wide")
st.title("⚡ 中国核心资产看板 (国内直连版)")
st.write("彻底解决新闻打不开的问题！图表走海外云端，资讯走本地直连，100% 契合国内网络环境！")

# 股票字典：同时保存雅虎代码和国内纯数字代码
stock_dict = {
    "贵州茅台 (白酒)": {"yahoo": "600519.SS", "code": "600519", "market": "SH"},
    "五粮液 (白酒)": {"yahoo": "000858.SZ", "code": "000858", "market": "SZ"},
    "腾讯控股 (港股)": {"yahoo": "0700.HK", "code": "0700", "market": "HK"},
    "比亚迪 (新能源)": {"yahoo": "002594.SZ", "code": "002594", "market": "SZ"},
    "宁德时代 (电池)": {"yahoo": "300750.SZ", "code": "300750", "market": "SZ"}
}

col1, col2 = st.columns(2)
with col1:
    selected_name = st.selectbox("🎯 请选择要查询的资产：", list(stock_dict.keys()))
    stock_info = stock_dict[selected_name]
with col2:
    chart_type = st.radio("📊 请选择图表类型：", ["专业 K线图", "简单折线图"])

if st.button("📡 获取最新行情与资讯直达通道"):
    
    # ================= 通道一：云端获取 K线图 (稳定不被墙) =================
    st.subheader("📊 行情数据区 (云端直连)")
    with st.spinner('正在获取行情...'):
        try:
            ticker = yf.Ticker(stock_info["yahoo"])
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

    # ================= 通道二：本地 Wi-Fi 直连国内权威门户 =================
    st.subheader(f"📰 深度资讯直达：{selected_name.split(' ')[0]}")
    st.info("💡 极客提示：以下通道将使用您当前的本地网络直接打开，无需 VPN，绝对秒开，且均为国内最权威的中文财经社区！")
    
    # 动态生成国内各大门户的专属链接
    code = stock_info["code"]
    market = stock_info["market"]
    
    # 东方财富链接拼接
    em_prefix = "sh" if market == "SH" else ("sz" if market == "SZ" else "hk")
    eastmoney_url = f"http://quote.eastmoney.com/{em_prefix}{code}.html"
    
    # 雪球链接拼接
    xq_prefix = market
    xueqiu_url = f"https://xueqiu.com/S/{xq_prefix}{code}"
    
    # 新浪财经链接拼接
    sina_url = f"https://finance.sina.com.cn/realstock/company/{em_prefix}{code}/nc.shtml"

    # 使用 Streamlit 的分列功能，把按钮排得漂漂亮亮
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    
    with btn_col1:
        st.markdown(f"""
        <a href="{eastmoney_url}" target="_blank">
            <button style="width:100%; padding:15px; background-color:#FF4B4B; color:white; border:none; border-radius:5px; font-size:16px; cursor:pointer;">
                🔴 前往【东方财富】看研报
            </button>
        </a>
        """, unsafe_allow_html=True)
        
    with btn_col2:
        st.markdown(f"""
        <a href="{xueqiu_url}" target="_blank">
            <button style="width:100%; padding:15px; background-color:#0066FF; color:white; border:none; border-radius:5px; font-size:16px; cursor:pointer;">
                🔵 前往【雪球】看大V讨论
            </button>
        </a>
        """, unsafe_allow_html=True)
        
    with btn_col3:
        st.markdown(f"""
        <a href="{sina_url}" target="_blank">
            <button style="width:100%; padding:15px; background-color:#FF9900; color:white; border:none; border-radius:5px; font-size:16px; cursor:pointer;">
                🟠 前往【新浪财经】看新闻
            </button>
        </a>
        """, unsafe_allow_html=True)
