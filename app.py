import streamlit as st

from examples import chat_elements, chart_elements, data_elements, input_widgets, layouts, status_elements, text_elements


st.title('Streamlit 기능 둘러보기')
st.write('위쪽에서 요소 그룹을 고르고, 아래쪽에서 기능을 선택해 보세요.')

# 각 그룹의 하위 탭과 예제는 examples 폴더의 파일이 맡습니다.
groups = [
    ('입력 위젯', input_widgets.show),
    ('레이아웃', layouts.show),
    ('텍스트 표시', text_elements.show),
    ('데이터 표시', data_elements.show),
    ('차트', chart_elements.show),
    ('상태', status_elements.show),
    ('채팅', chat_elements.show),
]

tabs = st.tabs(
    [name for name, _ in groups],
    key='main_tabs',
    on_change='rerun',
)

for tab, (_, show_group) in zip(tabs, groups):
    if tab.open:
        with tab:
            show_group()
