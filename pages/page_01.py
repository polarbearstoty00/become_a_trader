import streamlit as st
import requests
import pandas as pd

Upbit_Balance_API_URL = "https://port-0-mywts-investment-flask-m8u0vlaa031d4a0d.sel4.cloudtype.app/upbit_balances"

resp = requests.get(Upbit_Balance_API_URL, timeout=10)
data = resp.json()

st.metric("KRW 잔고", f"{data['krw']:,.0f} 원")

df = pd.DataFrame(data["coins"])
if not df.empty:
    st.table(df)
else:
    st.write("보유 코인이 없습니다.")
