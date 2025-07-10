import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
from datetime import datetime, timedelta

st.set_page_config(page_title="시총 Top 10 기업 주가 추이", layout="wide")
st.title("🌍 글로벌 시가총액 Top 10 기업 - 최근 3년 주가 변동")

# 시총 기준 Top 10 기업 및 티커
top10_companies = {
    "Apple (AAPL)": "AAPL",
    "Microsoft (MSFT)": "MSFT",
    "NVIDIA (NVDA)": "NVDA",
    "Saudi Aramco (2222.SR)": "2222.SR",  # 사우디거래소
    "Amazon (AMZN)": "AMZN",
    "Alphabet (GOOGL)": "GOOGL",
    "Meta Platforms (META)": "META",
    "Berkshire Hathaway (BRK-B)": "BRK-B",
    "Eli Lilly (LLY)": "LLY",
    "TSMC (TSM)": "TSM"
}

selected_companies = st.multiselect(
    "🔍 기업을 선택하세요 (복수 선택 가능)",
    list(top10_companies.keys()),
    default=["Apple (AAPL)", "Microsoft (MSFT)", "NVIDIA (NVDA)"]
)

if selected_companies:
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365*3)

    fig = go.Figure()

    for name in selected_companies:
        ticker = top10_companies[name]
        try:
            df = yf.download(ticker, start=start_date, end=end_date)
            if not df.empty:
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df['Close'],
                    mode='lines',
                    name=name
                ))
        except Exception as e:
            st.error(f"{name} 데이터를 불러오는 중 오류 발생: {e}")

    fig.update_layout(
        title="최근 3년간 종가 기준 주가 추이",
        xaxis_title="날짜",
        yaxis_title="주가 (USD)",
        legend_title="기업명",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("왼쪽에서 하나 이상의 기업을 선택하세요.")

