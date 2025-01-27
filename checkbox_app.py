import streamlit as st

# 체크박스 상태 초기화
if "checkboxes" not in st.session_state:
    st.session_state["checkboxes"] = {f"checkbox_{i}": False for i in range(1, 11)}

# 동기화를 위한 radio 상태 초기화
if "sync_radio" not in st.session_state:
    st.session_state["sync_radio"] = "None"

# 초기화 버튼
st.title("체크박스 초기화 버튼")
st.write("모든 체크박스를 해제하려면 아래 버튼을 누르세요:")

if st.button("초기화"):
    # Syncing 상태로 변경
    st.session_state.sync_radio = "Syncing"
    st.write(f"동기화 상태를 'Syncing'으로 변경: {st.session_state['sync_radio']}")

    # 초기화: 모든 체크박스를 False로 설정
    for i in range(1, 11):
        checkbox_key = f"checkbox_{i}"
        st.session_state["checkboxes"][checkbox_key] = False

    # 초기화 후 상태 출력
    st.write("초기화 후 상태:", st.session_state["checkboxes"])

# 체크박스 렌더링 함수
def render_checkboxes():
    for i in range(1, 11):
        checkbox_key = f"checkbox_{i}"
        # 체크박스 렌더링
        current_value = st.checkbox(
            f"체크박스 {i}",
            value=st.session_state["checkboxes"][checkbox_key],
            key=checkbox_key,
        )
        # 상태 동기화
        st.session_state["checkboxes"][checkbox_key] = current_value

# 체크박스 렌더링 호출
st.title("체크박스 예제")
st.write("체크박스를 선택하세요:")

# 렌더링 체크박스
render_checkboxes()

# 동기화 상태 확인을 위한 radio
selected_radio = st.radio(
    "동기화 상태:",
    options=["None", "Syncing"],
    index=0 if st.session_state["sync_radio"] == "None" else 1,
    key="sync_radio",
)

# 상태 디버그 출력
st.write("현재 체크박스 상태:", st.session_state["checkboxes"])
st.write("현재 동기화 상태:", st.session_state["sync_radio"])
