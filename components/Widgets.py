import streamlit as st


class Divider:
    def __init__(self, title=None, padding_top="0.5em", padding_bottom="0.5em"):
        self.title = title
        self.padding_top = padding_top
        self.padding_bottom = padding_bottom
        self.render()  # Automatically render on initialization

    def render(self):
        hr_style = (
            "flex: 1; border: none; border-top: 0.5px solid #ddd; margin: 0 10px 0 0px;"
        )
        hr_style_right = (
            "flex: 1; border: none; border-top: 0.5px solid #ddd; margin: 0 0 0 10px;"
        )
        hr_style_no_title = "border: none; border-top: 0.5px solid #ddd;"

        if self.title:
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; text-align: center; margin: {self.padding_top} 0 {self.padding_bottom} 0;">
                    <hr style="{hr_style}">
                    <span style="padding: 0 1em; color: #888;">{self.title}</span>
                    <hr style="{hr_style_right}">
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div style="margin: {self.padding_top} 0 {self.padding_bottom} 0;">
                    <hr style="{hr_style_no_title}">
                </div>
                """,
                unsafe_allow_html=True,
            )
