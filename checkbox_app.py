import streamlit as st

# 체크박스 상태 초기화
if "checkboxes" not in st.session_state:
    st.session_state["checkboxes"] = {f"checkbox_{i}": False for i in range(1, 11)}
    st.write("초기화: 세션 상태가 생성되었습니다.", st.session_state["checkboxes"])  # 초기화 로그

# 초기화 버튼
st.title("체크박스 초기화 버튼")
st.write("모든 체크박스를 해제하려면 아래 버튼을 누르세요:")

if st.button("초기화"):
    st.write("초기화 버튼이 클릭되었습니다.")  # 초기화 버튼 로그
    for i in range(1, 11):
        st.session_state["checkboxes"][f"checkbox_{i}"] = False
        st.write(f"초기화 후 체크박스 {i} 상태: {st.session_state['checkboxes'][f'checkbox_{i}']}")  # 상태 확인 로그

# 체크박스 렌더링
st.title("체크박스 예제")
st.write("체크박스를 선택하세요:")

for i in range(1, 11):
    checkbox_key = f"checkbox_{i}"
    current_value = st.session_state["checkboxes"][checkbox_key]
    
    # 렌더링 전 상태 확인
    st.write(f"렌더링 전 체크박스 {i} 상태: {current_value}")
    
    # 체크박스 렌더링 및 값 업데이트
    updated_value = st.checkbox(
        f"체크박스 {i}",
        value=current_value,  # 상태 유지
        key=checkbox_key
    )
    
    # 렌더링 후 상태 확인
    st.write(f"렌더링 후 체크박스 {i} 상태: {updated_value}")

    # 상태 동기화 로그
    if updated_value != current_value:
        st.write(f"체크박스 {i} 상태가 변경되었습니다. 업데이트 중...")
        st.session_state["checkboxes"][checkbox_key] = updated_value
        st.write(f"업데이트 후 체크박스 {i} 상태: {st.session_state['checkboxes'][checkbox_key]}")

# 최종 상태 확인
st.write("현재 체크박스 상태:", st.session_state["checkboxes"])
