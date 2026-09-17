import os
import sqlite3
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

DATABASE = os.getenv("CHAT_DB_PATH", "chat_history.db")
CHAT_STYLE = Path(__file__).parent / "assets" / "chatchat.css"


def list_sessions(username):
    """현재 사용자의 채팅 세션을 최신순으로 불러옵니다."""
    with sqlite3.connect(DATABASE) as connection:
        return connection.execute("""
            SELECT s.id,
                   COALESCE((SELECT SUBSTR(text, 1, 25) FROM messages
                             WHERE username = s.username AND session_id = s.id AND role = 'user'
                             ORDER BY id LIMIT 1), '새 채팅')
            FROM chat_sessions AS s
            WHERE s.username = ?
            ORDER BY s.id DESC
        """, (username,)).fetchall()


def load_all_messages(username, session_id):
    """선택한 세션의 대화 메시지를 불러옵니다."""
    with sqlite3.connect(DATABASE) as connection:
        return connection.execute(
            "SELECT id, role, text, response_id FROM messages "
            "WHERE username = ? AND session_id = ? ORDER BY id ASC",
            (username, session_id),
        ).fetchall()


st.html(CHAT_STYLE)
with st.container(key="history_header"):
    st.title("과거 채팅 내역")
    st.caption("저장된 대화를 세션별로 살펴보세요.")

if not st.session_state.get("username"):
    st.warning("로그인 후 채팅 내역을 볼 수 있습니다.")
    st.stop()

sessions = list_sessions(st.session_state.username)
if not sessions:
    st.info("저장된 채팅 세션이 없습니다.")
    st.stop()

with st.container(key="history_filters"):
    session_ids = [session_id for session_id, title in sessions]
    session_titles = {session_id: title for session_id, title in sessions}
    current_session = st.session_state.get("session_id")
    selected_session = st.selectbox(
        "채팅 세션",
        session_ids,
        index=session_ids.index(current_session) if current_session in session_ids else 0,
        format_func=lambda session_id: f"채팅 {session_id} · {session_titles[session_id]}",
    )
    rows = load_all_messages(st.session_state.username, selected_session)
    if rows:
        col1, col2 = st.columns(2)
        with col1:
            order = st.radio("정렬 순서", ["오래된 순", "최신순"], horizontal=True)
        with col2:
            role_filter = st.selectbox("역할 필터", ["전체", "내 메시지", "AI 답변"])

if not rows:
    with st.container(key="history_empty"):
        st.info("저장된 채팅 내역이 없습니다.")
else:
    # 정렬 적용
    display_rows = rows if order == "오래된 순" else list(reversed(rows))

    # 필터 적용
    roles = {"내 메시지": "user", "AI 답변": "assistant"}
    if role_filter in roles:
        display_rows = [row for row in display_rows if row[1] == roles[role_filter]]

    st.caption(f"총 {len(display_rows)}개의 메시지")

    # 대화 내용 표시
    for msg_id, role, text, response_id in display_rows:
        with st.chat_message(role):
            st.markdown(text)
            if response_id:
                st.caption(f"응답 ID: {response_id}")
