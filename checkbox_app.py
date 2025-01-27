import streamlit as st

# 체크박스 상태 초기화
if "checkboxes" not in st.session_state:
    st.session_state["checkboxes"] = {f"checkbox_{i}": False for i in range(1, 11)}

# 초기화 버튼
st.title("체크박스 초기화 버튼")
st.write("모든 체크박스를 해제하려면 아래 버튼을 누르세요:")

if st.button("초기화"):
    st.write("초기화 버튼이 클릭되었습니다.")
    
    # 모든 체크박스를 False로 강제 초기화
    for i in range(1, 11):
        st.session_state["checkboxes"][f"checkbox_{i}"] = False

    # 강제 상태 갱신 로그
    for i in range(1, 11):
        st.write(f"초기화 후 체크박스 {i} 상태: {st.session_state['checkboxes'][f'checkbox_{i}']}")

# 체크박스 렌더링
st.title("체크박스 예제")
st.write("체크박스를 선택하세요:")

# 체크박스 렌더링 및 상태 동기화
for i in range(1, 11):
    checkbox_key = f"checkbox_{i}"

    # 렌더링 전에 상태 로그
    st.write(f"렌더링 전 체크박스 {i} 상태: {st.session_state['checkboxes'][checkbox_key]}")

    # 체크박스 렌더링
    st.checkbox(
        f"체크박스 {i}",
        value=st.session_state["checkboxes"][checkbox_key],
        key=checkbox_key
    )
