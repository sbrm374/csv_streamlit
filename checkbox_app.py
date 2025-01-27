import streamlit as st

# 체크박스 상태 초기화
if "checkboxes" not in st.session_state:
    st.session_state["checkboxes"] = {f"checkbox_{i}": False for i in range(1, 11)}

# 체크박스 렌더링
st.title("체크박스 예제")
st.write("체크박스를 선택하세요:")

for i in range(1, 11):
    checkbox_key = f"checkbox_{i}"
    
    # 현재 상태 가져오기
    checkbox_state = st.session_state["checkboxes"][checkbox_key]
    
    # 체크박스 렌더링 및 선택 시 추가 행동
    new_state = st.checkbox(
        f"체크박스 {i}",
        value=checkbox_state,  # 현재 상태 유지
        key=checkbox_key  # 고유 키
    )
    
    # 새로운 상태가 이전 상태와 다르면 동기화 및 추가 동작
    if new_state != checkbox_state:
        st.session_state["checkboxes"][checkbox_key] = new_state
        # 체크박스가 선택되거나 해제되었을 때 메시지 출력
        action = "선택됨" if new_state else "해제됨"
        st.write(f"체크박스 {i}이(가) {action}")

# 초기화 버튼
st.title("체크박스 초기화 버튼")
st.write("모든 체크박스를 해제하려면 아래 버튼을 누르세요:")

if st.button("초기화"):
    # 모든 체크박스 상태 초기화
    for i in range(1, 11):
        st.session_state["checkboxes"][f"checkbox_{i}"] = False
    st.experimental_rerun()  # UI 강제 새로고침
