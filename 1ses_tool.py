import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# タイトル
st.title("SES事業継続率管理ツール")

# データ格納用のセッションステートを初期化
if "contracts" not in st.session_state:
    st.session_state["contracts"] = pd.DataFrame(columns=["エンジニア名", "スキル", "顧客名", "開始日", "終了日", "継続中", "アラート非表示"])

# CSVファイルアップロード
uploaded_file = st.sidebar.file_uploader("CSVファイルをアップロードしてください", type=["csv"])

# CSVアップロード処理
if uploaded_file is not None:
    try:
        new_data = pd.read_csv(uploaded_file, encoding="shift_jis")
        new_data["開始日"] = pd.to_datetime(new_data["開始日"], format="%Y-%m-%d", errors="coerce")
        new_data["終了日"] = pd.to_datetime(new_data["終了日"], format="%Y-%m-%d", errors="coerce")
        new_data["継続中"] = new_data["終了日"] > datetime.now()
        new_data["アラート非表示"] = False
        st.session_state["contracts"] = new_data
    except Exception as e:
        st.error("CSVファイルの読み込みに失敗しました。ファイルのフォーマットを確認してください。")

# データフレームを取得
contracts = st.session_state["contracts"]

# 継続率の計算
if len(contracts) > 0:
    total_engineers = len(contracts)
    continued_engineers = contracts["継続中"].sum()
    continuation_rate = (continued_engineers / total_engineers) * 100

    # 継続率の表示
    st.markdown(f"### **現在の継続率: {continuation_rate:.2f}%**")

    # 契約終了日30日前のアラート表示
    st.subheader("終了日が30日以内の契約")
    alert_date = datetime.now() + timedelta(days=30)
    expiring_contracts = contracts[(contracts["終了日"] <= alert_date) & ~contracts["アラート非表示"]]

    if len(expiring_contracts) > 0:
        for index, row in expiring_contracts.iterrows():
            with st.expander(f"エンジニア: {row['エンジニア名']} (終了日: {row['終了日'].date()})"):
                st.write(f"スキル: {row['スキル']}")
                st.write(f"顧客名: {row['顧客名']}")
                if st.checkbox("このアラートを非表示にする", key=f"alert_{index}"):
                    contracts.at[index, "アラート非表示"] = True
    else:
        st.write("30日以内に終了する契約はありません。")

    # データプレビュー
    st.subheader("契約データプレビュー")
    st.dataframe(contracts)

    # データ保存
    updated_csv = contracts.to_csv(index=False, encoding="shift_jis").encode("shift_jis")
    st.download_button(
        label="更新済みデータをダウンロード (CSV)",
        data=updated_csv,
        file_name="updated_ses_data.csv",
        mime="text/csv",
    )
else:
    st.write("契約データがありません。CSVをアップロードしてください。")

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
        new_row = {
            "エンジニア名": engineer_name,
            "スキル": skill,
            "顧客名": client_name,
            "開始日": pd.to_datetime(start_date),
            "終了日": pd.to_datetime(end_date),
            "継続中": pd.to_datetime(end_date) > datetime.now(),
            "アラート非表示": False,
        }
        st.session_state["contracts"] = st.session_state["contracts"].append(new_row, ignore_index=True)
        st.success("エンジニア情報を追加しました。")

# 継続率と前月比のグラフ（オプション）
if len(contracts) > 0:
    st.subheader("継続率の推移グラフ")
    contracts["月"] = contracts["終了日"].dt.to_period("M")
    monthly_data = contracts.groupby("月")["継続中"].sum()
    monthly_continuation_rate = (monthly_data / total_engineers) * 100

    plt.figure(figsize=(10, 5))
    monthly_continuation_rate.plot(kind="line", marker="o")
    plt.title("月別継続率の推移")
    plt.xlabel("月")
    plt.ylabel("継続率 (%)")
    plt.grid(True)
    st.pyplot(plt)
