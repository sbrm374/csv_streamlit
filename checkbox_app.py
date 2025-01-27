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

    # 렌더링 후 강제 동기화
    if new_value != st.session_state["checkboxes"][checkbox_key]:
        st.write(f"체크박스 {i} 상태가 변경되었습니다. 업데이트 중...")
        st.session_state["checkboxes"][checkbox_key] = new_value
    else:
        # 마지막 단계에서 강제 False로 동기화
        st.session_state["checkboxes"][checkbox_key] = False

    # 렌더링 후 상태 로그
    st.write(f"렌더링 후 체크박스 {i} 상태: {st.session_state['checkboxes'][checkbox_key]}")

if st.button("초기화"):
    for i in range(1, 11):
        checkbox_key = f"checkbox_{i}"
        # 강제 갱신 두 번 실행
        st.session_state["checkboxes"][checkbox_key] = True
        st.session_state["checkboxes"][checkbox_key] = False

    st.write("초기화 후 상태:", st.session_state["checkboxes"])
