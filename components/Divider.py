import streamlit as st


def divider(title=None):
    st.markdown(
        f"""
    <div style="display: flex; align-items: center; text-align: center; margin: 1.5em 0;">
        <hr style="flex: 1; border: none; border-top: 1px solid #bbb; margin: 0 10px 0 0px;">
        <span style="padding: 0 1em; color: #888;">{title}</span>
        <hr style="flex: 1; border: none; border-top: 1px solid #bbb; margin: 0 0 0 10px;">
    </div>
    """,
        unsafe_allow_html=True,
    )
