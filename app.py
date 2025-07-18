import streamlit as st
import pyupbit
from pybithumb import Bithumb
import python_bithumb

st.subheader("Become a trader")

# 업비트 티커 정보 불러오기
upbit_tickers = pyupbit.get_tickers()
upbit_krw_tickers = [ticker for ticker in upbit_tickers if ticker.startswith("KRW-")]
st.write("업비트")
st.write(upbit_krw_tickers)

# 빗썸 티커 정보 불러오기
bithumb_tickers = Bithumb.get_tickers()
st.write("빗썸")
st.write(bithumb_tickers)


df = Bithumb.get_candlestick("BTC", chart_intervals="1m")
st.write(df)


df_min = python_bithumb.get_ohlcv("KRW-BTC", interval="minute1", count=200)
st.write("python_bithumb")
st.write(df_min)
