import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
import matplotlib.font_manager as fm
import io
import os
import plotly.express as px
import chardet
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer as SumyTokenizer
from sumy.summarizers.lsa import LsaSummarizer
import re
from janome.tokenizer import Tokenizer
import requests

# DeepSeek API 엔드포인트
api_url = "https://api.deepseek.com/chat/completions"

# 발급받은 API 키
api_key = "sk-078fbb28ff064aa582be5d0a3767cc6f"

# 요청 헤더 설정
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# 요약 요청 함수
def summarize_text(text):
    # 요청 데이터 설정
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant specialized in summarizing text into the following format: ・イニシャル, ・年齢, ・性別, ・最寄り駅, ・得意分野, ・PR."},
            {"role": "user", "content": f"Please summarize the following text in the specified format:\n{text}"}
        ],
        "stream": False
    }

    # API 호출
    response = requests.post(api_url, headers=headers, json=data)

    # 응답 처리
    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content']
    else:
        return f"오류 발생: {response.status_code} - {response.text}"
        
def preprocess_text(text):
    """
    텍스트 전처리 함수: 불필요한 정보 제거 및 정리.
    """
    # 1. Unnamed와 NaN 제거
    text = re.sub(r"Unnamed: \d+|NaN", "", text)

    # 2. 중복된 공백 및 줄바꿈 제거
    text = re.sub(r"\s+", " ", text.strip())

    # 3. 불필요한 특수 문자 제거
    text = re.sub(r"[^a-zA-Z0-9가-힣ぁ-んァ-ン一-龥 .,。！？]", "", text)

    # 4. 텍스트 길이 줄이기 (필요 시)
    if len(text) > 10000:  # 필요 이상으로 긴 경우, 앞뒤 주요 부분만 사용
        text = text[:5000] + " ... " + text[-5000:]

    return text

# 텍스트 분할 함수
def split_text(text, chunk_size=1000):
    """
    긴 텍스트를 chunk_size로 나누는 함수.
    """
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    
# 형태소 분석 함수
def perform_mecab_analysis(text):
    tokenizer = Tokenizer()
    tokens = tokenizer.tokenize(text, wakati=True)
    return " ".join(tokens)

# 요약 함수
def summarize_text(text, max_sentences=2):
    parser = PlaintextParser.from_string(text, SumyTokenizer("japanese"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, max_sentences)
    return [str(sentence) for sentence in summary]
    
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

# セッション状態を初期化
if "contracts" not in st.session_state:
    st.session_state["contracts"] = pd.DataFrame(
        {
            "削除": pd.Series(dtype=bool),  # 明示的にbool型で初期化
            "エンジニア名": pd.Series(dtype=str),
            "スキル": pd.Series(dtype=str),
            "顧客名": pd.Series(dtype=str),
            "開始日": pd.Series(dtype="datetime64[ns]"),
            "終了日": pd.Series(dtype="datetime64[ns]"),
            "継続日数": pd.Series(dtype=int),
            "アラート非表示": pd.Series(dtype=bool),
        }
    )

if "render_flag" not in st.session_state:
    st.session_state["render_flag"] = False  # レンダリング制御フラグの初期化

def detect_encoding(file):
    """
    Detect the encoding of a given file using chardet.
    """
    raw_data = file.read()
    file.seek(0)  # Reset file pointer after reading
    result = chardet.detect(raw_data)
    encoding = result['encoding']
    if encoding is None:
        raise ValueError("ファイルのエンコーディングを判定できませんでした。")
    return encoding
    
def read_csv_with_encoding(file):
    """
    Read a CSV file with detected encoding.
    """
    try:
        encoding = detect_encoding(file)
        return pd.read_csv(file, encoding=encoding)
    except Exception as e:
        raise ValueError(f"CSVファイルを読み込む際にエラーが発生しました: {e}")


def generate_csv_download(dataframe, filename="data.csv"):
    """
    Generate CSV data encoded as utf-8 or shift_jis.
    """
    try:
        return dataframe.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    except UnicodeEncodeError:
        return dataframe.to_csv(index=False, encoding="shift_jis").encode("shift_jis")

# アップロードされたファイルを処理
if uploaded_file is not None:
    try:
        uploaded_data = read_csv_with_encoding(uploaded_file)

        uploaded_data["開始日"] = pd.to_datetime(uploaded_data["開始日"])
        uploaded_data["終了日"] = pd.to_datetime(uploaded_data["終了日"])
        uploaded_data["継続日数"] = [
            (datetime.now() - start).days for start in uploaded_data["開始日"]
        ]
        uploaded_data["アラート非表示"] = [False] * len(uploaded_data)
        uploaded_data["削除"] = [False] * len(uploaded_data)
    
        # データ型を明示的に変換
        uploaded_data["削除"] = uploaded_data["削除"].astype(bool)
        uploaded_data["アラート非表示"] = uploaded_data["アラート非表示"].astype(bool)
    
        # すでにアップロードされたデータか確認
        if "uploaded_flag" not in st.session_state or not st.session_state["uploaded_flag"]:
            # アップロードされたデータを既存データにマージ
            st.session_state["contracts"] = pd.concat(
                [st.session_state["contracts"], uploaded_data], ignore_index=True
            )
            # データのマージ後にデータ型を保証する
            st.session_state["contracts"]["削除"] = st.session_state["contracts"]["削除"].astype(bool)
            st.session_state["contracts"]["アラート非表示"] = st.session_state["contracts"]["アラート非表示"].astype(bool)
    
            st.session_state["uploaded_flag"] = True  # アップロード完了フラグを設定
            st.success("CSVファイルがアップロードされました。")
    except Exception as e:
        st.error(f"アップロードされたファイルの処理中にエラーが発生しました: {e}")
        
# Xボタンの動作を検知（ファイルのアップロードが初期化されたか確認）
elif "uploaded_flag" in st.session_state and st.session_state["uploaded_flag"]:
    # セッション状態を初期化
    st.session_state["contracts"] = pd.DataFrame(
        {
            "削除": pd.Series(dtype=bool),
            "エンジニア名": pd.Series(dtype=str),
            "スキル": pd.Series(dtype=str),
            "顧客名": pd.Series(dtype=str),
            "開始日": pd.Series(dtype="datetime64[ns]"),
            "終了日": pd.Series(dtype="datetime64[ns]"),
            "継続日数": pd.Series(dtype=int),
            "アラート非表示": pd.Series(dtype=bool),
        }
    )
    st.session_state["uploaded_flag"] = False
    
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
            "削除": False,
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

    text_data = """株式会社エイト
内山様

お世話になります。
てくてくの近藤です。

下記案件にて人材を探しております。
見合う方が居られましたらご紹介いただけますと幸いです。
ご確認よろしくお願いいたします。

※案件情報の再配信やwebサイトへ掲載するなどの行為は禁止します。

------------------------------------------------------
商流　　　：元請→上位→弊社
案件　　　：金融機関向け経理システム保守
概要　　　：仕訳データの取り扱いや帳簿作成、
　　　　　　DB操作や、必要に応じてロジック修正
期間　　　：2025年3月 ～ 長期予定
募集人数　：1名
勤務地　　：豊洲
勤務時間　：8:50?17:10
単価　　　：スキル見合い
精算　　　：固定
スキル　　：＜必須＞
　　　　　　・開発経験または設計経験 4年以上
　　　　　　・DB操作経験 3年以上
　　　　　　（DB周りを理解していること(データ型、プライマリーキー、一意制約違反等))
　　　　　　・SQL経験 3年以上
　　　　　　（DML文の基礎を理解していること）
　　　　　　・コミュニケーション能力
　　　　　　
　　　　　　＜尚可＞
　　　　　　・OracleEBS
　　　　　　・OracleDB
　　　　　　・Solaris、Linux※サーバ上でのコマンド操作
　　　　　　・C言語、シェル、Java
　　　　　　・PL/SQL
　　　　　　・AWS
　　　　　　・会計知識（日商簿記等）
　　　　　　・JP1※使い方、基礎知識

その他条件　：外国籍不可、40歳以上不可
面談　　　　：1回（上位プロパーとの面談）
商流制限　　：貴社プロパーまで
------------------------------------------------------


■■────────────────

株式会社てくてく
代表取締役　近藤優樹

〒160-0023
東京都新宿区西新宿8-11-10 星野ビル3F
MOBILE：090-4545-7548
TEL：03-6403-9099
FAX：03-6701-7399
MAIL：y.kondo@tektek.co.jp
URL：https://www.tektek.co.jp

────────────────■■

"""
    # text_data = "Unnamed: 0 Unnamed: 1 Unnamed: 2 Unnamed: 3 Unnamed: 4 Unnamed: 5 Unnamed: 6 Unnamed: 7 Unnamed: 8 Unnamed: 9 Unnamed: 10 Unnamed: 11 Unnamed: 12 Unnamed: 13 Unnamed: 14 Unnamed: 15 Unnamed: 16 Unnamed: 17 Unnamed: 18 Unnamed: 19 Unnamed: 20 Unnamed: 21 Unnamed: 22 Unnamed: 23 Unnamed: 24 Unnamed: 25 Unnamed: 26 Unnamed: 27 Unnamed: 28 Unnamed: 29 Unnamed: 30 Unnamed: 31 Unnamed: 32 Unnamed: 33 Unnamed: 34 Unnamed: 35 Unnamed: 36 Unnamed: 37 Unnamed: 38 Unnamed: 39 Unnamed: 40 Unnamed: 41 Unnamed: 42 Unnamed: 43 Unnamed: 44 Unnamed: 45 Unnamed: 46 Unnamed: 47 Unnamed: 48 Unnamed: 49 Unnamed: 50 Unnamed: 51 Unnamed: 52 　 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN 【職務経歴書】 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN ﾌﾘｶﾞﾅ NaN NaN NaN NaN 年齢 NaN NaN NaN 生年月日 NaN NaN NaN NaN NaN NaN 性別 NaN NaN 最寄り駅 NaN NaN NaN NaN NaN NaN NaN NaN NaN 取得日 NaN NaN NaN NaN NaN 資格 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN 氏名 NaN NT NaN NaN 28 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN 男 NaN NaN 京王・小田急/永山駅 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN 最終学歴 NaN NaN NaN 大学中退 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN 業務上の\n得意分野 NaN NaN NaN Java/Springboot / HTML / CSS / Javascript / Junit / Mybatis / Github NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN PR NaN NaN NaN 私の強みは、コミュニケーション能力の高さと、多趣味な一面を活かした柔軟な対応力です。特に、人と関わることが好きで、チームで協力し合いながら目標を達成することにやりがいを感じています。趣味としては本を読むことや楽器を演奏することがあり、常に新しい知識を吸収することに積極的です。これらの経験を通じて、日々成長し続けることができ、オンとオフの切り替えも得意です。今後もその特性を活かして、貴社に貢献できるよう努力していきます。 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN 経験 NaN NaN NaN 環境（OS等) NaN NaN NaN NaN NaN NaN DB NaN NaN NaN NaN NaN NaN 開発言語 NaN NaN NaN NaN NaN NaN FW NaN NaN NaN NaN NaN NaN ｿﾌﾄｳｪｱ NaN NaN NaN NaN NaN NaN ﾈｯﾄﾜｰｸ（機器等) NaN NaN NaN NaN NaN NaN その他 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN Win NaN NaN NaN NaN NaN NaN SQL NaN NaN NaN NaN NaN NaN Java NaN NaN NaN NaN NaN NaN Springboot NaN NaN NaN NaN NaN NaN teams NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN AWS NaN NaN NaN NaN NaN NaN MySQL NaN NaN NaN NaN NaN NaN HTML NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN Slack NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN CSS NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN Junit NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN Javascript NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN 業務詳細・トレーニング概要 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN 調査分析 要件定義 基本設計 詳細設計 製造 テスト 運用 NaN 期間 NaN NaN NaN 配属部署の業務概要 NaN NaN NaN NaN NaN NaN NaN NaN 個人で担当した業務詳細 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN 環境・使用ソフト NaN NaN NaN NaN NaN 言語・その他 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN 1 NaN NaN NaN NaN 【プロジェクト名】 NaN NaN NaN NaN NaN NaN NaN NaN 【担当業務内容】 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN ふるさと納税Webサイト\nリニューアル NaN NaN NaN NaN NaN NaN NaN NaN ---工程---\n　・詳細設計（改修・新規）\n　・製造（改修・新規）\n　・単体テスト\n\n---内容---\n　・アカウント認証機能\n　・商品登録機能\n　・商品検索機能\n　・商品問い合せ機能\n　・商品評価・口コミ機能\n　・支払機能\n　・マイページ機能 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN Win\nAWS NaN NaN NaN NaN NaN Java\nSpringboot\nMyBatis\nJunit\nGithub NaN NaN NaN NaN NaN NaN NaN NaN 〇 〇 〇 NaN NaN 45323 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN 45292 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN 1年 NaN NaN NaN 【業種】 NaN NaN 【役割】 NaN NaN 【規模】 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN IT NaN NaN SE NaN NaN 6 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN 2 NaN NaN NaN NaN 【プロジェクト名】 NaN NaN NaN NaN NaN NaN NaN NaN 【担当業務内容】 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN 保険システム運用・保守 NaN NaN NaN NaN NaN NaN NaN NaN ---工程---\n　・詳細設計（改修・新規）\n　・製造（改修・新規）\n　・単体テスト\n　・結合テスト\n　・運用\n\n---内容---\n　・信用口座開設判定機能\n　・定期保険 解約抽出機能\n　・代用有価証券不当引出アラート通知機能\n　・バッチ確認\n　・保険未払詳細抽出機能\n　・提携先保険会社のAPI接続など NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN Win\nAWS NaN NaN NaN NaN NaN Java\nSpringboot\nHTML\nCSS\nJavaScript\nGitHub\nA5M2\neclipse NaN NaN NaN NaN NaN NaN NaN NaN 〇 〇 〇 〇 NaN 44835 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN 45261 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN 1年2ヶ月 NaN NaN NaN 【業種】 NaN NaN 【役割】 NaN NaN 【規模】 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN 金融 NaN NaN SE NaN NaN 30 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN 3 NaN NaN NaN NaN 【プロジェクト名】 NaN NaN NaN NaN NaN NaN NaN NaN 【担当業務内容】 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN 研修 現場OJT NaN NaN NaN NaN NaN NaN NaN NaN エンジニア研修 3ヶ月\nJava\nSpringboot\nMySQL\n\n■現場OJT 3ヶ月\n不動産-検索情報システムの開発-単体テスト-改修\n NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN Win NaN NaN NaN NaN NaN Java\nSpringboot\nMyBatis\nJunit\nGithub NaN NaN NaN NaN NaN NaN NaN NaN 〇 〇 〇 NaN NaN 44652 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN 44805 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN 6ヶ月 NaN NaN NaN 【業種】 NaN NaN 【役割】 NaN NaN 【規模】 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN 不動産 NaN NaN PG NaN NaN 4 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN 4 NaN NaN NaN NaN 【プロジェクト名】 NaN NaN NaN NaN NaN NaN NaN NaN 【担当業務内容】 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN 43313 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN フリーランス営業として従事 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN 44621 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN 【業種】 NaN NaN 【役割】 NaN NaN 【規模】 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN - NaN NaN - NaN NaN - NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN 5 NaN NaN NaN NaN 【プロジェクト名】 NaN NaN NaN NaN NaN NaN NaN NaN 【担当業務内容】 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN 【業種】 NaN NaN 【役割】 NaN NaN 【規模】 NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN 【用語解説】　PM:ﾌﾟﾛｼﾞｪｸﾄﾏﾈｰｼﾞｬｰ、PL:ﾌﾟﾛｼﾞｪｸﾄﾘｰﾀﾞｰ、SL:ｻﾌﾞﾘｰﾀﾞｰ、M:ﾒﾝﾊﾞｰ NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN"
    cleaned_text = preprocess_text(text_data)
    # if st.button("要約実行"):
    #     cleaned_text = preprocess_text(text_data)
    #     text_chunks = split_text(cleaned_text)
    
    #     all_summaries = []
    #     for chunk in text_chunks:
    #         wakati_text = perform_mecab_analysis(chunk)
    #         summary = summarize_text(wakati_text)
    #         all_summaries.extend(summary)
    
    #     st.subheader("要約実行")
    #     for sentence in all_summaries:
    #         st.write(sentence)

    # 요약 버튼
    if st.button("要約実行!"):
        if cleaned_text.strip():  # 텍스트가 입력된 경우에만 실행
            with st.spinner("要約中..."):
                summary = summarize_text(cleaned_text)
            st.success("要約完了!")
            st.write("### 要約実行:")
            st.write(summary)
        else:
            st.warning("요약할 텍스트를 입력하세요!")
        
    # 初回のみ "contracts" を初期化
    if "contracts" not in st.session_state:
        st.session_state["contracts"] = pd.DataFrame({
            "エンジニア名": ["山田太郎", "佐藤花子"],
            "スキル": ["Python", "Java"],
            "顧客名": ["顧客A", "顧客B"],
            "削除": [False, False],
        })

    # `st.data_editor`を使用して編集可能にする
    edited_data = st.data_editor(
        st.session_state["contracts"],
        use_container_width=True,
        num_rows="static",
        column_config={
            "削除": st.column_config.CheckboxColumn(
                "削除",
                help="削除したい行を選択してください。",
            ),
            "アラート非表示": st.column_config.CheckboxColumn(
                "アラート非表示",
                disabled=True,  # 編集不可に設定
                help="この列は編集できません。",
            ),
        },
        key="editor",
    )
    
    # 削除ボタンを追加
    if st.button("選択した行を削除"):
        # `削除`列がTrueの行を削除
        st.session_state["contracts"] = edited_data[~edited_data["削除"]].reset_index(drop=True)
        st.rerun()
        st.success("選択した行が削除されました。")

    # 最終データダウンロードボタンを追加
    if not st.session_state["contracts"].empty:
        final_csv = generate_csv_download(st.session_state["contracts"], "current_ses_data.csv")
        st.sidebar.download_button(
            label="現在のデータをダウンロード",
            data=final_csv,
            file_name="current_ses_data.csv",
            mime="text/csv"
        )
    else:
        st.sidebar.write("現在のデータがありません。")
        
# 最新タブ（アラート非表示を除外）
with tab_latest:
    st.subheader("最新タブ: アラート表示中の契約")
    filtered_data = st.session_state["contracts"][st.session_state["contracts"]["アラート非表示"] == False]

    edited_latest = st.data_editor(
        filtered_data,
        use_container_width=True,
        num_rows="static",
        column_config={
            "削除": st.column_config.CheckboxColumn(
                "削除",
                help="削除したい行を選択してください。",
            ),
            "アラート非表示": st.column_config.CheckboxColumn(
                "アラート非表示",
                disabled=True,
                help="この列は編集できません。",
            ),
        },
        key="editor_latest",
    )

    if st.button("選択した行を削除", key="delete_latest"):
        st.session_state["contracts"] = st.session_state["contracts"][
            ~st.session_state["contracts"].index.isin(edited_latest[edited_latest["削除"]].index)
        ].reset_index(drop=True)
        st.rerun()

# 継続タブ
with tab_ongoing:
    st.subheader("継続タブ: 継続中の契約")
    now = pd.Timestamp.now()
    filtered_data = st.session_state["contracts"][
        (st.session_state["contracts"]["終了日"] > datetime.now()) &
        (st.session_state["contracts"]["アラート非表示"] == False)
    ]

    edited_ongoing = st.data_editor(
        filtered_data,
        use_container_width=True,
        num_rows="static",
        column_config={
            "削除": st.column_config.CheckboxColumn(
                "削除",
                help="削除したい行を選択してください。",
            ),
            "アラート非表示": st.column_config.CheckboxColumn(
                "アラート非表示",
                disabled=True,
                help="この列は編集できません。",
            ),
        },
        key="editor_ongoing",
    )

    if st.button("選択した行を削除", key="delete_ongoing"):
        st.session_state["contracts"] = st.session_state["contracts"][
            ~st.session_state["contracts"].index.isin(edited_ongoing[edited_ongoing["削除"]].index)
        ].reset_index(drop=True)
        st.rerun()

# 終了タブ
with tab_completed:
    st.subheader("終了タブ: 継続が終了した契約")
    now = pd.Timestamp.now()
    filtered_data = st.session_state["contracts"][
        (st.session_state["contracts"]["終了日"] <= datetime.now()) &
        (st.session_state["contracts"]["アラート非表示"] == False)
    ]
    
    edited_completed = st.data_editor(
        filtered_data,
        use_container_width=True,
        num_rows="static",
        column_config={
            "削除": st.column_config.CheckboxColumn(
                "削除",
                help="削除したい行を選択してください。",
            ),
            "アラート非表示": st.column_config.CheckboxColumn(
                "アラート非表示",
                disabled=True,
                help="この列は編集できません。",
            ),
        },
        key="editor_completed",
    )

    if st.button("選択した行を削除", key="delete_completed"):
        st.session_state["contracts"] = st.session_state["contracts"][
            ~st.session_state["contracts"].index.isin(edited_completed[edited_completed["削除"]].index)
        ].reset_index(drop=True)
        st.rerun()

# 終了率グラフタブ
with tab_rate:
    st.subheader("終了率グラフ (スライダー付き)")
    contracts_data = st.session_state["contracts"]

    if not contracts_data.empty:
        plot_completion_rate_with_slider(contracts_data, freq="D")
    else:
        st.write("現在終了した契約がありません。")
