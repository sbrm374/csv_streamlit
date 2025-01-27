import streamlit as st

# 체크박스 상태 초기화
if "checkboxes" not in st.session_state:
    st.session_state["checkboxes"] = {f"checkbox_{i}": False for i in range(1, 11)}

# 마지막으로 선택된 체크박스를 저장하기 위한 변수
if "last_checkbox" not in st.session_state:
    st.session_state["last_checkbox"] = None

# 초기화 버튼
st.title("체크박스 초기화 버튼")
st.write("모든 체크박스를 해제하려면 아래 버튼을 누르세요:")

if st.button("초기화"):
    st.write("초기화 버튼이 클릭되었습니다.")

    # 마지막 체크박스를 강제로 트리거하는 효과
    if st.session_state["last_checkbox"]:
        last_checkbox_key = st.session_state["last_checkbox"]
        st.session_state["checkboxes"][last_checkbox_key] = not st.session_state["checkboxes"][last_checkbox_key]
        st.write(f"마지막 체크박스 {last_checkbox_key} 상태를 강제로 갱신: {st.session_state['checkboxes'][last_checkbox_key]}")

    # 상태 초기화
    for i in range(1, 11):
        st.session_state["checkboxes"][f"checkbox_{i}"] = False

    st.write("초기화 후 상태:", st.session_state["checkboxes"])

# 체크박스 렌더링
st.title("체크박스 예제")
st.write("체크박스를 선택하세요:")

for i in range(1, 11):
    checkbox_key = f"checkbox_{i}"

    # 렌더링 전 상태를 명시적으로 동기화
    current_value = st.session_state["checkboxes"][checkbox_key]
    st.write(f"렌더링 전 체크박스 {i} 상태: {current_value}")

    # 체크박스 렌더링
    new_value = st.checkbox(
        f"체크박스 {i}",
        value=current_value,
        key=checkbox_key
    )

    # 상태가 변경된 경우 업데이트
    if new_value != current_value:
        st.session_state["checkboxes"][checkbox_key] = new_value
        st.session_state["last_checkbox"] = checkbox_key  # 마지막으로 선택된 체크박스 기록
        st.write(f"체크박스 {i} 상태가 변경되었습니다. 업데이트 중...")
        st.write(f"업데이트 후 체크박스 {i} 상태: {st.session_state['checkboxes'][checkbox_key]}")

# 최종 상태 출력
st.write("현재 체크박스 상태:", st.session_state["checkboxes"])
