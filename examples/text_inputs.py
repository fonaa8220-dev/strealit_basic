import streamlit as st


def show_text_input():
    st.header('st.text_input')

    # 기본 입력창의 값을 바로 화면에 보여줍니다.
    st.subheader('기본 입력')
    name = st.text_input('이름')
    st.write('입력한 이름:', name)

    # value는 입력창에 처음부터 표시할 값을 정합니다.
    st.subheader('기본값 넣기')
    movie = st.text_input('좋아하는 영화', value='기생충')
    st.write('좋아하는 영화:', movie)

    # placeholder는 안내 문구이고, max_chars는 입력 글자 수를 제한합니다.
    st.subheader('안내 문구와 글자 수 제한')
    nickname = st.text_input('별명', placeholder='10자 이내로 입력하세요', max_chars=10)
    st.write('입력한 별명:', nickname)

    # type='email'은 이메일 형식에 맞는 입력창을 만듭니다.
    st.subheader('이메일 입력')
    email = st.text_input('이메일', type='email')
    st.write('입력한 이메일:', email)

    # type='password'는 입력한 글자를 가려서 보여줍니다.
    st.subheader('비밀번호 입력')
    password = st.text_input('비밀번호', type='password')
    # 비밀번호 내용 대신 입력한 글자 수만 표시합니다.
    st.write('입력한 비밀번호 길이:', len(password))

def show_text_area():
    st.header('st.text_area')

    # text_area는 여러 줄의 글을 입력할 때 사용합니다.
    message = st.text_area('메시지', placeholder='메시지를 입력하세요', height=120)
    st.write('입력한 메시지:', message)
