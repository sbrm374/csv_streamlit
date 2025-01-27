import streamlit as st

# 체크박스 상태 초기화
if "checkboxes" not in st.session_state:
    st.session_state["checkboxes"] = {f"checkbox_{i}": False for i in range(1, 11)}

# 초기화 버튼
st.title("체크박스 초기화 버튼")
st.write("모든 체크박스를 해제하려면 아래 버튼을 누르세요:")

# 초기화 버튼 클릭 시
if st.button("초기화"):
    for i in range(1, 11):
        checkbox_key = f"checkbox_{i}"
        # 강제로 True -> False로 두 번 갱신
        st.session_state["checkboxes"][checkbox_key] = True
        st.session_state["checkboxes"][checkbox_key] = False

    st.write("초기화 후 상태:", st.session_state["checkboxes"])

# 체크박스 렌더링
st.title("체크박스 예제")
st.write("체크박스를 선택하세요:")

for i in range(1, 11):
    checkbox_key = f"checkbox_{i}"

    # 렌더링 전 상태 로그
    st.write(f"렌더링 전 체크박스 {i} 상태: {st.session_state['checkboxes'][checkbox_key]}")

    # 체크박스 렌더링
    new_value = st.checkbox(
        f"체크박스 {i}",
        value=st.session_state["checkboxes"][checkbox_key],
        key=checkbox_key
    )

    # 렌더링 후 상태 동기화
    if new_value != st.session_state["checkboxes"][checkbox_key]:
        st.write(f"체크박스 {i} 상태가 변경되었습니다. 업데이트 중...")
        st.session_state["checkboxes"][checkbox_key] = new_value

    # 렌더링 후 상태 로그
    st.write(f"렌더링 후 체크박스 {i} 상태: {st.session_state['checkboxes'][checkbox_key]}")

# 최종 상태 디버그 출력
st.write("현재 체크박스 상태:", st.session_state["checkboxes"])
