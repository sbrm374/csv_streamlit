import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 절대 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploaded_files")
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
sample_csv = sample_df.to_csv(index=False, encoding="utf-8").encode("utf-8")

# Streamlit 앱 초기화
st.title("SES事業継続率管理ツール")

# 샘플 CSV 다운로드 버튼
st.sidebar.download_button(
    label="サンプルCSVをダウンロード",
    data=sample_csv,
    file_name="sample_ses_data.csv",
    mime="text/csv",
)

# CSV 업로드 처리
uploaded_file = st.sidebar.file_uploader("CSVファイルをアップロードしてください", type=["csv"])
if uploaded_file is not None:
    # 업로드된 파일을 로컬 디렉토리에 저장
    uploaded_file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(uploaded_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    try:
        # 업로드된 CSV 읽기
        st.session_state["contracts"] = pd.read_csv(uploaded_file_path, encoding="utf-8")
        st.success(f"アップロードしたファイル: {uploaded_file.name} を読み込みました。")
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
        st.session_state["contracts"] = pd.concat([st.session_state["contracts"], new_row], ignore_index=True)

        # 로컬 파일에 저장
        if uploaded_file_path:
            try:
                st.session_state["contracts"].to_csv(uploaded_file_path, index=False, encoding="utf-8")
                st.success(f"新しいデータが {uploaded_file_path} に保存されました。")

                # 저장된 파일 내용 확인
                with open(uploaded_file_path, "r", encoding="utf-8") as file:
                    file_content = file.read()
                    st.text_area("保存されたCSVの内容を確認", file_content, height=200)

            except Exception as e:
                st.error(f"CSVファイルの保存中にエラーが発生しました: {e}")
        else:
            st.error("アップロードしたCSVファイルが見つかりません。")
