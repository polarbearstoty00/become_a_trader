import pandas as pd
import pandas_ta as ta
from pykrx import stock
from datetime import datetime, timedelta
import pytz
import json
import time
from Task_module_01.stock_tickers import ticker_dict

# 날짜 관련 함수
def get_kst_startdate_str(days_ago=0):
    kst = pytz.timezone("Asia/Seoul")
    target_date = datetime.now(kst) - timedelta(days=days_ago)
    return target_date.strftime("%Y%m%d")

def get_kst_today_str():
    kst = pytz.timezone("Asia/Seoul")
    return datetime.now(kst).strftime("%Y%m%d")

start_date = get_kst_startdate_str(350)
today = get_kst_today_str()

# 기술적 지표 계산 함수
def analyze_all_signals(df):
    result = df.copy()

    result["RSI"] = ta.rsi(result["종가"], length=14)
    macd = ta.macd(result["종가"], fast=12, slow=26, signal=9)
    result["MACD"] = macd["MACD_12_26_9"]
    result["MACD_signal"] = macd["MACDs_12_26_9"]
    result["MACD_hist"] = macd["MACDh_12_26_9"]
    stoch = ta.stoch(result["고가"], result["저가"], result["종가"])
    result["STOCH_%K"] = stoch["STOCHk_14_3_3"]
    result["STOCH_%D"] = stoch["STOCHd_14_3_3"]
    result["CCI"] = ta.cci(result["고가"], result["저가"], result["종가"], length=20)
    result["MOM"] = ta.mom(result["종가"], length=10)
    result["ADX"] = ta.adx(result["고가"], result["저가"], result["종가"], length=14)["ADX_14"]

    for length in [5, 10, 20, 50, 100, 200]:
        result[f"SMA{length}"] = ta.sma(result["종가"], length=length)
        result[f"EMA{length}"] = ta.ema(result["종가"], length=length)

    def rsi_sig(x): return "Buy" if x <= 30 else "Sell" if x >= 70 else "Neutral"
    def macd_sig(row): return "Buy" if row["MACD"] > row["MACD_signal"] else "Sell" if row["MACD"] < row["MACD_signal"] else "Neutral"
    def stoch_sig(row): return "Buy" if row["STOCH_%K"] < 20 else "Sell" if row["STOCH_%K"] > 80 else "Neutral"
    def cci_sig(x): return "Buy" if x < -100 else "Sell" if x > 100 else "Neutral"
    def mom_sig(x): return "Buy" if x > 0 else "Sell" if x < 0 else "Neutral"
    def adx_sig(x): return "Buy" if x > 25 else "Neutral"

    def ma_sig(row, fast, slow):
        f = row[f"SMA{fast}"]
        s = row[f"SMA{slow}"]
        if pd.isna(f) or pd.isna(s):
            return "Neutral"
        return "Buy" if f > s else "Sell" if f < s else "Neutral"

    result["RSI_signal"] = result["RSI"].apply(rsi_sig)
    result["MACD_signal_decision"] = result.apply(macd_sig, axis=1)
    result["STOCH_signal"] = result.apply(stoch_sig, axis=1)
    result["CCI_signal"] = result["CCI"].apply(cci_sig)
    result["MOM_signal"] = result["MOM"].apply(mom_sig)
    result["ADX_signal"] = result["ADX"].apply(adx_sig)
    result["MA_cross_signal"] = result.apply(lambda r: ma_sig(r, 20, 200), axis=1)

    def signal_to_score(sig):
        return 1 if sig == "Buy" else -1 if sig == "Sell" else 0

    signal_cols = [
        "RSI_signal", "MACD_signal_decision", "STOCH_signal",
        "CCI_signal", "MOM_signal", "ADX_signal", "MA_cross_signal"
    ]

    for col in signal_cols:
        result[col] = result[col].map(signal_to_score)

    result["Total_Score"] = result[signal_cols].sum(axis=1)

    def final_decision(score):
        if score >= 5:
            return "Strong Buy"
        elif score >= 3:
            return "Buy"
        elif score <= -5:
            return "Strong Sell"
        elif score <= -3:
            return "Sell"
        else:
            return "Neutral"

    result["Final_Summary"] = result["Total_Score"].apply(final_decision)

    return result

# 이동평균 요약 함수
def summarize_moving_averages_with_summary(df):
    latest = df.iloc[-1]
    close = latest["종가"]

    rows = []
    total_score = 0
    for length in [5, 10, 20, 50, 100, 200]:
        sma = latest[f"SMA{length}"]
        ema = latest[f"EMA{length}"]

        sma_signal = "매수" if close > sma else "매도"
        ema_signal = "매수" if close > ema else "매도"

        score = 0
        score += 1 if sma_signal == "매수" else -1
        score += 1 if ema_signal == "매수" else -1
        total_score += score

        rows.append({
            "기간": f"MA{length}",
            "단순 평균": f"{sma:.4f}",
            "단순 신호": sma_signal,
            "지수 평균": f"{ema:.4f}",
            "지수 신호": ema_signal
        })

    if total_score >= 8:
        final = "Strong Buy"
    elif total_score >= 4:
        final = "Buy"
    elif total_score <= -8:
        final = "Strong Sell"
    elif total_score <= -4:
        final = "Sell"
    else:
        final = "Neutral"

    df_summary = pd.DataFrame(rows)
    df_summary.loc["최종 판단"] = ["", "", "", "", final]

    return df_summary

# 신호 점수 매핑 함수
def signal_to_score(sig):
    mapping = {
        "Strong Buy": 3,
        "Buy": 2,
        "Neutral": 0,
        "Sell": -2,
        "Strong Sell": -3
    }
    return mapping.get(sig, 0)

# 최종 판단 함수
def final_overall_decision(score):
    if score >= 4:
        return "Strong Buy"
    elif score >= 2:
        return "Buy"
    elif score <= -4:
        return "Strong Sell"
    elif score <= -2:
        return "Sell"
    else:
        return "Neutral"

# 다중 티커 분석 함수
def analyze_multiple_tickers(tickers, start_date, end_date):
    results = []
    for ticker in tickers:
        df = stock.get_market_ohlcv(start_date, end_date, ticker)
        analyzed_df = analyze_all_signals(df)
        summary_df = summarize_moving_averages_with_summary(analyzed_df)

        tech_final_summary = analyzed_df["Final_Summary"].iloc[-1]
        ma_final_summary = summary_df.iloc[-1, -1]

        tech_score = signal_to_score(tech_final_summary)
        ma_score = signal_to_score(ma_final_summary)
        total_score = tech_score + ma_score
        final_decision = final_overall_decision(total_score)

        results.append({
            "Ticker": ticker,
            "Detailed": analyzed_df,
            "Summary": summary_df,
            "Tech_Signal": tech_final_summary,
            "MA_Signal": ma_final_summary,
            "Final_Decision": final_decision
        })
        time.sleep(0.3)

    return results

# 데이터 클린 처리 함수
def clean_result_data(results):
    keys_to_remove = ["시가", "고가", "저가", "종가", "거래량", "등락률"]

    for item in results:
        detailed = item.get("Detailed")

        if isinstance(detailed, str):
            df_detailed = pd.read_json(detailed)
        elif isinstance(detailed, pd.DataFrame):
            df_detailed = detailed
        else:
            df_detailed = None

        if df_detailed is not None:
            if '날짜' in df_detailed.columns:
                df_detailed['날짜'] = df_detailed['날짜'].astype(str)
            df_detailed = df_detailed.drop(columns=[col for col in keys_to_remove if col in df_detailed.columns], errors="ignore")
            latest_row = df_detailed.tail(1).reset_index(drop=True)
            item["Detailed"] = latest_row.to_dict(orient="records")

        summary = item.get("Summary")

        if isinstance(summary, str):
            df_summary = pd.read_json(summary)
        elif isinstance(summary, pd.DataFrame):
            df_summary = summary
        else:
            df_summary = None

        if df_summary is not None:
            latest_summary = df_summary.tail(1).reset_index(drop=True)
            item["Summary"] = latest_summary.to_dict(orient="records")

    return results

# JSON 변환 함수
def results_to_json(results):
    json_ready = []

    for res in results:
        try:
            detailed_data = res["Detailed"]
            if isinstance(detailed_data, pd.DataFrame):
                latest_row = detailed_data.tail(1).reset_index()
                latest_row['날짜'] = latest_row['날짜'].astype(str)
                res["Detailed"] = latest_row.to_dict(orient="records")
            elif isinstance(detailed_data, list):
                res["Detailed"] = [detailed_data[-1]]
            else:
                res["Detailed"] = []

            json_ready.append(res)

        except Exception as e:
            print(f"[ERROR] Failed to process result for {res.get('Ticker')}: {e}")
            continue

    return json_ready

if __name__ == "__main__":
    tickers = list(ticker_dict.keys())

    # 1. 분석 + 수집
    results = analyze_multiple_tickers(tickers, start_date, today)

    # 2. 데이터 클린업
    cleaned_results = clean_result_data(results)

    # 3. JSON 변환
    json_output_str = json.dumps(cleaned_results, ensure_ascii=False, indent=2)

    # 4. 요약 정보만 추출
    final_output = []
    for item in cleaned_results:
        ticker = item.get("Ticker")
        Company_Name = ticker_dict.get(ticker, "알 수 없음")

        final_output.append({
            "Ticker": ticker,
            "Company": Company_Name,
            "Tech_Signal": item.get("Tech_Signal"),
            "MA_Signal": item.get("MA_Signal"),
            "Final_Decision": item.get("Final_Decision")
        })

    # 5. 최종 JSON 문자열
    summary_json_str = json.dumps(final_output, ensure_ascii=False, indent=2)
