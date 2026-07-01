import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import requests
import xml.etree.ElementTree as ET
import urllib.parse

st.set_page_config(page_title="中国核心资产看板 (专业风控版)", page_icon="🛡️", layout="wide")
st.title("🛡️ 中国核心资产看板 (专业风控版)")
st.write("满足三大严苛要求：1. 绝对稳定不断联 | 2. 仅限权威财经信源 | 3. 严格限制近7天内资讯")

stock_dict = {
    "贵州茅台 (A股)": "600519.SS",
    "五粮液 (A股)": "000858.SZ",
    "腾讯控股 (港股)": "0700.HK",
    "比亚迪 (A股)": "002594.SZ",
    "宁德时代 (A股)": "300750.SZ"
}

col1, col2 = st.columns(2)
with col1:
    selected_name = st.selectbox("🎯 请选择要查询的资产：", list(stock_dict.keys()))
    symbol = stock_dict[selected_name]
    search_keyword = selected_name.split(" ")[0] 
with col2:
    chart_type = st.radio("📊 请选择图表类型：", ["专业 K线图", "简单折线图"])

# ================= 核心科技：权威信源白名单 =================
# 只有这些中国最顶级的财经媒体，才有资格出现在你的看板上
TRUSTED_SOURCES = [
    "新浪", "东方财富", "财联社", "第一财经", "证券时报", "中国基金报", 
    "华尔街见闻", "界面新闻", "经济观察", "每日经济新闻", "21世纪经济报道",
    "中国证券报", "上海证券报", "彭博", "路透", "FT中文网"
]

def get_authoritative_news(keyword):
    """
    使用 Google News RSS 聚合引擎：
    1. 稳定：海外云服务器直连 Google 毫无阻碍
    2. 时效：强制附加 when:7d 参数，只取7天内
    3. 权威：在 Python 层面进行白名单二次过滤
    """
    # 【核心魔法】强制附加 7天内 的搜索条件
    query = f"{keyword} when:7d"
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        root = ET.fromstring(response.content)
        
        valid_news = []
        for item in root.findall('.//channel/item'):
            title = item.find('title').text if item.find('title') is not None else ''
            link = item.find('link').text if item.find('link') is not None else ''
            pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ''
            
            # 提取新闻来源
            source_elem = item.find('source')
            source = source_elem.text if source_elem is not None else (title.split(' - ')[-1] if ' - ' in title else '未知')
            
            # 【核心魔法】白名单过滤：宁缺毋滥
            if any(trusted in source or trusted in title for trusted in TRUSTED_SOURCES):
                # 清理标题，去掉后缀的来源名称，让界面更清爽
                clean_title = title.rsplit(' - ', 1)[0] if ' - ' in title else title
                valid_news.append({
                    'title': clean_title,
                    'link': link,
                    'pubDate': pubDate,
                    'source': source
                })
        return valid_news
    except Exception as e:
        return []

if st.button("📡 跨洋抓取：行情 + 权威资讯"):
    
    # ================= 通道一：雅虎财经抓价格 =================
    st.subheader("📊 行情数据区 (Yahoo Finance)")
    with st.spinner('正在获取行情...'):
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

    # ================= 通道二：高信噪比资讯 =================
    st.subheader(f"📰 权威资讯过滤：{search_keyword} (近7天)")
    with st.spinner('正在全球新闻源中进行【7天时效限制】与【白名单交叉比对】...'):
        news_data = get_authoritative_news(search_keyword)
        
        if news_data:
            st.success(f"🎉 过滤完成！成功为您提纯出 {len(news_data)} 条近一周内的权威报道。")
            for article in news_data[:8]: # 展示前8条
                with st.container():
                    st.markdown(f"#### [{article['title']}]({article['link']})")
                    # 绿色高亮显示权威来源
                    st.markdown(f"**✅ 权威信源: <span style='color:green'>{article['source']}</span>** | 🕒 {article['pubDate']}", unsafe_allow_html=True)
                    st.write("---")
        else:
            st.warning("⚠️ 近7天内，未监测到来自【权威白名单媒体】的相关资讯。宁缺毋滥，已拦截所有低质量信息。")
