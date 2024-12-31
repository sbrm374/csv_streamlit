import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 파일 저장 디렉토리 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploaded_files")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Streamlit 앱 초기화
st.title("CSVファイル編集ツール")

# CSV 파일 업로드
uploaded_file = st.sidebar.file_uploader("CSVファイルをアップロードしてください", type=["csv"])
if uploaded_file is not None:
    # 업로드된 파일 로컬에 저장
    uploaded_file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(uploaded_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        # CSV 파일 읽기
        df = pd.read_csv(uploaded_file_path, encoding="utf-8")
        st.subheader("アップロードしたCSVファイル")
        st.dataframe(df)

        # 새로운 행 추가 폼
        st.sidebar.subheader("新しい行を追加")
        with st.sidebar.form("add_row_form"):
            new_row = {}
            for col in df.columns:
                new_row[col] = st.text_input(f"{col} 値", value="")
            submitted = st.form_submit_button("追加")

            if submitted:
                # 새로운 행 추가
                new_row_df = pd.DataFrame([new_row])
                df = pd.concat([df, new_row_df], ignore_index=True)

                # CSV 파일 업데이트
                df.to_csv(uploaded_file_path, index=False, encoding="utf-8")
                st.success("新しい行がCSVファイルに追加されました。")

                # 업데이트된 파일 읽기 및 표시
                updated_df = pd.read_csv(uploaded_file_path, encoding="utf-8")
                st.subheader("更新されたCSVファイル")
                st.dataframe(updated_df)

    except Exception as e:
        st.error(f"CSVファイルの処理中にエラーが発生しました: {e}")
else:
    st.info("CSVファイルをアップロードしてください。")
