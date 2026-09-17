import streamlit as st

from examples import buttons, colors, date_time, numbers, selections, text_inputs


def show():
    examples = [
        ('st.text_input', text_inputs.show_text_input),
        ('st.text_area', text_inputs.show_text_area),
        ('st.selectbox', selections.show_selectbox),
        ('st.radio', selections.show_radio),
        ('st.multiselect', selections.show_multiselect),
        ('st.checkbox', selections.show_checkbox),
        ('st.toggle', selections.show_toggle),
        ('st.number_input', numbers.show_number_input),
        ('st.slider', numbers.show_slider),
        ('st.button', buttons.show),
        ('st.date_input', date_time.show_date_input),
        ('st.time_input', date_time.show_time_input),
        ('st.color_picker', colors.show),
    ]

    tabs = st.tabs([name for name, _ in examples], key='input_tabs', on_change='rerun')
    for tab, (_, show_example) in zip(tabs, examples):
        if tab.open:
            with tab:
                show_example()
