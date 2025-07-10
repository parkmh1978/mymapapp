import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# 1. 시총 기준 Top 10 종목 (2025년 기준, Ticker 포함)
top10_companies = {
    'Apple (AAPL)': 'AAPL',
    'Microsoft (MSFT)': 'MSFT',
    'Alphabet (GOOGL)': 'GOOGL',
    'Amazon (AMZN)': 'AMZN',
    'NVIDIA (NVDA)': 'NVDA',
    'Meta (META)': 'META',
    'Berkshire Hathaway (BRK-B)': 'BRK-B',
    'Eli Lilly (LLY)': 'LLY',
    'Visa (V)': 'V',
    'TSMC (TSM)': 'TSM'
}

# 2. Streamlit UI
st.title("📈 시가총액 Top 10 기업 - 최근 3년 주가 비교")

selected = st.multiselect("기업을 선택하세요 (복수 선택 가능)", options=list(top10_companies.keys()), default=['Apple (AAPL)', 'Microsoft (MSFT)'])

if selected:
    # 3. 데이터 기간 설정
    end_date = datetime.today()
    start_date = end_date - timedelta(days=3*365)

    # 4. 데이터 로딩 및 시각화
    st.write(f"### 최근 3년간 주가 (종가 기준)")

    plt.figure(figsize=(12, 6))
    for name in selected:
        ticker = top10_companies[name]
        data = yf.download(ticker, start=start_date, end=end_date)
        if not data.empty:
            plt.plot(data.index, data['Close'], label=name)
        else:
            st.warning(f"{name} 데이터가 없습니다.")

    plt.legend()
    plt.xlabel("날짜")
    plt.ylabel("주가 ($)")
    plt.title("Top 10 기업 주가 비교 (3년)")
    st.pyplot(plt)
else:
    st.info("기업을 하나 이상 선택해주세요.")
