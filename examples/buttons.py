import streamlit as st


def show():
    st.header('st.button')

    # button을 클릭한 순간에만 아래 메시지가 표시됩니다.
    if st.button('인사하기'):
        st.write('안녕하세요!')
