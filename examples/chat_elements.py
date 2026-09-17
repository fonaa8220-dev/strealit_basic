import streamlit as st


def show_chat_message():
    st.header('st.chat_message')
    # 사용자와 앱의 메시지를 서로 다른 말풍선으로 표시합니다.
    with st.chat_message('user'):
        st.write('안녕하세요!')
    with st.chat_message('assistant'):
        st.write('무엇을 도와드릴까요?')


def show_chat_input():
    st.header('st.chat_input')
    # 탭 안에서 메시지를 입력하면 바로 아래에 표시합니다.
    prompt = st.chat_input('메시지를 입력하세요')
    if prompt:
        with st.chat_message('user'):
            st.write(prompt)


def show():
    examples = [
        ('st.chat_message', show_chat_message),
        ('st.chat_input', show_chat_input),
    ]

    tabs = st.tabs([name for name, _ in examples], key='chat_tabs', on_change='rerun')
    for tab, (_, show_example) in zip(tabs, examples):
        if tab.open:
            with tab:
                show_example()
