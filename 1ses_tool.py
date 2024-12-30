import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

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

# サンプルCSVをダウンロードできるようにする
sample_df = pd.DataFrame(sample_data)
sample_csv = sample_df.to_csv(index=False, encoding="shift_jis").encode("shift_jis")
st.sidebar.download_button(
    label="サンプルCSVをダウンロード",
    data=sample_csv,
    file_name="sample_ses_data.csv",
    mime="text/csv",
)

# セッションステートの初期化
if "contracts" not in st.session_state:
    if os.path.exists(CSV_FILE_PATH):=
        st.session_state["contracts"] = pd.read_csv(CSV_FILE_PATH)
    else:
        st.session_state["contracts"] = pd.DataFrame(columns=["エンジニア名", "スキル", "顧客名", "開始日", "終了日", "継続日数", "アラート非表示"])

# CSVファイルアップロード
uploaded_file = st.sidebar.file_uploader("CSVファイルをアップロードしてください", type=["csv"])

# CSVの読み込みとデータ初期化
if uploaded_file is not None:
    try:
        new_data = pd.read_csv(uploaded_file, encoding="shift_jis")
        
        # 必要な列が存在するか確認
        required_columns = ["エンジニア名", "スキル", "顧客名", "開始日", "終了日"]
        if not all(col in new_data.columns for col in required_columns):
            st.error(f"CSVファイルには以下の列が必要です: {', '.join(required_columns)}")
            st.stop()
        
        # 日付変換とエラーチェック
        new_data["開始日"] = pd.to_datetime(new_data["開始日"], format="%Y-%m-%d", errors="coerce")
        new_data["終了日"] = pd.to_datetime(new_data["終了日"], format="%Y-%m-%d", errors="coerce")
        if new_data["開始日"].isna().any() or new_data["終了日"].isna().any():
            st.error("日付が正しくありません。開始日と終了日はYYYY-MM-DD形式で入力してください。")
            st.stop()
        
        # 継続日数の計算
        new_data["継続日数"] = (datetime.now() - new_data["開始日"]).dt.days
        new_data["アラート非表示"] = False
        
        # セッションステートに保存
        st.session_state["contracts"] = new_data
    except Exception as e:
        st.error(f"CSVの読み込み中にエラーが発生しました: {e}")
        st.stop()

# データフレーム取得
contracts = st.session_state["contracts"]

# タブ表示
tab_latest, tab_ongoing, tab_completed = st.tabs(["最新タブ", "継続タブ", "終了タブ"])

# 最新タブ
with tab_latest:
    st.subheader("最新タブ: CSV一覧")
    if not contracts.empty:
        st.dataframe(contracts, use_container_width=True)
    else:
        st.write("CSVデータがアップロードされていません。")

# 継続タブ
with tab_ongoing:
    st.subheader("継続タブ: 継続中の契約")
    ongoing_data = contracts[contracts["終了日"] > datetime.now()]
    if not ongoing_data.empty:
        st.dataframe(ongoing_data, use_container_width=True)
    else:
        st.write("現在継続中の契約はありません。")

# 終了タブ
with tab_completed:
    st.subheader("終了タブ: 継続が終了した契約")
    completed_data = contracts[contracts["終了日"] <= datetime.now()]
    if not completed_data.empty:
        st.dataframe(completed_data, use_container_width=True)
    else:
        st.write("継続が終了した契約はありません。")

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
        st.session_state["contracts"].to_csv(CSV_FILE_PATH, index=False, encoding="utf-8-sig")
        st.success("エンジニア情報を追加し、CSVファイルに保存しました！")        

st.write("契約一覧")
st.dataframe(st.session_state["contracts"], use_container_width=True)
