import streamlit as st
import pandas as pd
import os
from datetime import datetime

# CSV 파일 경로
CSV_FILE_PATH = "updated_ses_data.csv"

# 샘플 데이터 생성
sample_data = {
    "エンジニア名": ["山田太郎", "佐藤花子", "鈴木一郎", "田中次郎"],
    "スキル": ["Python, AWS", "Java, Spring", "React, JavaScript", "C#, .NET"],
    "顧客名": ["顧客A", "顧客B", "顧客C", "顧客D"],
    "開始日": ["2023-01-01", "2023-05-01", "2023-06-01", "2023-02-01"],
    "終了日": ["2023-12-31", "2024-04-30", "2023-12-31", "2024-01-31"],
}

# 샘플 CSV 생성
sample_df = pd.DataFrame(sample_data)
sample_csv = sample_df.to_csv(index=False, encoding="shift_jis").encode("shift_jis")

# CSV 데이터 로드 함수
def load_data():
    if os.path.exists(CSV_FILE_PATH):
        data = pd.read_csv(CSV_FILE_PATH, encoding="shift_jis")
    else:
        data = pd.DataFrame(
            columns=["エンジニア名", "スキル", "顧客名", "開始日", "終了日", "継続日数", "アラート非表示"]
        )
    # 날짜 열 형식 변환
    data["開始日"] = pd.to_datetime(data["開始日"], errors="coerce")
    data["終了日"] = pd.to_datetime(data["終了日"], errors="coerce")
    return data

# CSV 데이터 저장 함수
def save_data(dataframe):
    dataframe.to_csv(CSV_FILE_PATH, index=False, encoding="shift_jis")

# Streamlit 앱 초기화
st.title("SES事業継続率管理ツール")

# 샘플 CSV 다운로드 버튼
st.sidebar.download_button(
    label="サンプルCSVをダウンロード",
    data=sample_csv,
    file_name="sample_ses_data.csv",
    mime="text/csv",
)

# 데이터 로드
if "contracts" not in st.session_state:
    st.session_state["contracts"] = load_data()

contracts = st.session_state["contracts"]

# CSV 업로드 처리
uploaded_file = st.sidebar.file_uploader("CSVファイルをアップロードしてください", type=["csv"])
if uploaded_file is not None:
    try:
        new_data = pd.read_csv(uploaded_file, encoding="shift_jis")
        required_columns = ["エンジニア名", "スキル", "顧客名", "開始日", "終了日"]
        if not all(col in new_data.columns for col in required_columns):
            st.error(f"CSVファイルには以下の列が必要です: {', '.join(required_columns)}")
        else:
            # 날짜 변환 및 검증
            new_data["開始日"] = pd.to_datetime(new_data["開始日"], errors="coerce")
            new_data["終了日"] = pd.to_datetime(new_data["終了日"], errors="coerce")
            new_data["継続日数"] = (datetime.now() - new_data["開始日"]).dt.days
            new_data["アラート非表示"] = False
            st.session_state["contracts"] = pd.concat([contracts, new_data], ignore_index=True)
            save_data(st.session_state["contracts"])
            st.experimental_set_query_params(reload="true")  # 화면 새로고침
    except Exception as e:
        st.error(f"CSV読み込み中にエラーが発生しました: {e}")

# 데이터 표시
tab_latest, tab_ongoing, tab_completed = st.tabs(["最新タブ", "継続タブ", "終了タブ"])

with tab_latest:
    st.subheader("最新タブ: CSV一覧")
    st.dataframe(contracts, use_container_width=True)

with tab_ongoing:
    st.subheader("継続タブ: 継続中の契約")
    ongoing_data = contracts[contracts["終了日"] > datetime.now()]
    st.dataframe(ongoing_data, use_container_width=True)

with tab_completed:
    st.subheader("終了タブ: 継続が終了した契約")
    completed_data = contracts[contracts["終了日"] <= datetime.now()]
    st.dataframe(completed_data, use_container_width=True)

# 엔지니어 정보 추가 폼
st.sidebar.subheader("エンジニア情報を追加")
with st.sidebar.form("add_engineer_form"):
    engineer_name = st.text_input("エンジニア名")
    skill = st.text_input("スキル")
    client_name = st.text_input("顧客名")
    start_date = st.date_input("開始日")
    end_date = st.date_input("終了日")
    submitted = st.form_submit_button("追加")

    if submitted:
        new_row = pd.DataFrame([{
            "エンジニア名": engineer_name,
            "スキル": skill,
            "顧客名": client_name,
            "開始日": pd.to_datetime(start_date),
            "終了日": pd.to_datetime(end_date),
            "継続日数": (datetime.now() - pd.to_datetime(start_date)).days,
            "アラート非表示": False,
        }])
        st.session_state["contracts"] = pd.concat([contracts, new_row], ignore_index=True)
        save_data(st.session_state["contracts"])
        st.success("エンジニア情報が追加されました。")
        st.experimental_set_query_params(reload="true")  # 화면 새로고침
