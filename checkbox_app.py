import streamlit as st

# 체크박스 상태 초기화
if "checkboxes" not in st.session_state:
    st.session_state["checkboxes"] = {f"checkbox_{i}": False for i in range(1, 11)}

# 초기화 버튼
st.title("체크박스 초기화 버튼")
st.write("모든 체크박스를 해제하려면 아래 버튼을 누르세요:")

if st.button("초기화"):
    # 상태 초기화
    for i in range(1, 11):
        st.session_state["checkboxes"][f"checkbox_{i}"] = False
    # 강제로 UI 새로고침
    st.experimental_rerun()

# 체크박스 렌더링
st.title("체크박스 예제")
st.write("체크박스를 선택하세요:")

for i in range(1, 11):
    checkbox_key = f"checkbox_{i}"
    # 강제 동기화와 렌더링
    current_value = st.session_state["checkboxes"][checkbox_key]
    updated_value = st.checkbox(
        f"체크박스 {i}",
        value=current_value,  # 상태 유지
        key=checkbox_key
    )
    # 상태가 변경된 경우 동기화
    if updated_value != current_value:
        st.session_state["checkboxes"][checkbox_key] = updated_value

# 상태 디버깅 출력
st.write("현재 체크박스 상태:", st.session_state["checkboxes"])
