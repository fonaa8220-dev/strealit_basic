import streamlit as st


def show_markdown():
    st.header('st.markdown')
    # Markdown 문법으로 글자를 꾸밉니다.
    st.markdown('**굵은 글씨**, *기울임꼴*, `코드`')
    st.markdown(':blue[파란 글씨]와 :green-background[배경색]도 표시할 수 있습니다.')


def show_code():
    st.header('st.code')
    # 언어를 지정하면 코드에 문법 강조가 적용됩니다.
    st.code("name = '홍길동'\nprint(name)", language='python', line_numbers=True)


def show_latex():
    st.header('st.latex')
    # 수식을 LaTeX 문법으로 표시합니다.
    st.latex(r'E = mc^2')


def show_badge():
    st.header('st.badge')
    # 색상이 다른 작은 상태 표시를 만듭니다.
    st.badge('새 기능', color='green')
    st.badge('확인 필요', color='orange')


def show_divider():
    st.header('st.divider')
    st.write('구분선 위의 내용')
    st.divider()
    st.write('구분선 아래의 내용')


def show():
    examples = [
        ('st.markdown', show_markdown),
        ('st.code', show_code),
        ('st.latex', show_latex),
        ('st.badge', show_badge),
        ('st.divider', show_divider),
    ]

    tabs = st.tabs([name for name, _ in examples], key='text_tabs', on_change='rerun')
    for tab, (_, show_example) in zip(tabs, examples):
        if tab.open:
            with tab:
                show_example()
