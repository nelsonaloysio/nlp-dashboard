from typing import Callable

import streamlit as st

from .base import (
    Artifacts,
    Configure,
    Content,
    Default,
    Sidebar,
    Uploader,
)
from .lib import (
    Altair,
    Filters,
    Kwic,
    Wordcloud,
)

PAGE_CONFIG = {
    "layout": "wide",
    "page_title": "Culture Hack Labs NLP Dashboard App",
    "page_icon": "https://dashboard.culturehack.io/favicon.ico",
}

TITLE = """
    <h1 align="center">✨ The Culture Hack Labs NLP Dashboard App ✨</h1>
    """

FOOTNOTE = """
    ___
    > Note: This is a prototype intended for demo purposes of the Culture Hack Labs Natural Language
    > Processor Dashboard App and does not represent the final product. Recommended resolution: `1920x1080`.
    """


class App(Default, Sidebar, Uploader, Artifacts, Content, Configure, Altair, Kwic, Filters, Wordcloud):

    def __init__(self, pipeline: Callable) -> None:
        self.pipeline = pipeline
        st.set_page_config(**PAGE_CONFIG)

    def __call__(self) -> None:
        st.write(TITLE, unsafe_allow_html=True)
        st.write("___")

        content = st.container()
        footnote = st.container()

        with st.sidebar:
            self.sidebar()

        with footnote:
            st.caption(FOOTNOTE)

        with content:
            if "artifacts" in st.session_state:
                self.content()
            else:
                self.configure()
