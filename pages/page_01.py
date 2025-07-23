import streamlit as st
import requests
import pandas as pd
import time

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


# 판단값 변환 함수
def translate_signal(signal):
    mapping = {
        "Strong Sell": "적극매도",
        "Sell": "매도",
        "Neutral": "중립",
        "Buy": "매수",
        "Strong Buy": "적극매수"
    }
    return mapping.get(signal, signal)

# 컬럼명 매핑
column_rename_map = {
    "Ticker": "종목코드",
    "Company": "종목명",
    "Tech_Signal": "기술등급",
    "MA_Signal": "이동평균 등급",
    "Final_Summury": "최종등급"
}




st.title("기술적 분석 신호 조회")

if st.button("분석 결과 받아오기"):
    with st.spinner("서버에서 데이터 받아오는 중..."):
        try:
            # 1. 첫 번째 데이터 요청
            response1 = requests.get("https://port-0-working-task-madmcado69392982.sel4.cloudtype.app/generate_01")
            response1.raise_for_status()
            data1 = response1.json()

            # 2. 60초 대기
            time.sleep(60)

            # 3. 두 번째 데이터 요청
            response2 = requests.get("https://port-0-working-task-madmcado69392982.sel4.cloudtype.app/generate_02")
            response2.raise_for_status()
            data2 = response2.json()

            # 4. data1, data2 결과 출력
            st.write("data1 result", type(data1.get("result")), data1.get("result"))
            st.write("data2 result", type(data2.get("result")), data2.get("result"))

            # 5. combined_result 생성 (예시: 두 리스트 합치기)
            # 실제 데이터 구조에 맞게 조정 필요
            combined_result = []
            if isinstance(data1.get("result"), list) and isinstance(data2.get("result"), list):
                combined_result = data1.get("result") + data2.get("result")
            else:
                st.warning("data1 또는 data2의 'result'가 리스트가 아님. combined_result를 생성할 수 없습니다.")

            st.write("결합된 원시 데이터", combined_result)
            st.write("combined result", type(combined_result), combined_result)

            # 6. combined_result 구조 점검
            if not combined_result:
                st.warning("combined_result가 비어있습니다.")
            else:
                all_dict = True
                for i, item in enumerate(combined_result):
                    if not isinstance(item, dict):
                        all_dict = False
                        st.error(f"[❌] combined_result[{i}]는 dict가 아님: {type(item)}, 값: {item}")
                    else:
                        st.write(f"[✅] combined_result[{i}]는 dict: {item}")

                # 7. DataFrame 변환 시도
                if all_dict:
                    try:
                        df = pd.DataFrame(combined_result)
                        st.success("DataFrame 변환 성공!")
                        st.dataframe(df)
                    except Exception as e:
                        st.error(f"[❌] DataFrame 변환 실패: {e}")

        except Exception as e:
            st.error(f"데이터 요청 실패: {e}")
