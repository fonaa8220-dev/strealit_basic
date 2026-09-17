import streamlit as st


def show_messages():
    st.header('상태 메시지')
    # 상황에 맞는 색과 아이콘으로 메시지를 구분합니다.
    st.success('작업이 완료되었습니다.')
    st.info('참고할 정보가 있습니다.')
    st.warning('확인이 필요합니다.')
    st.error('오류가 발생했습니다.')


def show_progress():
    st.header('st.progress')
    # 슬라이더를 움직여 진행 막대를 바꿔 보세요.
    value = st.slider('진행률', 0, 100, 40)
    st.progress(value, text=f'{value}% 완료')


def show_status():
    st.header('st.status')
    # 컨테이너에 작업 단계를 넣고 펼쳐 볼 수 있습니다.
    with st.status('작업 단계', expanded=True):
        st.write('1단계: 데이터 읽기')
        st.write('2단계: 결과 만들기')


def show():
    examples = [
        ('메시지', show_messages),
        ('st.progress', show_progress),
        ('st.status', show_status),
    ]

    tabs = st.tabs([name for name, _ in examples], key='status_tabs', on_change='rerun')
    for tab, (_, show_example) in zip(tabs, examples):
        if tab.open:
            with tab:
                show_example()
