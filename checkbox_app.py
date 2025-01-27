import streamlit as st

# 체크박스 상태 초기화
if "checkboxes" not in st.session_state:
    st.session_state["checkboxes"] = {f"checkbox_{i}": False for i in range(1, 11)}

# 초기화 버튼
st.title("체크박스 초기화 버튼")
st.write("모든 체크박스를 해제하려면 아래 버튼을 누르세요:")

if st.button("초기화"):
    # 모든 체크박스를 False로 설정
    for i in range(1, 11):
        checkbox_key = f"checkbox_{i}"
        st.session_state["checkboxes"][checkbox_key] = False

    # 강제로 UI 동기화
    st.write("초기화 후 상태:", st.session_state["checkboxes"])

# 체크박스 렌더링 함수
def render_checkboxes():
    for i in range(1, 11):
        checkbox_key = f"checkbox_{i}"
        # 렌더링 전 상태 출력
        st.write(f"렌더링 전 체크박스 {i} 상태: {st.session_state['checkboxes'][checkbox_key]}")
        # 체크박스 렌더링
        current_value = st.checkbox(
            f"체크박스 {i}",
            value=st.session_state["checkboxes"][checkbox_key],
            key=checkbox_key,
        )
        # 상태 동기화
        if current_value != st.session_state["checkboxes"][checkbox_key]:
            st.session_state["checkboxes"][checkbox_key] = current_value
            st.write(f"체크박스 {i} 상태가 변경되었습니다. 업데이트 중...")
        # 렌더링 후 상태 출력
        st.write(f"렌더링 후 체크박스 {i} 상태: {st.session_state['checkboxes'][checkbox_key]}")

# 체크박스 렌더링 호출
st.title("체크박스 예제")
st.write("체크박스를 선택하세요:")
render_checkboxes()

# 상태 디버그 출력
st.write("현재 체크박스 상태:", st.session_state["checkboxes"])
