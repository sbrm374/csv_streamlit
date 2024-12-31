import streamlit as st
import pandas as pd
import os

# CSV 파일 경로 설정 (실제 파일 경로를 지정해야 합니다)
csv_file_path = "data.csv"

st.title("CSV 파일 업데이트 📝")

# CSV 파일 존재 여부 확인
if os.path.exists(csv_file_path):
    df = pd.read_csv(csv_file_path)
    st.write("📄 현재 CSV 파일 내용:")
    st.dataframe(df)
else:
    st.warning(f"'{csv_file_path}' 파일이 존재하지 않습니다.")
    df = pd.DataFrame()  # 빈 DataFrame 생성

# 새 행 추가 폼
st.write("📝 새 행 추가")
new_row = {}
if not df.empty:
    for column in df.columns:
        new_row[column] = st.text_input(f"새로운 {column} 값 입력:", key=column)
else:
    st.info("새로운 열 이름들을 입력하세요.")
    columns = st.text_input("열 이름 (쉼표로 구분):")
    if columns:
        df = pd.DataFrame(columns=[col.strip() for col in columns.split(",")])

if st.button("새 행 추가"):
    if new_row:
        df = df.append(new_row, ignore_index=True)
        st.success("새 행이 추가되었습니다!")
        st.dataframe(df)

        # CSV 파일에 저장
        df.to_csv(csv_file_path, index=False)
        st.success(f"내용이 '{csv_file_path}'에 저장되었습니다!")
    else:
        st.warning("모든 열에 값을 입력해주세요.")

# CSV 파일 저장 버튼
if st.button("CSV 파일 다운로드"):
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="💾 수정된 파일 다운로드",
        data=csv,
        file_name="updated_file.csv",
        mime="text/csv",
    )
