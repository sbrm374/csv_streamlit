import streamlit as st

# 체크박스 상태 초기화
if "checkboxes" not in st.session_state:
    st.session_state["checkboxes"] = {
        f"checkbox_{i}": False for i in range(1, 11)  # 체크박스 1~10
    }

# 체크박스 렌더링
st.title("체크박스 예제")
st.write("체크박스를 선택하세요:")

for i in range(1, 11):
    st.session_state["checkboxes"][f"checkbox_{i}"] = st.checkbox(
        f"체크박스 {i}",
        value=st.session_state["checkboxes"][f"checkbox_{i}"],  # 상태 유지
        key=f"checkbox_{i}"  # 고유 키
    )
