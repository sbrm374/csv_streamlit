import streamlit as st

# 체크박스 상태 초기화
if "checkboxes" not in st.session_state:
    st.session_state["checkboxes"] = {f"checkbox_{i}": False for i in range(1, 11)}

# 초기화 버튼
st.title("체크박스 초기화 버튼")
st.write("모든 체크박스를 해제하려면 아래 버튼을 누르세요:")

if st.button("초기화"):
    # 모든 체크박스를 False로 설정 (초기화)
    for i in range(1, 11):
        checkbox_key = f"checkbox_{i}"
        st.session_state["checkboxes"][checkbox_key] = False

    # 동기화를 강제로 유도
    st.rerun()

# 체크박스 렌더링
st.title("체크박스 예제")
st.write("체크박스를 선택하세요:")

for i in range(1, 11):
    checkbox_key = f"checkbox_{i}"

    # 렌더링
    new_value = st.checkbox(
        f"체크박스 {i}",
        value=st.session_state["checkboxes"][checkbox_key],
        key=checkbox_key
    )
    
    # 값이 변경된 경우 세션 상태를 업데이트
    if new_value != st.session_state["checkboxes"][checkbox_key]:
        st.session_state["checkboxes"][checkbox_key] = new_value

# 상태 디버그 출력
st.write("현재 체크박스 상태:", st.session_state["checkboxes"])
