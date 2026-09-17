import hashlib
import hmac
import os
import sqlite3
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI


# .env의 OPENAI_API_KEY와 OPENAI_MODEL을 불러옵니다.
load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
DATABASE = os.getenv("CHAT_DB_PATH", "chat_history.db")
CORGI_IMAGE = Path(__file__).parent / "assets" / "chatchat_corgi.svg"
CHAT_STYLE = Path(__file__).parent / "assets" / "chatchat.css"
PASSWORD_ITERATIONS = 600_000
MAX_EXCHANGES = 100
MAX_SESSIONS = 10

st.set_page_config(page_title="ChatChat", page_icon="🐶")


def create_tables():
    """계정과 채팅 테이블을 만들고 이전 채팅 테이블을 업데이트합니다."""
    with sqlite3.connect(DATABASE) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                salt BLOB NOT NULL,
                password_hash BLOB NOT NULL,
                iterations INTEGER NOT NULL
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                username TEXT,
                session_id INTEGER,
                role TEXT,
                text TEXT,
                files TEXT,
                response_id TEXT
            )
        """)
        columns = {row[1] for row in connection.execute("PRAGMA table_info(messages)")}
        if "username" not in columns:
            connection.execute("ALTER TABLE messages ADD COLUMN username TEXT")
        if "session_id" not in columns:
            connection.execute("ALTER TABLE messages ADD COLUMN session_id INTEGER")

        # 기존 사용자별 메시지는 사용자마다 하나의 세션으로 옮깁니다.
        old_users = connection.execute(
            "SELECT DISTINCT username FROM messages WHERE username IS NOT NULL AND session_id IS NULL"
        ).fetchall()
        for (username,) in old_users:
            session_id = connection.execute(
                "INSERT INTO chat_sessions (username) VALUES (?)", (username,)
            ).lastrowid
            connection.execute(
                "UPDATE messages SET session_id = ? WHERE username = ? AND session_id IS NULL",
                (session_id, username),
            )
            trim_session(connection, username, session_id)
            prune_sessions(connection, username)


def trim_session(connection, username, session_id):
    """완료된 최근 100회 대화와 그 이후의 메시지만 남깁니다."""
    replies = connection.execute(
        "SELECT id FROM messages WHERE username = ? AND session_id = ? AND role = 'assistant' "
        "ORDER BY id DESC LIMIT 1 OFFSET ?",
        (username, session_id, MAX_EXCHANGES - 1),
    ).fetchone()
    if not replies:
        return
    oldest_reply_id = replies[0]
    previous_reply = connection.execute(
        "SELECT id FROM messages WHERE username = ? AND session_id = ? "
        "AND role = 'assistant' AND id < ? ORDER BY id DESC LIMIT 1",
        (username, session_id, oldest_reply_id),
    ).fetchone()
    first_message = connection.execute(
        "SELECT id FROM messages WHERE username = ? AND session_id = ? "
        "AND role = 'user' AND id < ? AND id > ? ORDER BY id DESC LIMIT 1",
        (username, session_id, oldest_reply_id, previous_reply[0] if previous_reply else 0),
    ).fetchone()
    connection.execute(
        "DELETE FROM messages WHERE username = ? AND session_id = ? AND id < ?",
        (username, session_id, first_message[0] if first_message else oldest_reply_id),
    )


def prune_sessions(connection, username):
    """사용자의 최근 세션 10개만 남깁니다."""
    old_sessions = connection.execute(
        "SELECT id FROM chat_sessions WHERE username = ? ORDER BY id DESC LIMIT -1 OFFSET ?",
        (username, MAX_SESSIONS),
    ).fetchall()
    for (session_id,) in old_sessions:
        connection.execute(
            "DELETE FROM messages WHERE username = ? AND session_id = ?",
            (username, session_id),
        )
        connection.execute(
            "DELETE FROM chat_sessions WHERE username = ? AND id = ?",
            (username, session_id),
        )


def create_session(username):
    """새 채팅 세션을 만들고 오래된 세션을 정리합니다."""
    with sqlite3.connect(DATABASE) as connection:
        session_id = connection.execute(
            "INSERT INTO chat_sessions (username) VALUES (?)", (username,)
        ).lastrowid
        prune_sessions(connection, username)
    return session_id


def list_sessions(username):
    """사용자의 채팅 세션과 각 세션의 첫 질문을 가져옵니다."""
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


def register_user(username, password):
    """계정을 등록하고 비밀번호는 솔트가 적용된 해시로 저장합니다."""
    salt = os.urandom(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS
    )
    try:
        with sqlite3.connect(DATABASE) as connection:
            connection.execute(
                "INSERT INTO users (username, salt, password_hash, iterations) VALUES (?, ?, ?, ?)",
                (username, salt, password_hash, PASSWORD_ITERATIONS),
            )
    except sqlite3.IntegrityError:
        return False
    return True


def check_password(username, password):
    """입력한 비밀번호와 저장된 해시를 비교합니다."""
    with sqlite3.connect(DATABASE) as connection:
        row = connection.execute(
            "SELECT salt, password_hash, iterations FROM users WHERE username = ?",
            (username,),
        ).fetchone()
    if not row:
        return False
    salt, saved_hash, iterations = row
    entered_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(entered_hash, saved_hash)


def load_history(username, session_id):
    """선택한 세션의 메시지와 마지막 응답 ID를 불러옵니다."""
    with sqlite3.connect(DATABASE) as connection:
        rows = connection.execute(
            "SELECT role, text, response_id FROM messages "
            "WHERE username = ? AND session_id = ? ORDER BY id",
            (username, session_id),
        ).fetchall()

    messages = [
        {"role": role, "text": text}
        for role, text, response_id in rows
    ]
    response_id = next((row[2] for row in reversed(rows) if row[2]), None)
    return messages, response_id


def save_exchange(username, session_id, prompt, answer, response_id):
    """사용자 질문과 AI 답변을 함께 저장하고 오래된 대화를 정리합니다."""
    with sqlite3.connect(DATABASE) as connection:
        connection.execute(
            "INSERT INTO messages (username, session_id, role, text, files) VALUES (?, ?, ?, ?, ?)",
            (username, session_id, "user", prompt, ""),
        )
        connection.execute(
            "INSERT INTO messages (username, session_id, role, text, files, response_id) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (username, session_id, "assistant", answer, "", response_id),
        )
        trim_session(connection, username, session_id)


def clear_history(username):
    """현재 사용자의 채팅 세션과 메시지를 모두 삭제합니다."""
    with sqlite3.connect(DATABASE) as connection:
        connection.execute("DELETE FROM messages WHERE username = ?", (username,))
        connection.execute("DELETE FROM chat_sessions WHERE username = ?", (username,))


@st.dialog("API 키 등록", icon="🔑")
def api_key_dialog():
    """현재 세션에서 사용할 API 키를 등록합니다."""
    corgi_col, text_col = st.columns([1, 4], vertical_alignment="center")
    with corgi_col:
        st.image(CORGI_IMAGE, width=64)
    with text_col:
        st.markdown("**ChatChat에 사용할 키를 입력해 주세요.**")
        st.caption("키는 세션에서만 사용하고 DB에 저장하지 않아요.")

    new_key = st.text_input("OpenAI API 키", type="password", placeholder="API 키를 입력하세요")
    if st.button(
        "키 저장",
        type="primary",
        use_container_width=True,
        disabled=not new_key.strip(),
        key="save_api_key",
    ):
        st.session_state.registered_api_key = new_key.strip()
        st.rerun()

    if st.session_state.get("registered_api_key"):
        if st.button("입력한 키 삭제", use_container_width=True):
            del st.session_state.registered_api_key
            st.rerun()


create_tables()


def login_page():
    st.html(CHAT_STYLE)
    with st.container(key="login_panel"):
        _, corgi_col, _ = st.columns([2, 1, 2])
        with corgi_col:
            st.image(CORGI_IMAGE, width=88)
        st.title("ChatChat")
        login_tab, register_tab = st.tabs(["로그인", "계정 만들기"])
        with login_tab:
            with st.form("login_form"):
                username = st.text_input("닉네임", max_chars=30)
                password = st.text_input("비밀번호", type="password")
                login_clicked = st.form_submit_button("로그인", type="primary", use_container_width=True)
            if login_clicked:
                username = username.strip()
                if check_password(username, password):
                    st.session_state.username = username
                    st.session_state.open_api_key_after_login = True
                    st.rerun()
                else:
                    st.error("닉네임 또는 비밀번호가 올바르지 않습니다.")

        with register_tab:
            with st.form("register_form"):
                new_username = st.text_input("새 닉네임", max_chars=30)
                new_password = st.text_input("새 비밀번호", type="password")
                st.caption("비밀번호는 15자 이상 입력해 주세요.")
                confirm_password = st.text_input("비밀번호 확인", type="password")
                register_clicked = st.form_submit_button("계정 만들기", type="primary", use_container_width=True)
            if register_clicked:
                new_username = new_username.strip()
                if not new_username:
                    st.error("닉네임을 입력해 주세요.")
                elif len(new_password) < 15:
                    st.error("비밀번호를 15자 이상 입력해 주세요.")
                elif new_password != confirm_password:
                    st.error("비밀번호 확인이 일치하지 않습니다.")
                elif not register_user(new_username, new_password):
                    st.error("이미 사용 중인 닉네임입니다.")
                else:
                    st.session_state.username = new_username
                    st.session_state.open_api_key_after_login = True
                    st.rerun()

        st.warning(
            "학습용 로그인입니다. 로그인 시도 제한·계정 잠금·비밀번호 재설정이 없으니 "
            "민감한 정보를 입력하지 마세요."
        )


def chat_page():
    st.html(CHAT_STYLE)
    username = st.session_state.username

    sessions = list_sessions(username)
    if not sessions:
        create_session(username)
        sessions = list_sessions(username)
    session_ids = [session_id for session_id, title in sessions]
    if st.session_state.get("session_id") not in session_ids:
        st.session_state.session_id = session_ids[0]
    if st.session_state.get("selected_session") not in session_ids:
        st.session_state.selected_session = st.session_state.session_id

    st.sidebar.markdown("#### 내 채팅")
    if st.sidebar.button("➕ 새 채팅", use_container_width=True, type="primary"):
        st.session_state.session_id = create_session(username)
        st.session_state.selected_session = st.session_state.session_id
        st.session_state.pop("messages", None)
        st.session_state.pop("response_id", None)
        st.rerun()

    session_titles = {session_id: title for session_id, title in sessions}
    selected_session = st.sidebar.selectbox(
        "채팅 세션",
        session_ids,
        format_func=lambda session_id: f"채팅 {session_id} · {session_titles[session_id]}",
        key="selected_session",
    )
    if selected_session != st.session_state.session_id:
        st.session_state.session_id = selected_session
        st.session_state.pop("messages", None)
        st.session_state.pop("response_id", None)
        st.rerun()
    st.sidebar.caption(f"저장된 채팅: {len(sessions)}/{MAX_SESSIONS}개")

    with st.container(key="chat_header"):
        corgi_col, title_col, history_col = st.columns([1, 5, 2], vertical_alignment="center")
        with corgi_col:
            st.image(CORGI_IMAGE, width=68)
        with title_col:
            st.title("ChatChat")
        with history_col:
            if st.button("🔑 API 키 변경" if api_key else "🔑 API 키 등록", use_container_width=True):
                api_key_dialog()
            st.page_link("app2_history.py", label="과거 내역 보기", icon="📜", use_container_width=True)

    if not api_key:
        with st.container(key="key_notice"):
            st.info("채팅을 시작하려면 위의 API 키 등록 버튼을 눌러 주세요.")

    if "messages" not in st.session_state:
        st.session_state.messages, st.session_state.response_id = load_history(
            username, st.session_state.session_id
        )
    with st.container(key="chat_status"):
        st.caption(
            f"이 채팅: {sum(message['role'] == 'assistant' for message in st.session_state.messages)}"
            f"/{MAX_EXCHANGES}회 대화 저장"
        )

    st.sidebar.divider()
    if st.sidebar.button("채팅 기록 삭제"):
        clear_history(username)
        for key in ("session_id", "selected_session", "messages", "response_id"):
            st.session_state.pop(key, None)
        st.rerun()

    if not st.session_state.messages:
        with st.container(key="empty_chat"):
            _, corgi_col, _ = st.columns([2, 1, 2])
            with corgi_col:
                st.image(CORGI_IMAGE, width=88)
            st.subheader("첫 메시지를 보내보세요")
            st.caption("아래 입력창에 메시지를 적으면 이 채팅이 시작됩니다.")

    # SQLite에서 불러온 이전 채팅을 화면에 표시합니다.
    for message in st.session_state.messages:
        avatar = CORGI_IMAGE if message["role"] == "assistant" else None
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["text"])

    prompt = st.chat_input("메시지를 입력하세요", disabled=not api_key)

    if prompt and api_key:
        with st.chat_message("user"):
            st.markdown(prompt)

        request = {"model": MODEL, "input": prompt}
        if st.session_state.response_id:
            request["previous_response_id"] = st.session_state.response_id

        with st.chat_message("assistant", avatar=CORGI_IMAGE):
            with st.spinner("답변을 생성하는 중..."):
                response = OpenAI(api_key=api_key).responses.create(**request)
            st.markdown(response.output_text)

        # 질문과 답변을 한 번에 저장하고 최근 100회 대화만 유지합니다.
        save_exchange(username, st.session_state.session_id, prompt, response.output_text, response.id)
        st.session_state.messages, st.session_state.response_id = load_history(
            username, st.session_state.session_id
        )
        st.rerun()


if st.session_state.get("username"):
    api_key = st.session_state.get("registered_api_key", "") or os.getenv("OPENAI_API_KEY", "").strip()
    st.sidebar.caption(f"{st.session_state.username}님")
    st.sidebar.caption(f"사용 모델: {MODEL}")
    chat_page_nav = st.Page(chat_page, title="ChatChat", icon="🐶", url_path="chat", default=True)
    history_page_nav = st.Page("app2_history.py", title="과거 채팅 내역", icon="📜", url_path="history")
    pg = st.navigation([chat_page_nav, history_page_nav])
else:
    pg = st.navigation(
        [st.Page(login_page, title="로그인", icon="🐶", default=True)],
        position="hidden",
    )
pg.run()
if st.session_state.get("username"):
    st.sidebar.divider()
    if st.sidebar.button("로그아웃", use_container_width=True):
        for key in (
            "username", "session_id", "selected_session", "messages", "response_id",
            "registered_api_key", "open_api_key_after_login",
        ):
            st.session_state.pop(key, None)
        st.rerun()
if st.session_state.pop("open_api_key_after_login", False):
    api_key_dialog()
