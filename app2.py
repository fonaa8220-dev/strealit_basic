import base64
import os
import sqlite3

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI


# .env의 OPENAI_API_KEY와 OPENAI_MODEL을 불러옵니다.
load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
DATABASE = os.getenv("CHAT_DB_PATH", "chat_history.db")
IMAGE_TYPES = ["png", "jpg", "jpeg", "webp"]
FILE_TYPES = ["pdf", "txt", "md", "docx", "csv", "xlsx", "pptx"]
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def create_table():
    """채팅 메시지를 저장할 테이블을 만듭니다."""
    with sqlite3.connect(DATABASE) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                role TEXT,
                text TEXT,
                files TEXT,
                response_id TEXT
            )
        """)


def load_history():
    """SQLite에 저장된 메시지와 마지막 응답 ID를 불러옵니다."""
    with sqlite3.connect(DATABASE) as connection:
        rows = connection.execute(
            "SELECT role, text, files, response_id FROM messages ORDER BY id"
        ).fetchall()

    messages = [
        {"role": role, "text": text, "files": files.split("|") if files else []}
        for role, text, files, response_id in rows
    ]
    response_id = next((row[3] for row in reversed(rows) if row[3]), None)
    return messages, response_id


def save_message(role, text, files=[], response_id=None):
    """메시지 한 개를 SQLite에 저장합니다."""
    with sqlite3.connect(DATABASE) as connection:
        connection.execute(
            "INSERT INTO messages (role, text, files, response_id) VALUES (?, ?, ?, ?)",
            (role, text, "|".join(files), response_id),
        )


def clear_history():
    """SQLite에 저장된 모든 채팅 메시지를 삭제합니다."""
    with sqlite3.connect(DATABASE) as connection:
        connection.execute("DELETE FROM messages")


@st.dialog("이미지 업로드")
def image_upload_dialog():
    """이미지를 드래그 앤 드롭으로 고르는 팝업입니다."""
    images = st.file_uploader(
        "이미지를 여기에 끌어 놓거나 파일을 선택하세요.",
        type=IMAGE_TYPES,
        accept_multiple_files=True,
        key="image_uploader",
    )
    if st.button("이미지 첨부"):
        st.session_state.pending_images = images
        st.rerun()


@st.dialog("파일 업로드")
def file_upload_dialog():
    """문서 파일을 고르는 팝업입니다."""
    files = st.file_uploader(
        "파일을 여기에 끌어 놓거나 파일을 선택하세요.",
        type=FILE_TYPES,
        accept_multiple_files=True,
        key="file_uploader",
    )
    if st.button("파일 첨부"):
        st.session_state.pending_files = files
        st.rerun()


create_table()


def chat_page():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("OpenAI 채팅")
        st.caption(f".env에서 불러온 모델: {MODEL}")
    with col2:
        st.write("")
        st.page_link("app2_history.py", label="과거 내역 보기", icon="📜", use_container_width=True)

    if "messages" not in st.session_state:
        st.session_state.messages, st.session_state.response_id = load_history()

    if "pending_images" not in st.session_state:
        st.session_state.pending_images = []

    if "pending_files" not in st.session_state:
        st.session_state.pending_files = []

    st.sidebar.page_link("app2_history.py", label="과거 채팅 내역 보기", icon="📜")
    if st.sidebar.button("채팅 기록 삭제"):
        clear_history()
        st.session_state.messages = []
        st.session_state.response_id = None
        st.rerun()

    # SQLite에서 불러온 이전 채팅을 화면에 표시합니다.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["text"])
            for file_name in message["files"]:
                file_path = os.path.join(UPLOAD_DIR, file_name)
                ext = file_name.split(".")[-1].lower()
                if ext in IMAGE_TYPES and os.path.exists(file_path):
                    st.image(file_path, caption=file_name)
                else:
                    st.caption("첨부: " + file_name)

    # 이미지와 문서 파일은 각각의 버튼에서 따로 첨부합니다.
    image_button, file_button = st.columns(2)
    with image_button:
        if st.button("이미지 업로드", use_container_width=True):
            image_upload_dialog()
    with file_button:
        if st.button("파일 업로드", use_container_width=True):
            file_upload_dialog()

    attachments = st.session_state.pending_images + st.session_state.pending_files
    if attachments:
        st.caption("보낼 첨부: " + ", ".join(file.name for file in attachments))
        for img in st.session_state.pending_images:
            st.image(img, caption=f"첨부할 이미지: {img.name}", width=150)

    prompt = st.chat_input("메시지를 입력하세요")

    if prompt:
        text = prompt
        file_names = [file.name for file in attachments]
        # 첨부된 파일을 uploads 폴더에 저장합니다.
        for file in attachments:
            save_path = os.path.join(UPLOAD_DIR, file.name)
            with open(save_path, "wb") as f:
                f.write(file.getbuffer())

        message = {"role": "user", "text": text, "files": file_names}
        st.session_state.messages.append(message)
        save_message("user", text, file_names)

        with st.chat_message("user"):
            st.markdown(text)
            for file in attachments:
                ext = file.name.split(".")[-1].lower()
                if ext in IMAGE_TYPES:
                    st.image(file, caption=file.name)
                else:
                    st.caption("첨부: " + file.name)

        # 이미지는 이미지 입력으로, 문서는 파일 입력으로 Responses API에 보냅니다.
        content = [{"type": "input_text", "text": text}]
        for file in attachments:
            encoded = base64.b64encode(file.getvalue()).decode("utf-8")
            data_url = f"data:{file.type};base64,{encoded}"
            if file.type.startswith("image/"):
                content.append({"type": "input_image", "image_url": data_url})
            else:
                content.append({"type": "input_file", "filename": file.name, "file_data": data_url})

        request = {"model": MODEL, "input": [{"role": "user", "content": content}]}
        if st.session_state.response_id:
            request["previous_response_id"] = st.session_state.response_id

        with st.chat_message("assistant"):
            with st.spinner("답변을 생성하는 중..."):
                response = OpenAI().responses.create(**request)
            st.markdown(response.output_text)

        # 마지막 응답 ID와 답변을 SQLite에 저장해 다음 실행에도 대화를 이어갑니다.
        st.session_state.response_id = response.id
        assistant_message = {"role": "assistant", "text": response.output_text, "files": []}
        st.session_state.messages.append(assistant_message)
        save_message("assistant", response.output_text, response_id=response.id)
        st.session_state.pending_images = []
        st.session_state.pending_files = []


# st.navigation을 사용해 채팅 페이지와 과거 채팅 내역 페이지를 구성합니다.
chat_page_nav = st.Page(chat_page, title="채팅", icon="💬", url_path="chat", default=True)
history_page_nav = st.Page("app2_history.py", title="과거 채팅 내역", icon="📜", url_path="history")

pg = st.navigation([chat_page_nav, history_page_nav])
st.set_page_config(page_title="OpenAI 채팅", page_icon="💬")
pg.run()
