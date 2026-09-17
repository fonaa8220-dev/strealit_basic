import streamlit as st


def show():
    st.header('st.color_picker')

    # color_picker는 색을 고르고 색상 코드를 돌려줍니다.
    color = st.color_picker('좋아하는 색', value='#FF4B4B')
    st.write('선택한 색상 코드:', color)
