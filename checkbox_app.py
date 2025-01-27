import streamlit as st

# 체크박스 상태 초기화
if "checkboxes" not in st.session_state:
    st.session_state["checkboxes"] = {f"checkbox_{i}": False for i in range(1, 11)}

def sync_checkboxes():
    """체크박스를 렌더링하며 상태를 강제로 동기화합니다."""
    for i in range(1, 11):
        checkbox_key = f"checkbox_{i}"
        # 현재 상태 확인
        current_value = st.checkbox(
            f"체크박스 {i}",
            value=st.session_state["checkboxes"][checkbox_key],
            key=checkbox_key
        )
        # 상태 업데이트
        st.session_state["checkboxes"][checkbox_key] = current_value

# 초기화 버튼
st.title("체크박스 초기화 버튼")
st.write("모든 체크박스를 해제하려면 아래 버튼을 누르세요:")

if st.button("초기화"):
    # 모든 체크박스를 False로 설정
    for i in range(1, 11):
        st.session_state["checkboxes"][f"checkbox_{i}"] = False
    # 초기화를 강제로 UI에 반영
    st.write("초기화 후 상태:", st.session_state["checkboxes"])

    # 체크박스 렌더링 전후 상태 확인
    for i in range(1, 11):
        checkbox_key = f"checkbox_{i}"
        st.write(f"렌더링 전 체크박스 {i} 상태:", st.session_state["checkboxes"][checkbox_key])
        # 렌더링 수행
        st.session_state["checkboxes"][checkbox_key] = st.checkbox(
            f"체크박스 {i}",
            value=st.session_state["checkboxes"][checkbox_key],
            key=checkbox_key
        )
        st.write(f"렌더링 후 체크박스 {i} 상태:", st.session_state["checkboxes"][checkbox_key])
        
# 체크박스 렌더링
st.title("체크박스 예제")
st.write("체크박스를 선택하세요:")

# 렌더링 및 동기화
sync_checkboxes()

# 상태 디버그 출력
st.write("현재 체크박스 상태:", st.session_state["checkboxes"])
