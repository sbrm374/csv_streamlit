import streamlit as st

# 체크박스 상태 초기화
if "checkboxes" not in st.session_state:
    st.session_state["checkboxes"] = {f"checkbox_{i}": False for i in range(1, 11)}

def render_checkboxes():
    """체크박스를 렌더링하고 상태를 UI와 동기화"""
    for i in range(1, 11):
        checkbox_key = f"checkbox_{i}"
        # 현재 상태 가져오기
        current_value = st.session_state["checkboxes"][checkbox_key]
        
        # 체크박스 렌더링
        new_value = st.checkbox(
            f"체크박스 {i}",
            value=current_value,
            key=checkbox_key
        )
        
        # 상태 변경 시 업데이트
        if new_value != current_value:
            st.session_state["checkboxes"][checkbox_key] = new_value
            st.write(f"체크박스 {i} 상태가 변경되었습니다. 업데이트 중...")

# 초기화 버튼
st.title("체크박스 초기화 버튼")
st.write("모든 체크박스를 해제하려면 아래 버튼을 누르세요:")

if st.button("초기화"):
    st.write("초기화 버튼이 클릭되었습니다.")
    
    # 모든 체크박스 상태를 False로 초기화
    for i in range(1, 11):
        checkbox_key = f"checkbox_{i}"
        st.session_state["checkboxes"][checkbox_key] = False

    # 상태 확인 로그
    st.write("초기화 후 상태:", st.session_state["checkboxes"])

# 체크박스 렌더링
st.title("체크박스 예제")
st.write("체크박스를 선택하세요:")

render_checkboxes()

# 최종 상태 출력
st.write("현재 체크박스 상태:", st.session_state["checkboxes"])
