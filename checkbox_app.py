import streamlit as st

# チェックボックスの状態を初期化
if "checkboxes" not in st.session_state:
    st.session_state["checkboxes"] = {f"checkbox_{i}": False for i in range(1, 11)}

# ユニークキー管理用の状態を追加
if "unique_keys" not in st.session_state:
    st.session_state["unique_keys"] = {f"checkbox_{i}": f"checkbox_{i}" for i in range(1, 11)}

# 初期化ボタン
st.title("チェックボックス初期化ボタン")
st.write("すべてのチェックボックスを解除するには、以下のボタンを押してください:")

if st.button("初期化"):
    # すべてのチェックボックスを False に設定
    for i in range(1, 11):
        checkbox_key = f"checkbox_{i}"
        # チェックボックスキーを変更して Streamlit に強制レンダリングを促す
        st.session_state["unique_keys"][checkbox_key] += "_updated"
        st.session_state["checkboxes"][checkbox_key] = False
    
    # UI を強制的に再実行
    st.rerun()

# チェックボックスをレンダリングする関数
def render_checkboxes():
    for i in range(1, 11):
        checkbox_key = f"checkbox_{i}"
        # 動的に変更されたキーを使用してチェックボックスを生成
        new_key = st.session_state["unique_keys"][checkbox_key]
        current_value = st.checkbox(
            f"チェックボックス {i}",
            value=st.session_state["checkboxes"][checkbox_key],
            key=new_key,
        )
        # 状態を同期
        st.session_state["checkboxes"][checkbox_key] = current_value

# チェックボックスをレンダリングする呼び出し
st.title("チェックボックス例")
st.write("チェックボックスを選択してください:")
render_checkboxes()

# 状態のデバッグ出力
st.write("現在のチェックボックス状態:", st.session_state["checkboxes"])
