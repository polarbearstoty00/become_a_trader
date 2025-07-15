import streamlit as st

st.subheader("Become a trader")

# 업비트 티커 정보 불러오기
tickers = pyupbit.get_tickers()
st.write(tickers)
