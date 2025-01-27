import streamlit as st

# 체크박스 상태 초기화
if "checkboxes" not in st.session_state:
    st.session_state["checkboxes"] = {f"checkbox_{i}": False for i in range(1, 11)}

# 체크박스 렌더링
st.title("체크박스 예제")
st.write("체크박스를 선택하세요:")

for i in range(1, 11):
    st.session_state["checkboxes"][f"checkbox_{i}"] = st.checkbox(
        f"체크박스 {i}",
        value=st.session_state["checkboxes"][f"checkbox_{i}"],  # 상태 유지
        key=f"checkbox_{i}"  # 고유 키
    )

# 초기화 버튼
st.title("체크박스 초기화 버튼")
st.write("모든 체크박스를 해제하려면 아래 버튼을 누르세요:")

# 초기화 버튼
if st.button("초기화"):
    for i in range(1, 11):
        st.session_state["checkboxes"][f"checkbox_{i}"] = False  # 상태 초기화
    st.rerun()  # UI 강제 새로고침

for i in range(1, 11):
    st.checkbox(
        f"체크박스 {i}",
        value=st.session_state["checkboxes"][f"checkbox_{i}"],  # 상태 동기화
        key=f"checkbox_{i}"  # 고유 키
    )
