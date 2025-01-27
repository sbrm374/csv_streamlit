import streamlit as st

# 체크박스 상태 초기화
if "checkboxes" not in st.session_state:
    st.session_state["checkboxes"] = {f"checkbox_{i}": False for i in range(1, 11)}

# 고유 키 관리용 상태 추가
if "unique_keys" not in st.session_state:
    st.session_state["unique_keys"] = {f"checkbox_{i}": f"checkbox_{i}" for i in range(1, 11)}

# 초기화 버튼
st.title("체크박스 초기화 버튼")
st.write("모든 체크박스를 해제하려면 아래 버튼을 누르세요:")

if st.button("초기화"):
    # 모든 체크박스를 False로 설정
    for i in range(1, 11):
        checkbox_key = f"checkbox_{i}"
        # 체크박스 키를 변경하여 Streamlit이 강제로 렌더링하도록 강제
        st.session_state["unique_keys"][checkbox_key] += "_updated"
        st.session_state["checkboxes"][checkbox_key] = False
    
    # UI 강제 재실행
    st.rerun()

# 체크박스 렌더링 함수
def render_checkboxes():
    for i in range(1, 11):
        checkbox_key = f"checkbox_{i}"
        # 동적으로 변경된 키를 사용하여 체크박스 생성
        new_key = st.session_state["unique_keys"][checkbox_key]
        current_value = st.checkbox(
            f"체크박스 {i}",
            value=st.session_state["checkboxes"][checkbox_key],
            key=new_key,
        )
        # 상태 동기화
        st.session_state["checkboxes"][checkbox_key] = current_value

# 체크박스 렌더링 호출
st.title("체크박스 예제")
st.write("체크박스를 선택하세요:")
render_checkboxes()

# 상태 디버그 출력
st.write("현재 체크박스 상태:", st.session_state["checkboxes"])
