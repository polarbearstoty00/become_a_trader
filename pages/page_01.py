import streamlit as st
import requests
import pandas as pd
import time
import json

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
        "Strong Sell": "🔵적극매도",
        "Sell": "🔵매도",
        "Neutral": "🟢중립",
        "Buy": "🔴매수",
        "Strong Buy": "🔴적극매수"
    }
    return mapping.get(signal, signal)

# 컬럼명 매핑
column_rename_map = {
    "Ticker": "종목코드",
    "Company": "종목명",
    "Tech_Signal": "기술등급",
    "MA_Signal": "이동평균 등급",
    "Final_Summury": "요약"
}

# '요약' 컬럼만 볼드 처리하는 스타일 함수 정의
def bold_summary(val):
    return "font-weight: bold" if val else ""


# 디버깅 출력 여부 설정 : True, False
DEBUG = False

st.title("AI 기술적 분석")

if st.button("분석 요청"):
    with st.spinner("AI에게 기술적 분석을 요청중입니다.", show_time=True):
        try:
            # API 호출 - 첫 번째 요청
            response1 = requests.get("https://port-0-working-task-madmcado69392982.sel4.cloudtype.app/generate_01")
            response1.raise_for_status()
            data1 = response1.json()
            if DEBUG:
                st.write("📋 data1 전체 응답:", data1)

            time.sleep(60)  # 60초 대기

            # API 호출 - 두 번째 요청
            response2 = requests.get("https://port-0-working-task-madmcado69392982.sel4.cloudtype.app/generate_02")
            response2.raise_for_status()
            data2 = response2.json()
            if DEBUG:
                st.write("📋 data2 전체 응답:", data2)

            # 'result' 값 추출
            result1 = data1.get("result")
            result2 = data2.get("result")

            # 'result' 키 존재 여부 확인
            if result1 is None or result2 is None:
                st.error("❌ 'result' 키가 data1 또는 data2에 없습니다.")
                st.stop()

            # 문자열인 경우 JSON 파싱
            if isinstance(result1, str):
                try:
                    result1 = json.loads(result1)
                    if DEBUG:
                        st.write("✅ data1 result 문자열을 리스트로 변환:", result1)
                except json.JSONDecodeError as e:
                    st.error(f"❌ data1 result JSON 파싱 실패: {e}, 값={result1}")
                    st.stop()
            if isinstance(result2, str):
                try:
                    result2 = json.loads(result2)
                    if DEBUG:
                        st.write("✅ data2 result 문자열을 리스트로 변환:", result2)
                except json.JSONDecodeError as e:
                    st.error(f"❌ data2 result JSON 파싱 실패: {e}, 값={result2}")
                    st.stop()

            # 리스트 타입 확인
            if not isinstance(result1, list):
                st.error(f"❌ data1의 'result'는 리스트가 아님: 타입={type(result1)}, 값={result1}")
                st.stop()
            if not isinstance(result2, list):
                st.error(f"❌ data2의 'result'는 리스트가 아님: 타입={type(result2)}, 값={result2}")
                st.stop()

            # 리스트 결합
            combined_result = result1 + result2
            if DEBUG:
                st.write("✅ combined_result 길이:", len(combined_result))

            # 중복된 Ticker 확인
            df_temp = pd.DataFrame(combined_result)
            duplicate_tickers = df_temp[df_temp.duplicated(subset=["Ticker"], keep=False)]
            if not duplicate_tickers.empty:
                st.warning("⚠️ 중복된 Ticker 발견:")
                st.dataframe(duplicate_tickers)

            # combined_result 검사
            if not combined_result:
                st.warning("⚠️ combined_result가 비어있습니다.")
            else:
                for i, item in enumerate(combined_result):
                    if not isinstance(item, dict):
                        st.error(f"[❌] combined_result[{i}]는 딕셔너리가 아님: 타입={type(item)}, 값={item}")
                    else:
                        # 변환할 컬럼 리스트
                        for key in ["Tech_Signal", "MA_Signal", "Final_Summury"]:
                            if key in item:
                                item[key] = translate_signal(item[key])
                        if DEBUG:
                            st.write(f"[✅] combined_result[{i}]는 딕셔너리: {item}")

                # DataFrame 변환
                try:
                    df = pd.DataFrame(combined_result)
                    df.rename(columns=column_rename_map, inplace=True)
                    # 스타일 적용
                    styled_df = df.style.applymap(bold_summary, subset=["요약"])
                    st.write("📊 데이터:")
                    st.dataframe(styled_df, hide_index=True)
                except Exception as e:
                    st.error(f"[❌] DataFrame 변환 실패: {e}")

        except Exception as e:
            st.error(f"데이터 요청 실패: {e}")
