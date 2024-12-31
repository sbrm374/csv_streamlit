import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 절대 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploaded_files")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Streamlit 앱 초기화
st.title("SES事業継続率管理ツール")

# CSV 업로드
uploaded_file = st.sidebar.file_uploader("CSVファイルをアップロードしてください", type=["csv"])
if uploaded_file is not None:
    # 업로드된 파일 로컬에 저장
    uploaded_file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(uploaded_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        # CSV 읽기
        df = pd.read_csv(uploaded_file_path, encoding="utf-8")
        st.session_state["contracts"] = df  # 세션에 저장
        st.success(f"アップロードしたファイル: {uploaded_file_path} を読み込みました。")
    except Exception as e:
        st.error(f"CSVファイルの読み込み中にエラーが発生しました: {e}")

# 데이터 로드 (업로드된 파일이 없는 경우 초기화)
if "contracts" not in st.session_state:
    st.session_state["contracts"] = pd.DataFrame(
        columns=["エンジニア名", "スキル", "顧客名", "開始日", "終了日", "継続日数", "アラート非表示"]
    )

# 데이터 표시
st.subheader("現在の契約一覧")
st.dataframe(st.session_state["contracts"], use_container_width=True)

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

        # 새로운 행 추가 및 업데이트
        st.session_state["contracts"] = pd.concat([st.session_state["contracts"], new_row], ignore_index=True)
        st.session_state["contracts"].to_csv(uploaded_file_path, index=False, encoding="utf-8")

        # 업데이트된 파일 다시 읽기
        updated_df = pd.read_csv(uploaded_file_path, encoding="utf-8")
        st.session_state["contracts"] = updated_df  # 세션 상태 업데이트

        st.success(f"新しいデータが {uploaded_file_path} に保存されました。")
        st.subheader("更新されたCSVファイル")
        st.dataframe(updated_df)  # 화면에 업데이트된 데이터 표시
