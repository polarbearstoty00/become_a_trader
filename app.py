import streamlit as st
import pyupbit
from pybithumb import Bithumb

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
