import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
import matplotlib.font_manager as fm
import io
import os
import plotly.express as px

# フォント設定
font_path = "./fonts/NotoSansJP-Regular.otf"
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False  # マイナス記号が崩れないように設定

# タイトル
st.title("SES事業継続率管理ツール")

# サンプルデータ
sample_data = {
    "エンジニア名": ["山田太郎", "佐藤花子", "鈴木一郎", "田中次郎"],
    "スキル": ["Python, AWS", "Java, Spring", "React, JavaScript", "C#, .NET"],
    "顧客名": ["顧客A", "顧客B", "顧客C", "顧客D"],
    "開始日": ["2023-01-01", "2023-05-01", "2023-06-01", "2023-02-01"],
    "終了日": ["2023-12-31", "2024-04-30", "2023-12-31", "2024-01-31"],
}

# サンプルCSVをダウンロード可能にする
sample_df = pd.DataFrame(sample_data)
sample_csv = sample_df.to_csv(index=False, encoding="shift_jis").encode("shift_jis")
st.sidebar.download_button(
    label="サンプルCSVをダウンロード",
    data=sample_csv,
    file_name="sample_ses_data.csv",
    mime="text/csv",
)

# CSVファイルをアップロード
uploaded_file = st.sidebar.file_uploader("CSVファイルをアップロードしてください", type=["csv"])

# セッション 상태를 초기화
if "contracts" not in st.session_state:
    st.session_state["contracts"] = pd.DataFrame()

if "render_flag" not in st.session_state:
    st.session_state["render_flag"] = False  # レンダリング制御フラグの初期化

# アップロードされたファイルを処理
if uploaded_file is not None:
    try:
        # CSVデータを読み込む
        uploaded_data = pd.read_csv(uploaded_file, encoding="shift_jis")
        uploaded_data["開始日"] = pd.to_datetime(uploaded_data["開始日"])
        uploaded_data["終了日"] = pd.to_datetime(uploaded_data["終了日"])

        # "削除" 列を追加
        uploaded_data["削除"] = False
        
        uploaded_data["継続日数"] = [
            (datetime.now() - start).days for start in uploaded_data["開始日"]
        ]
        uploaded_data["アラート非表示"] = [False] * len(uploaded_data)

        # すでにアップロードされたデータか確認
        if "uploaded_flag" not in st.session_state or not st.session_state["uploaded_flag"]:
            # アップロードされたデータを既存データにマージ
            st.session_state["contracts"] = pd.concat(
                [st.session_state["contracts"], uploaded_data], ignore_index=True
            )
            st.session_state["uploaded_flag"] = True  # アップロード完了フラグを設定
            st.success("CSVファイルがアップロードされました。")
    except Exception as e:
        st.error(f"アップロードされたファイルの処理中にエラーが発生しました: {e}")

# データ表示と削除機能
if not st.session_state["contracts"].empty:
    st.subheader("アップロードされたデータ")

    # Streamlit データエディタでデータを表示
    edited_df = st.experimental_data_editor(
        st.session_state["contracts"], num_rows="dynamic", use_container_width=True
    )

    # "削除" 列の値がTrueの行を削除
    if st.button("選択した行を削除"):
        st.session_state["contracts"] = edited_df[~edited_df["削除"]].drop(columns=["削除"])
        st.success("選択した行が削除されました。")

    # 更新されたデータの表示
    st.subheader("更新後のデータフレーム")
    st.dataframe(st.session_state["contracts"], use_container_width=True)
else:
    st.info("CSVファイルをアップロードしてください。")

# 継続率を計算する関数
def calculate_continuity_rate(data):
    data = data.sort_values("終了日")
    total = len(data)
    data["累計終了"] = range(1, total + 1)
    data["継続率"] = (total - data["累計終了"]) / total * 100
    return data

# 終了率グラフ + スライダーでX軸をスクロール
def plot_completion_rate_with_slider(data, freq="D"):
    if data.empty:
        st.write("データがありません。")
        return

    # 全ての日付範囲を生成（開始日から3か月後まで）
    start_date = data["開始日"].min()
    end_date = datetime.now() + timedelta(days=90)
    all_dates = pd.date_range(start=start_date, end=end_date, freq=freq)

    # 日付ごとの終了率を計算
    completion_data = pd.DataFrame(index=all_dates)
    total_contracts = 0  # 総契約数
    completed_contracts = 0  # 終了した契約数
    completion_rates = []

    for current_date in completion_data.index:
        started_today = len(data[data["開始日"] == current_date])
        total_contracts += started_today
        completed_today = len(data[data["終了日"] == current_date])
        completed_contracts += completed_today

        if total_contracts > 0:
            completion_rate = (completed_contracts / total_contracts) * 100
        else:
            completion_rate = 0

        completion_rates.append(completion_rate)

    completion_data["終了率"] = completion_rates

    # 日付範囲をスライダーで設定（Timestamp → datetime.dateに変換）
    min_date = completion_data.index.min().date()
    max_date = completion_data.index.max().date()
    selected_range = st.slider(
        "表示期間を選択してください。",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, (min_date + timedelta(days=30))),  # 修正された部分
    )

    # 選択した範囲でフィルタリング
    filtered_data = completion_data.loc[
        (completion_data.index >= pd.Timestamp(selected_range[0])) &
        (completion_data.index <= pd.Timestamp(selected_range[1]))
    ]

    # グラフを作成
    plt.figure(figsize=(10, 5))
    plt.step(filtered_data.index, filtered_data["終了率"], where="mid", label="終了率", linewidth=2)

    plt.title("終了率推移", fontsize=16, fontproperties=font_prop)
    plt.xlabel("期間", fontsize=12, fontproperties=font_prop)
    plt.ylabel("終了率 (%)", fontsize=12, fontproperties=font_prop)
    plt.xticks(rotation=45, fontproperties=font_prop)
    plt.yticks(fontproperties=font_prop)
    plt.grid(True)

    # 凡例を追加
    plt.legend(prop=font_prop, fontsize=10)

    # グラフをバッファに保存してStreamlitに表示
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=300)
    buf.seek(0)
    st.image(buf, caption="終了率推移 (スライダーで期間選択)", use_container_width=True)
    buf.close()

# エンジニア情報追加フォーム
st.sidebar.subheader("エンジニア情報を追加")
with st.sidebar.form("add_engineer_form", clear_on_submit=True):
    engineer_name = st.text_input("エンジニア名")
    skill = st.text_input("スキル")
    client_name = st.text_input("顧客名")
    start_date = st.date_input("開始日")
    end_date = st.date_input("終了日")
    alert_hidden = st.checkbox("アラート非表示", value=False)
    submitted = st.form_submit_button("追加")

if submitted:
    # 入力値の有効性を確認
    if not (engineer_name and skill and client_name and start_date and end_date):
        st.warning("すべての情報を入力してください。")
    else:
        # 新しいデータを生成
        new_row = {
            "エンジニア名": engineer_name,
            "スキル": skill,
            "顧客名": client_name,
            "開始日": pd.to_datetime(start_date),
            "終了日": pd.to_datetime(end_date),
            "継続日数": (datetime.now() - pd.to_datetime(start_date)).days,
            "アラート非表示": alert_hidden,
        }

        # セッション状態に新しいデータを追加
        updated_contracts = pd.concat(
            [st.session_state["contracts"], pd.DataFrame([new_row])],
            ignore_index=True,
        )
        st.session_state["contracts"] = updated_contracts

        # 追加完了メッセージ
        st.success("エンジニア情報を追加しました。")

# データ表示タブ
tab_all, tab_latest, tab_ongoing, tab_completed, tab_rate = st.tabs(
    ["全体タブ", "最新タブ", "継続タブ", "終了タブ", "終了率グラフ"]
)

# 全体タブ（すべてのデータを表示）
with tab_all:
    st.subheader("全体タブ: 全ての契約")
    st.dataframe(
        st.session_state["contracts"],
        use_container_width=True,
        column_config={
            "アラート非表示": st.column_config.CheckboxColumn("アラート非表示")
        },
    )

# 最新タブ（アラート非表示を除外）
with tab_latest:
    st.subheader("最新タブ: アラート表示中の契約")
    latest_data = st.session_state["contracts"][
        st.session_state["contracts"]["アラート非表示"] == False
    ]
    st.dataframe(
        latest_data,
        use_container_width=True,
        column_config={
            "アラート非表示": st.column_config.CheckboxColumn("アラート非表示")
        },
    )

# 継続タブ
with tab_ongoing:
    st.subheader("継続タブ: 継続中の契約")
    ongoing_data = st.session_state["contracts"][
        (st.session_state["contracts"]["終了日"] > datetime.now()) &
        (st.session_state["contracts"]["アラート非表示"] == False)
    ]
    st.dataframe(
        ongoing_data,
        use_container_width=True,
        column_config={
            "アラート非表示": st.column_config.CheckboxColumn("アラート非表示")
        },
    )

# 終了タブ
with tab_completed:
    st.subheader("終了タブ: 継続が終了した契約")
    completed_data = st.session_state["contracts"][
        (st.session_state["contracts"]["終了日"] <= datetime.now()) &
        (st.session_state["contracts"]["アラート非表示"] == False)
    ]
    st.dataframe(
        completed_data,
        use_container_width=True,
        column_config={
            "アラート非表示": st.column_config.CheckboxColumn("アラート非表示")
        },
    )

# 終了率グラフタブ
with tab_rate:
    st.subheader("終了率グラフ (スライダー付き)")
    contracts_data = st.session_state["contracts"]

    if not contracts_data.empty:
        plot_completion_rate_with_slider(contracts_data, freq="D")
    else:
        st.write("現在終了した契約がありません。")
