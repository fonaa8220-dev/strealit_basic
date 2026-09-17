import streamlit as st


PRODUCTS = {'상품': ['연필', '노트', '지우개'], '가격': [500, 2000, 700]}


def show_dataframe():
    st.header('st.dataframe')
    # 열을 정렬하거나 검색할 수 있는 표입니다.
    st.dataframe(PRODUCTS, hide_index=True)


def show_data_editor():
    st.header('st.data_editor')
    # 셀을 수정하거나 새 행을 추가해 보세요.
    edited = st.data_editor(PRODUCTS, num_rows='dynamic', hide_index=True)
    st.write('수정한 데이터:', edited)


def show_table():
    st.header('st.table')
    # 작은 데이터를 고정된 표로 보여줍니다.
    st.table(PRODUCTS)


def show_metric():
    st.header('st.metric')
    # 값과 이전 값과의 차이를 강조해 표시합니다.
    st.metric('오늘 방문자', '1,240명', '+120명')


def show_json():
    st.header('st.json')
    # 중첩된 데이터를 접고 펼치며 볼 수 있습니다.
    st.json({'사용자': {'이름': '홍길동', '관심사': ['독서', '운동']}})


def show():
    examples = [
        ('st.dataframe', show_dataframe),
        ('st.data_editor', show_data_editor),
        ('st.table', show_table),
        ('st.metric', show_metric),
        ('st.json', show_json),
    ]

    tabs = st.tabs([name for name, _ in examples], key='data_tabs', on_change='rerun')
    for tab, (_, show_example) in zip(tabs, examples):
        if tab.open:
            with tab:
                show_example()
