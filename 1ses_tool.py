import streamlit as st
import pandas as pd
from datetime import datetime

# タイトル
st.title("SES事業継続率管理ツール")

# サンプルCSVデータ
sample_data = {
    "エンジニア名": ["山田太郎", "佐藤花子", "鈴木一郎", "田中次郎"],
    "スキル": ["Python, AWS", "Java, Spring", "React, JavaScript", "C#, .NET"],
    "顧客名": ["顧客A", "顧客B", "顧客C", "顧客D"],
    "開始日": ["2023-01-01", "2023-05-01", "2023-06-01", "2023-02-01"],
    "終了日": ["2023-12-31", "2024-04-30", "2023-12-31", "2024-01-31"],
}

# セッションステートの初期化
if "contracts" not in st.session_state:
    st.session_state["contracts"] = pd.DataFrame(
        sample_data | {
            "開始日": pd.to_datetime(sample_data["開始日"]),
            "終了日": pd.to_datetime(sample_data["終了日"]),
            "継続日数": [
                (datetime.now() - pd.to_datetime(start)).days
                for start in sample_data["開始日"]
            ],
            "アラート非表示": [False] * len(sample_data["エンジニア名"]),
        }
    )

# タブ表示
tab_latest, tab_ongoing, tab_completed = st.tabs(["最新タブ", "継続タブ", "終了タブ"])

# 最新タブ
with tab_latest:
    st.subheader("最新タブ: CSV一覧")
    st.dataframe(st.session_state["contracts"], use_container_width=True)

# 継続タブ
with tab_ongoing:
    st.subheader("継続タブ: 継続中の契約")
    ongoing_data = st.session_state["contracts"][st.session_state["contracts"]["終了日"] > datetime.now()]
    st.dataframe(ongoing_data, use_container_width=True)

# 終了タブ
with tab_completed:
    st.subheader("終了タブ: 継続が終了した契約")
    completed_data = st.session_state["contracts"][st.session_state["contracts"]["終了日"] <= datetime.now()]
    st.dataframe(completed_data, use_container_width=True)

# エンジニア情報追加フォーム
st.sidebar.subheader("エンジニア情報を追加")
with st.sidebar.form("add_engineer_form"):
    engineer_name = st.text_input("エンジニア名")
    skill = st.text_input("スキル")
    client_name = st.text_input("顧客名")
    start_date = st.date_input("開始日")
    end_date = st.date_input("終了日")
    submitted = st.form_submit_button("追加")

    if submitted:
        # 새 행 생성
        new_row = {
            "エンジニア名": engineer_name,
            "スキル": skill,
            "顧客名": client_name,
            "開始日": pd.to_datetime(start_date),
            "終了日": pd.to_datetime(end_date),
            "継続日数": (datetime.now() - pd.to_datetime(start_date)).days,
            "アラート非表示": True,
        }

        # 세션 상태의 데이터프레임에 행 추가
        st.session_state["contracts"] = pd.concat(
            [st.session_state["contracts"], pd.DataFrame([new_row])], ignore_index=True
        )

        # 성공 메시지
        st.success("エンジニア情報を追加しました。")
        st.rerun()
