import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
import matplotlib.font_manager as fm
import io
import os
import plotly.express as px

# 폰트 설정
font_path = "./fonts/NotoSansJP-Regular.otf"
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False  # 음수 기호 깨짐 방지

# タイトル
st.title("SES事業継続率管理ツール")

# 샘플 데이터
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

# CSVファイルアップロード
uploaded_file = st.sidebar.file_uploader("CSVファイルをアップロードしてください", type=["csv"])

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

# 지속률 계산 함수
def calculate_continuity_rate(data):
    data = data.sort_values("終了日")
    total = len(data)
    data["累計終了"] = range(1, total + 1)
    data["継続率"] = (total - data["累計終了"]) / total * 100
    return data

# 완료율 그래프 + 슬라이더로 X축 스크롤 구현
def plot_completion_rate_with_slider(data, freq="D"):
    if data.empty:
        st.write("データがありません。")
        return

    # 모든 날짜 범위 생성 (시작일부터 3달 뒤까지)
    start_date = data["開始日"].min()
    end_date = datetime.now() + timedelta(days=90)
    all_dates = pd.date_range(start=start_date, end=end_date, freq=freq)

    # 날짜별 완료율 계산
    completion_data = pd.DataFrame(index=all_dates)
    total_contracts = 0  # 총 계약 수
    completed_contracts = 0  # 완료된 계약 수
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

    # 날짜 범위를 슬라이더로 설정 (Timestamp → datetime.date 변환)
    min_date = completion_data.index.min().date()
    max_date = completion_data.index.max().date()
    selected_range = st.slider(
        "表示期間を選択してください。",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, (min_date + timedelta(days=30))),  # 수정된 부분
    )

    # 선택된 범위로 필터링
    filtered_data = completion_data.loc[
        (completion_data.index >= pd.Timestamp(selected_range[0])) &
        (completion_data.index <= pd.Timestamp(selected_range[1]))
    ]

    # 그래프 생성
    plt.figure(figsize=(10, 5))
    plt.step(filtered_data.index, filtered_data["終了率"], where="mid", label="終了率", linewidth=2)

    plt.title("終了率推移", fontsize=16, fontproperties=font_prop)
    plt.xlabel("期間", fontsize=12, fontproperties=font_prop)
    plt.ylabel("終了率 (%)", fontsize=12, fontproperties=font_prop)
    plt.xticks(rotation=45, fontproperties=font_prop)
    plt.yticks(fontproperties=font_prop)
    plt.grid(True)

    # 범례 추가
    plt.legend(prop=font_prop, fontsize=10)

    # 그래프를 버퍼에 저장 후 Streamlit에 출력
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=300)
    buf.seek(0)
    st.image(buf, caption="終了率推移 (スライダーで期間選択)", use_container_width=True)
    buf.close()


    
# タブ表示
tab_all, tab_latest, tab_ongoing, tab_completed, tab_rate = st.tabs(
    ["全体タブ", "最新タブ", "継続タブ", "終了タブ", "終了率グラフ"]
)

# 全体タブ (모든 데이터를 보여줌)
with tab_all:
    st.subheader("全体タブ: 全ての契約")
    st.dataframe(st.session_state["contracts"], use_container_width=True)

# 最新タブ (알림 비표시 제외)
with tab_latest:
    st.subheader("最新タブ: アラート表示中の契約")
    latest_data = st.session_state["contracts"][st.session_state["contracts"]["アラート非表示"] == False]
    st.dataframe(latest_data, use_container_width=True)

# 継続タブ
with tab_ongoing:
    st.subheader("継続タブ: 継続中の契約")
    ongoing_data = st.session_state["contracts"][
        (st.session_state["contracts"]["終了日"] > datetime.now()) &
        (st.session_state["contracts"]["アラート非表示"] == False)
    ]
    st.dataframe(ongoing_data, use_container_width=True)

# 終了タブ
with tab_completed:
    st.subheader("終了タブ: 継続が終了した契約")
    completed_data = st.session_state["contracts"][
        (st.session_state["contracts"]["終了日"] <= datetime.now()) &
        (st.session_state["contracts"]["アラート非表示"] == False)
    ]
    st.dataframe(completed_data, use_container_width=True)
    

# 終了率グラフタブ
with tab_rate:
    st.subheader("終了率グラフ (スライダー付き)")
    contracts_data = st.session_state["contracts"]

    if not contracts_data.empty:
        plot_completion_rate_with_slider(contracts_data, freq="D")
    else:
        st.write("現在終了した契約がありません。")

# エンジニア情報追加フォーム
st.sidebar.subheader("エンジニア情報を追加")
with st.sidebar.form("add_engineer_form"):
    engineer_name = st.text_input("エンジニア名")
    skill = st.text_input("スキル")
    client_name = st.text_input("顧客名")
    start_date = st.date_input("開始日")
    end_date = st.date_input("終了日")
    alert_hidden = st.checkbox("アラート非表示", value=False)
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
            "アラート非表示": alert_hidden,
        }

        # 세션 상태의 데이터프레임에 행 추가
        st.session_state["contracts"] = pd.concat(
            [st.session_state["contracts"], pd.DataFrame([new_row])], ignore_index=True
        )

        # 성공 메시지
        st.success("エンジニア情報を追加しました。")
        st.rerun()
