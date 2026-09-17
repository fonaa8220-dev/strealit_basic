import streamlit as st


@st.dialog('모달 창 예제')
def show_dialog():
    st.write('모달은 현재 화면 위에 열립니다.')
    name = st.text_input('모달 안에서 이름 입력')
    st.write('입력한 이름:', name)


def show_columns():
    st.subheader('st.columns: 나란히 배치')
    # 숫자 목록으로 열의 상대적인 너비를 정할 수 있습니다.
    left, right = st.columns([2, 1], border=True)
    left.write('넓은 왼쪽 열')
    right.write('좁은 오른쪽 열')


def show_container():
    st.subheader('st.container: 요소 묶기')
    # 컨테이너 안에 여러 요소를 함께 넣습니다.
    with st.container(border=True):
        st.write('이 글과 체크박스는 같은 컨테이너 안에 있습니다.')
        checked = st.checkbox('컨테이너 안의 체크박스')
        st.write('체크 여부:', checked)


def show_modal():
    st.subheader('st.dialog: 모달 창')
    # 버튼을 누르면 위에 정의한 모달 함수가 실행됩니다.
    if st.button('모달 열기'):
        show_dialog()


def show_empty():
    st.subheader('st.empty: 내용 바꾸기')
    # 같은 자리의 내용을 새 요소로 교체합니다.
    placeholder = st.empty()
    placeholder.info('처음 표시한 내용')
    if st.button('내용 바꾸기'):
        placeholder.success('새 내용으로 바뀌었습니다!')


def show_expander():
    st.subheader('st.expander: 접고 펼치기')
    with st.expander('설명 펼치기'):
        st.write('클릭하면 이 내용이 보이고, 다시 클릭하면 접힙니다.')


def show_form():
    st.subheader('st.form: 한 번에 제출하기')
    # 폼 안의 값은 제출 버튼을 누를 때 함께 전달됩니다.
    with st.form('layout_form'):
        name = st.text_input('폼 안의 이름')
        color = st.selectbox('좋아하는 색', ['빨강', '파랑', '초록'])
        submitted = st.form_submit_button('제출')
    if submitted:
        st.write('제출한 값:', name, color)


def show_popover():
    st.subheader('st.popover: 작은 창 열기')
    with st.popover('설정 열기'):
        selected = st.checkbox('팝오버 안의 옵션')
    st.write('옵션 선택:', selected)


def show_sidebar():
    st.subheader('st.sidebar: 왼쪽 영역')
    st.write('사이드바 예제는 화면 왼쪽에 표시됩니다.')
    # 사이드바에 넣은 위젯의 값은 본문에서도 사용할 수 있습니다.
    choice = st.sidebar.selectbox('사이드바 선택', ['첫 번째', '두 번째'])
    st.write('사이드바에서 선택한 값:', choice)


def show_bottom():
    st.subheader('st.bottom: 화면 아래쪽 고정')
    st.write('화면 아래쪽에 고정된 안내 문구를 확인해 보세요.')
    st.bottom.caption('st.bottom으로 표시한 하단 안내 문구')


def show_space():
    st.subheader('st.space: 여백 넣기')
    st.write('위쪽 문장')
    st.space('large')
    st.write('큰 여백 아래의 문장')


def show_tabs():
    st.subheader('st.tabs: 탭으로 나누기')
    # 현재 앱의 큰 탭도 같은 기능으로 만들었습니다.
    first, second = st.tabs(['첫 번째 탭', '두 번째 탭'])
    with first:
        st.write('첫 번째 탭의 내용')
    with second:
        st.write('두 번째 탭의 내용')


def show():
    examples = [
        ('st.columns', show_columns),
        ('st.container', show_container),
        ('st.dialog', show_modal),
        ('st.empty', show_empty),
        ('st.expander', show_expander),
        ('st.form', show_form),
        ('st.popover', show_popover),
        ('st.sidebar', show_sidebar),
        ('st.bottom', show_bottom),
        ('st.space', show_space),
        ('st.tabs', show_tabs),
    ]

    tabs = st.tabs([name for name, _ in examples], key='layout_tabs', on_change='rerun')
    for tab, (_, show_example) in zip(tabs, examples):
        if tab.open:
            with tab:
                show_example()
