import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="주요 기업 주가 현황", # 페이지 제목 변경
    page_icon="📈",
    layout="wide"
)

# 분석할 기업 목록 (시총 Top 10 및 추가 기업 포함)
COMPANIES_TO_ANALYZE = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Alphabet": "GOOGL",
    "Amazon": "AMZN",
    "NVIDIA": "NVDA",
    "Tesla": "TSLA",
    "Meta": "META",
    "Berkshire Hathaway": "BRK-B",
    "Taiwan Semiconductor": "TSM",
    "Visa": "V",
    # 한국 기업 추가
    "Samsung Electronics": "005930.KS", # 삼성전자 (KRX)
    "Hyundai Motor": "005380.KS",     # 현대자동차 (KRX)
    # 차세대 AI 관련 기업 (예시 - 대표적인 AI 관련 기업들)
    "Advanced Micro Devices": "AMD",  # AI 칩
    "Broadcom": "AVGO",               # AI 인프라
    "Palantir Technologies": "PLTR",  # 데이터 분석 및 AI
    # 양자컴퓨터 관련 기업 (예시 - 주목받는 양자컴퓨팅 관련 기업들)
    "IonQ": "IONQ",                   # 양자 컴퓨팅 하드웨어 및 소프트웨어
    "Rigetti Computing": "RGTI",      # 양자 컴퓨팅 하드웨어
    "Honeywell International": "HON"  # 양자 솔루션 연구 개발 포함
}

@st.cache_data
def get_exchange_rate_data(period="3y"):
    """KRW/USD 환율 데이터를 가져오는 함수"""
    try:
        krw_usd = yf.Ticker("KRW=X")
        # yfinance의 history 함수는 start, end 날짜를 지정하는 것이 더 정확할 수 있습니다.
        # period를 사용하면 최근 며칠간의 데이터가 누락될 수 있습니다.
        # 여기서는 period를 그대로 사용하되, 실제 앱에서는 start/end를 고려할 수 있습니다.
        exchange_data = krw_usd.history(period=period)
        if not exchange_data.empty:
            # 환율 데이터의 'Close' 컬럼만 사용
            return exchange_data['Close'].rename('KRW_USD_Rate')
        return None
    except Exception as e:
        st.error(f"KRW/USD 환율 데이터를 가져오는 중 오류 발생: {e}")
        return None

@st.cache_data
def get_stock_data(ticker, period="3y"):
    """주식 데이터를 가져오는 함수 (한국 주식은 환율 변환 포함)"""
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period)

        if data.empty:
            return None

        # 한국 주식인 경우 (티커가 .KS로 끝나는 경우) 환율 변환 적용
        if ticker.endswith(".KS"):
            exchange_rates = get_exchange_rate_data(period)
            if exchange_rates is not None and not exchange_rates.empty:
                # 주식 데이터 인덱스에 맞춰 환율 데이터 정렬 및 누락된 값 채우기 (이전 값으로)
                # 이 과정은 주식 거래일과 환율 제공일이 다를 수 있기 때문에 중요합니다.
                aligned_exchange_rates = exchange_rates.reindex(data.index, method='ffill')

                # 환율 데이터가 없는 날짜가 있다면 해당 주식 데이터는 제외
                data = data.dropna(subset=['Close']) # 주가 데이터에 NaN이 없도록 확인
                aligned_exchange_rates = aligned_exchange_rates.dropna() # 환율 데이터에 NaN이 없도록 확인

                # 두 데이터프레임의 인덱스를 교집합으로 맞춰서 정확한 매칭
                common_index = data.index.intersection(aligned_exchange_rates.index)
                data = data.loc[common_index]
                aligned_exchange_rates = aligned_exchange_rates.loc[common_index]

                if not data.empty and not aligned_exchange_rates.empty:
                    # KRW 가격을 USD로 변환
                    for col in ['Open', 'High', 'Low', 'Close']:
                        data[col] = data[col] / aligned_exchange_rates
                    # 거래량은 통화 변환의 대상이 아니므로 그대로 둡니다.
                else:
                    st.warning(f"{ticker}에 대한 환율 데이터가 충분하지 않아 변환을 건너뛰었습니다.")
            else:
                st.warning(f"KRW/USD 환율 데이터를 가져올 수 없어 {ticker}의 주가가 변환되지 않았습니다.")
        return data
    except Exception as e:
        st.error(f"{ticker} 데이터를 가져오는 중 오류 발생: {e}")
        return None

@st.cache_data
def get_company_info(ticker):
    """회사 정보를 가져오는 함수 (한국 기업은 환율 변환 포함)"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        current_price = info.get('currentPrice', 0)
        market_cap = info.get('marketCap', 0)

        # 한국 주식인 경우 현재 가격과 시가총액을 USD로 변환
        if ticker.endswith(".KS"):
            krw_usd = yf.Ticker("KRW=X")
            # 최신 환율을 가져오기 위해 "1d" 기간 사용
            exchange_data = krw_usd.history(period="1d")
            if not exchange_data.empty:
                latest_rate = exchange_data['Close'].iloc[-1]
                if latest_rate > 0:
                    current_price = current_price / latest_rate
                    market_cap = market_cap / latest_rate
                else:
                    st.warning(f"유효한 최신 KRW/USD 환율(0이하)을 가져올 수 없어 {ticker}의 가격이 변환되지 않았습니다.")
            else:
                st.warning(f"최신 KRW/USD 환율 데이터를 가져올 수 없어 {ticker}의 가격이 변환되지 않았습니다.")

        return {
            'name': info.get('longName', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'marketCap': market_cap,
            'currentPrice': current_price
        }
    except Exception as e:
        st.error(f"{ticker} 회사 정보를 가져오는 중 오류 발생: {e}")
        return {'name': 'N/A', 'sector': 'N/A', 'marketCap': 0, 'currentPrice': 0}

def format_market_cap(market_cap):
    """시가총액을 읽기 쉬운 형태로 변환"""
    if market_cap >= 1e12:
        return f"${market_cap/1e12:.2f}T"
    elif market_cap >= 1e9:
        return f"${market_cap/1e9:.2f}B"
    elif market_cap >= 1e6:
        return f"${market_cap/1e6:.2f}M"
    else:
        return f"${market_cap:,.0f}"

def main():
    st.title("📈 주요 기업 주가 현황") # 제목 변경
    st.markdown("최근 주가 데이터를 확인해보세요.") # 설명 변경

    # 사이드바에서 기업 선택
    st.sidebar.header("기업 선택")
    selected_companies = st.sidebar.multiselect(
        "분석할 기업을 선택하세요:",
        options=list(COMPANIES_TO_ANALYZE.keys()), # 변경된 딕셔너리 사용
        default=["Apple", "Samsung Electronics", "NVIDIA"]  # 기본 선택 기업 조정
    )

    if not selected_companies:
        st.warning("최소 하나의 기업을 선택해주세요.")
        return

    # 기간 선택
    period_options = {
        "1년": "1y",
        "2년": "2y",
        "3년": "3y",
        "5년": "5y",
        "10년": "10y", # 10년 옵션 추가
        "최대": "max"  # 최대 옵션 추가
    }

    selected_period = st.sidebar.selectbox(
        "기간 선택:",
        options=list(period_options.keys()),
        index=2  # 기본값: 3년
    )

    # 차트 타입 선택
    chart_type = st.sidebar.radio(
        "차트 타입:",
        ["라인 차트", "캔들스틱 차트"]
    )

    # 데이터 로딩
    with st.spinner("데이터를 불러오는 중..."):
        stock_data = {}
        company_info = {}

        for company in selected_companies:
            ticker = COMPANIES_TO_ANALYZE[company] # 변경된 딕셔너리 사용
            data = get_stock_data(ticker, period_options[selected_period])
            info = get_company_info(ticker)

            if data is not None and not data.empty:
                stock_data[company] = data
                company_info[company] = info

    if not stock_data:
        st.error("선택한 기업의 데이터를 불러올 수 없습니다.")
        return

    # 회사 정보 표시
    st.header("📊 선택된 기업 정보")

    cols = st.columns(len(selected_companies))
    for i, company in enumerate(selected_companies):
        if company in company_info:
            info = company_info[company]
            with cols[i]:
                st.metric(
                    label=f"{company}",
                    value=f"${info['currentPrice']:.2f}",
                    delta=f"시총: {format_market_cap(info['marketCap'])}"
                )
                st.caption(f"섹터: {info['sector']}")

    # 주가 차트
    st.header("📈 주가 차트")

    if chart_type == "라인 차트":
        # 라인 차트
        fig = go.Figure()

        colors = px.colors.qualitative.Set1[:len(selected_companies)]

        for i, (company, data) in enumerate(stock_data.items()):
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['Close'],
                mode='lines',
                name=company,
                line=dict(color=colors[i], width=2),
                hovertemplate=f'<b>{company}</b><br>' +
                               'Date: %{x}<br>' +
                               'Price: $%{y:.2f}<br>' +
                               '<extra></extra>'
            ))

        fig.update_layout(
            title=f"주가 추이 - {selected_period}",
            xaxis_title="날짜",
            yaxis_title="주가 (USD)",
            hovermode='x unified',
            height=600,
            template='plotly_white'
        )

    else:
        # 캔들스틱 차트 (단일 기업만)
        if len(selected_companies) > 1:
            st.info("캔들스틱 차트는 한 번에 하나의 기업만 표시됩니다. 첫 번째 선택된 기업을 표시합니다.")

        company = selected_companies[0]
        data = stock_data[company]

        fig = go.Figure(data=go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name=company
        ))

        fig.update_layout(
            title=f"{company} 캔들스틱 차트 - {selected_period}",
            xaxis_title="날짜",
            yaxis_title="주가 (USD)",
            height=600,
            template='plotly_white'
        )

    st.plotly_chart(fig, use_container_width=True)

    # 성과 비교 테이블
    st.header("📊 성과 비교")

    performance_data = []
    for company, data in stock_data.items():
        if len(data) > 0:
            start_price = data['Close'].iloc[0]
            end_price = data['Close'].iloc[-1]
            total_return = ((end_price - start_price) / start_price) * 100

            # 최고가, 최저가
            max_price = data['Close'].max()
            min_price = data['Close'].min()

            performance_data.append({
                '기업': company,
                '시작 가격': f"${start_price:.2f}",
                '현재 가격': f"${end_price:.2f}",
                '총 수익률': f"{total_return:.2f}%",
                '최고가': f"${max_price:.2f}",
                '최저가': f"${min_price:.2f}",
                '변동성': f"{data['Close'].std():.2f}"
            })

    if performance_data:
        df_performance = pd.DataFrame(performance_data)
        st.dataframe(df_performance, use_container_width=True)

    # 거래량 차트
    st.header("📊 거래량 분석")

    fig_volume = go.Figure()

    for i, (company, data) in enumerate(stock_data.items()):
        fig_volume.add_trace(go.Scatter(
            x=data.index,
            y=data['Volume'],
            mode='lines',
            name=company,
            line=dict(color=colors[i % len(colors)], width=2),
            hovertemplate=f'<b>{company}</b><br>' +
                               'Date: %{x}<br>' +
                               'Volume: %{y:,.0f}<br>' +
                               '<extra></extra>'
        ))

    fig_volume.update_layout(
        title=f"거래량 추이 - {selected_period}",
        xaxis_title="날짜",
        yaxis_title="거래량",
        hovermode='x unified',
        height=400,
        template='plotly_white'
    )

    st.plotly_chart(fig_volume, use_container_width=True)

    # 추가 정보
    st.header("ℹ️ 추가 정보")
    st.info("""
    **데이터 소스**: Yahoo Finance

    **주의사항**:
    - 이 데이터는 투자 조언이 아닙니다.
    - 실제 투자 전에 전문가와 상담하세요.
    - 과거 성과가 미래 성과를 보장하지 않습니다.
    """)

if __name__ == "__main__":
    main()
