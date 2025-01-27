import streamlit as st

# 체크박스 상태 초기화
if "checkboxes" not in st.session_state:
    st.session_state["checkboxes"] = {f"checkbox_{i}": False for i in range(1, 11)}

# 체크박스 렌더링
st.title("체크박스 예제")
st.write("체크박스를 선택하세요:")

for i in range(1, 11):
    checkbox_key = f"checkbox_{i}"
    # 체크박스를 렌더링하면서 현재 상태를 유지
    st.session_state["checkboxes"][checkbox_key] = st.checkbox(
        f"체크박스 {i}",
        value=st.session_state["checkboxes"][checkbox_key],
        key=checkbox_key
    )

# 초기화 버튼
st.title("체크박스 초기화 버튼")
st.write("모든 체크박스를 해제하려면 아래 버튼을 누르세요:")

if st.button("초기화", key="reset_button"):
    # 상태를 직접 변경 (rerun 없이)
    for i in range(1, 11):
        st.session_state["checkboxes"][f"checkbox_{i}"] = False

# 렌더링 이후 상태 확인 (디버깅용)
st.write("현재 체크박스 상태:", st.session_state["checkboxes"])
