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




import streamlit as st
import pandas as pd
import requests
import time

st.title("기술적 분석 신호 조회")

if st.button("분석 결과 받아오기"):
    with st.spinner("서버에서 데이터 받아오는 중..."):
        try:
            # 1. 첫 번째 데이터 받아오기
            response1 = requests.get("https://port-0-working-task-madmcado69392982.sel4.cloudtype.app/generate_01")
            response1.raise_for_status()
            data1 = response1.json()

            st.success("data1 받아오기 완료")
            st.write("✅ data1 타입:", type(data1))
            st.write("✅ data1 preview:", data1[:3] if isinstance(data1, list) else data1)

            # 2. 대기 시간
            time.sleep(60)

            # 3. 두 번째 데이터 받아오기
            response2 = requests.get("https://port-0-working-task-madmcado69392982.sel4.cloudtype.app/generate_02")
            response2.raise_for_status()
            data2 = response2.json()

            st.success("data2 받아오기 완료")
            st.write("✅ data2 타입:", type(data2))
            st.write("✅ data2 preview:", data2[:3] if isinstance(data2, list) else data2)

            # 4. 데이터 결합 전 체크
            if not isinstance(data1, list) or not isinstance(data2, list):
                st.error("❌ data1 또는 data2가 리스트가 아님. combined_result 생성 불가.")
                st.stop()

            # 5. 데이터 결합
            combined_result = data1 + data2

            if not combined_result:
                st.warning("⚠️ combined_result가 비어있습니다.")
            else:
                # 구조 점검
                for i, item in enumerate(combined_result):
                    if not isinstance(item, dict):
                        st.error(f"[❌] combined_result[{i}]는 dict가 아님: {type(item)}, 값: {item}")
                    else:
                        st.write(f"[✅] combined_result[{i}]는 dict: {item}")

                # 6. DataFrame으로 변환
                try:
                    df = pd.DataFrame(combined_result)
                    st.subheader("📊 분석 결과표")
                    st.dataframe(df)
                except Exception as e:
                    st.error(f"[❌] DataFrame 변환 실패: {e}")

        except Exception as e:
            st.error(f"[❌] 전체 데이터 처리 중 오류 발생: {e}")
