import streamlit as st

# 체크박스 상태 초기화
if "checkboxes" not in st.session_state:
    st.session_state["checkboxes"] = {f"checkbox_{i}": False for i in range(1, 11)}

# 체크박스 상태 강제 동기화 함수
def sync_checkboxes():
    for i in range(1, 11):
        checkbox_key = f"checkbox_{i}"
        # 현재 UI 상태를 강제로 읽어와서 동기화
        st.session_state["checkboxes"][checkbox_key] = st.checkbox(
            f"체크박스 {i}",
            value=st.session_state["checkboxes"][checkbox_key],
            key=checkbox_key,
        )

# 초기화 버튼
st.title("체크박스 초기화 버튼")
st.write("모든 체크박스를 해제하려면 아래 버튼을 누르세요:")

if st.button("초기화"):
    st.write("초기화 버튼이 클릭되었습니다.")
    
    # 체크박스 상태를 강제로 동기화
    sync_checkboxes()
    st.write("모든 체크박스 상태를 동기화했습니다.")

    # 모든 체크박스 초기화
    for i in range(1, 11):
        st.session_state["checkboxes"][f"checkbox_{i}"] = False

# 체크박스 렌더링
st.title("체크박스 예제")
st.write("체크박스를 선택하세요:")

# 체크박스 렌더링 및 상태 확인
for i in range(1, 11):
    checkbox_key = f"checkbox_{i}"
    current_value = st.session_state["checkboxes"][checkbox_key]
    st.write(f"렌더링 전 체크박스 {i} 상태: {current_value}")

    # 체크박스 UI 렌더링
    updated_value = st.checkbox(
        f"체크박스 {i}",
        value=current_value,
        key=checkbox_key,
    )

    # 상태 업데이트
    if updated_value != current_value:
        st.session_state["checkboxes"][checkbox_key] = updated_value
        st.write(f"체크박스 {i} 상태가 변경되었습니다. 업데이트 중...")

# 최종 상태 출력
st.write("현재 체크박스 상태:", st.session_state["checkboxes"])
