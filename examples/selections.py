import streamlit as st


def show_selectbox():
    st.header('st.selectbox')
    # selectbox는 목록에서 한 가지를 고릅니다.
    fruit = st.selectbox('좋아하는 과일', ['사과', '바나나', '딸기'])
    st.write('선택한 과일:', fruit)

    # index=None으로 시작하면 처음에는 아무 항목도 선택되지 않습니다.
    drink = st.selectbox('마실 음료', ['물', '커피', '주스'], index=None, placeholder='음료를 고르세요')
    st.write('선택한 음료:', drink)

def show_radio():
    st.header('st.radio')
    # radio는 선택지를 펼쳐 놓고 한 가지를 고릅니다.
    season = st.radio('좋아하는 계절', ['봄', '여름', '가을', '겨울'], horizontal=True)
    st.write('선택한 계절:', season)

    # 세로 라디오 버튼에는 각 선택지의 설명을 붙일 수도 있습니다.
    delivery = st.radio('받는 방법', ['택배', '직접 수령'], captions=['집으로 배송', '매장에서 수령'], index=None)
    st.write('선택한 방법:', delivery)

def show_multiselect():
    st.header('st.multiselect')
    # multiselect는 여러 항목을 동시에 고릅니다.
    hobbies = st.multiselect('취미', ['독서', '운동', '게임', '여행'])
    st.write('선택한 취미:', hobbies)

def show_checkbox():
    st.header('st.checkbox')
    # checkbox는 체크 여부를 True 또는 False로 돌려줍니다.
    agree = st.checkbox('알림 받기')
    st.write('알림 받기:', agree)

def show_toggle():
    st.header('st.toggle')
    # toggle도 켜짐과 꺼짐을 선택하지만 스위치 모양으로 표시됩니다.
    enabled = st.toggle('기능 켜기')
    st.write('기능 켜짐:', enabled)
