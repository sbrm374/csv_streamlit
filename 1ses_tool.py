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
        # CSVデータを最初にShift_JISで読み込む
        try:
            uploaded_data = pd.read_csv(uploaded_file, encoding="shift_jis")
            st.success("ファイルがShift_JISエンコーディングとして読み込まれました。")
        except UnicodeDecodeError:
            # Shift_JISでエラーが発生した場合、UTF-8で再試行
            uploaded_file.seek(0)  # ファイルポインタを先頭に戻す
            uploaded_data = pd.read_csv(uploaded_file, encoding="utf-8")
            st.success("ファイルがUTF-8エンコーディングとして読み込まれました。")

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
