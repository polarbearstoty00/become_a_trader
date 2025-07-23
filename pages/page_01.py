import streamlit as st
import requests
import pandas as pd

Upbit_Balance_API_URL = "https://port-0-mywts-investment-flask-m8u0vlaa031d4a0d.sel4.cloudtype.app/upbit_balances"

def fetch_upbit_balances():
    try:
        resp = requests.get(Upbit_Balance_API_URL)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"잔고 조회 실패: {e}")
        return None

data = fetch_upbit_balances()

if data:
    st.metric("KRW 잔고", f"{data['krw']:,.0f} 원")
    df = pd.DataFrame(data.get("coins", []))
    if not df.empty:
        st.table(df)
    else:
        st.write("보유 코인이 없습니다.")
else:
    st.write("잔고 데이터를 불러올 수 없습니다.")



st.title("기술적 분석 신호 조회")

if st.button("분석 결과 받아오기"):
    with st.spinner("서버에서 데이터 받아오는 중..."):
        try:
            # 첫 번째 라우터 호출
            response1 = requests.get("https://port-0-working-task-madmcado69392982.sel4.cloudtype.app/generate_01")
            response1.raise_for_status()
            data1 = response1.json()

            # 두 번째 라우터 호출 (data1을 활용할 수도 있음)
            response2 = requests.get("https://port-0-working-task-madmcado69392982.sel4.cloudtype.app/generate_02")
            response2.raise_for_status()
            data2 = response2.json()

            # 결과 출력
            if data1 and data2:
                st.subheader("1단계 결과")
                st.json(data1["result"])
                st.subheader("2단계 결과")
                st.json(data2["result"])
            else:
                st.write("데이터가 부족합니다.")
        except Exception as e:
            st.error(f"데이터 요청 실패: {e}")
