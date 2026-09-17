import streamlit as st


def show_number_input():
    st.header('st.number_input')
    # number_input은 숫자를 직접 입력하거나 증감 버튼으로 바꿉니다.
    quantity = st.number_input('수량', min_value=0, max_value=20, value=1, step=1)
    st.write('선택한 수량:', quantity)

def show_slider():
    st.header('st.slider')
    # slider를 움직여 숫자를 바꿔 봅니다.
    score = st.slider('점수', min_value=0, max_value=100, value=50)
    st.write('선택한 점수:', score)
