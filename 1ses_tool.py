import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.font_manager as fm
import io
import os

# 폰트 설정
font_path = "./fonts/NotoSansJP-Regular.otf"
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False  # 음수 기호 깨짐 방지

# 디버깅 정보 출력
st.write("Font file exists:", os.path.exists(font_path)) 
st.write("Loaded font name:", font_prop.get_name())
st.write("Current font family:", plt.rcParams['font.family'])

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

# 종료율 그래프
def plot_continuity_rate(data, freq="M"):
    if not data.empty:
        # 주기별 데이터 처리 (freq: "D"=일별, "M"=월별, "Y"=년도별)
        data = data.set_index("終了日").resample(freq).count()
        data["累計終了"] = data["エンジニア名"].cumsum()  # 종료 인원 누적
        total = len(st.session_state["contracts"])
        data["継続率"] = (total - data["累計終了"]) / total * 100

        # 그래프 생성
        plt.figure(figsize=(10, 5))
        plt.plot(data.index, data["継続率"], marker="o")
        
        # 텍스트 설정
        freq_label = {"D": "日別", "M": "月別", "Y": "年別"}[freq]
        plt.title(f"継続率推移 ({freq_label})", fontsize=16, fontproperties=font_prop)
        plt.xlabel("期間", fontsize=12, fontproperties=font_prop)
        plt.ylabel("継続率 (%)", fontsize=12, fontproperties=font_prop)
        plt.xticks(rotation=45, fontproperties=font_prop)
        plt.yticks(fontproperties=font_prop)
        plt.grid(True)

        # 그래프를 버퍼에 저장 후 Streamlit에 출력
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=300)
        buf.seek(0)
        st.image(buf, caption=f"継続率推移 ({freq_label})", use_container_width=True)
        buf.close()

# タブ表示
tab_all, tab_latest, tab_ongoing, tab_completed, tab_rate = st.tabs(
    ["全体タブ", "最新タブ", "継続タブ", "終了タブ", "継続率グラフ"]
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

# 継続率グラフタブ
with tab_rate:
    st.subheader("継続率グラフ")
    completed_data = st.session_state["contracts"][
        st.session_state["contracts"]["終了日"] <= datetime.now()
    ]

    if not completed_data.empty:
        # 년도별, 월별, 일별 옵션
        plot_continuity_rate(completed_data, freq="Y")  # 年別
        plot_continuity_rate(completed_data, freq="M")  # 月別
        plot_continuity_rate(completed_data, freq="D")  # 日別
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
