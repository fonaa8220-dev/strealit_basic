import os
import sqlite3

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

DATABASE = os.getenv("CHAT_DB_PATH", "chat_history.db")
UPLOAD_DIR = "uploads"
IMAGE_TYPES = ["png", "jpg", "jpeg", "webp"]


def load_all_messages():
    """SQLite에 저장된 모든 대화 메시지를 불러옵니다."""
    with sqlite3.connect(DATABASE) as connection:
        return connection.execute(
            "SELECT id, role, text, files, response_id FROM messages ORDER BY id ASC"
        ).fetchall()


st.title("과거 채팅 내역")
st.caption("SQLite 데이터베이스에 저장된 이전 대화 기록을 조회합니다.")

rows = load_all_messages()

if not rows:
    st.info("저장된 채팅 내역이 없습니다.")
else:
    # 정렬 및 역할 필터 옵션
    col1, col2 = st.columns(2)
    with col1:
        order = st.radio("정렬 순서", ["오래된 순", "최신순"], horizontal=True)
    with col2:
        role_filter = st.selectbox("역할 필터", ["전체", "user", "assistant"])

    # 정렬 적용
    display_rows = rows if order == "오래된 순" else list(reversed(rows))

    # 필터 적용
    if role_filter != "전체":
        display_rows = [row for row in display_rows if row[1] == role_filter]

    st.caption(f"총 {len(display_rows)}개의 메시지")

    # 대화 내용 표시
    for msg_id, role, text, files, response_id in display_rows:
        with st.chat_message(role):
            st.markdown(text)
            if files:
                for file_name in files.split("|"):
                    file_path = os.path.join(UPLOAD_DIR, file_name)
                    ext = file_name.split(".")[-1].lower()
                    if ext in IMAGE_TYPES and os.path.exists(file_path):
                        st.image(file_path, caption=file_name)
                    else:
                        st.caption("첨부: " + file_name)
            if response_id:
                st.caption(f"응답 ID: {response_id}")

