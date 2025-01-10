import chardet  # 인코딩 감지를 위해 추가 설치 필요
import streamlit as st
import pandas as pd
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import io

# フォント設定
font_path = "./fonts/NotoSansJP-Regular.otf"
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False

# タイトル
st.title("SES事業継続率管理ツール")

# CSVファイルをアップロード
uploaded_file = st.sidebar.file_uploader("CSVファイルをアップロードしてください", type=["csv"])

if uploaded_file is not None:
    try:
        # ファイルのバイナリデータを読み込む
        raw_data = uploaded_file.read()
        
        # インコーディングを自動検出
        detected = chardet.detect(raw_data)
        encoding = detected['encoding'] if detected['confidence'] > 0.8 else 'utf-8'  # 信頼度が高ければそのエンコーディングを使用
        
        # データをエンコーディングを指定して読み込む
        uploaded_data = pd.read_csv(io.BytesIO(raw_data), encoding=encoding)
        
        # 日付フィールドをパース
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

        # アップロード成功の通知
        st.success(f"CSVファイルがアップロードされました。検出されたエンコーディング: {encoding}")

    except Exception as e:
        st.error(f"アップロードされたファイルの処理中にエラーが発生しました: {e}")
