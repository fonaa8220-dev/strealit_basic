import streamlit as st


SALES = {'판매량': [12, 18, 15, 24, 30]}


def show_line_chart():
    st.header('st.line_chart')
    # 값의 변화를 선으로 보여줍니다.
    st.line_chart(SALES)


def show_bar_chart():
    st.header('st.bar_chart')
    # 같은 데이터를 막대로 비교합니다.
    st.bar_chart(SALES)


def show_area_chart():
    st.header('st.area_chart')
    # 선 아래 영역을 채워 변화량을 보여줍니다.
    st.area_chart(SALES)


def show_scatter_chart():
    st.header('st.scatter_chart')
    # 두 값의 관계를 점으로 표시합니다.
    scores = {'공부 시간': [1, 2, 3, 4, 5], '점수': [52, 65, 70, 82, 91]}
    st.scatter_chart(scores, x='공부 시간', y='점수')


def show():
    examples = [
        ('st.line_chart', show_line_chart),
        ('st.bar_chart', show_bar_chart),
        ('st.area_chart', show_area_chart),
        ('st.scatter_chart', show_scatter_chart),
    ]

    tabs = st.tabs([name for name, _ in examples], key='chart_tabs', on_change='rerun')
    for tab, (_, show_example) in zip(tabs, examples):
        if tab.open:
            with tab:
                show_example()
