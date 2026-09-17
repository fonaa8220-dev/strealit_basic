import streamlit as st


def show_date_input():
    st.header('st.date_input')
    # date_input은 달력에서 날짜를 선택합니다.
    selected_date = st.date_input('날짜')
    st.write('선택한 날짜:', selected_date)

def show_time_input():
    st.header('st.time_input')
    # time_input은 시간을 선택합니다.
    selected_time = st.time_input('시간')
    st.write('선택한 시간:', selected_time)
