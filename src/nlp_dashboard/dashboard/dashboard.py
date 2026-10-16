# import pydeck as pdk
# import plotly.express as px
# import plotly.io as pio
import streamlit as st

from .base.app import BaseApp
from .base.process import process
from .base.reader import reader
from .base.sidebar import SIDEBAR, sidebar
from .base.uploader import uploader
from .configure.cluster import configure_cluster
from .configure.column.date import configure_column_date
from .configure.column.text import configure_column_text
from .configure.filter.numeric import configure_filter_numeric
from .configure.filter.rows import configure_filter_rows
from .configure.filter.stopwords import configure_filter_stopwords
from .configure.filter.dates import configure_filter_dates
from .configure.filter.words import configure_filter_words
from .configure.model.hf import configure_model_hf
from .configure.model.spacy import configure_model_spacy
from .configure.network import configure_network
from .configure.preview import configure_preview
from .display.artifact import display_artifact
from .display.configure import display_configure
from .display.debug import display_debug
from .display.download import display_download
from .display.kwic import display_kwic
from .display.network import display_network
from .display.overview import display_overview
from .display.power import display_power
from .display.start import display_start
from .display.themes import display_themes

# pio.templates.default = "none"

PAGE_CONFIG = {
    "layout": "wide",
    "page_title": "Natural Language Processing Dashboard App",
    "page_icon": "✨",
    "menu_items": {
        "Report a bug": "https://github.com/nelsonaloysio/nlp-dashboard/issues",
    }
}

TITLE = """
    <h1 align="center">✨ Natural Language Processing Dashboard App ✨</h1>
    """

FOOTNOTE = """
    ___
    > © 2026 Nelson Aloysio Reis de Almeida Passos.
    > Proof of concept for demonstration purposes only;
    > source code available on [GitHub](https://github.com/nelsonaloysio/nlp-dashboard).
    > Recommended resolution: `1920x1080`.
    """


class Dashboard(BaseApp):
    configure_cluster = configure_cluster
    configure_column_date = configure_column_date
    configure_column_text = configure_column_text
    configure_filter_numeric = configure_filter_numeric
    configure_filter_rows = configure_filter_rows
    configure_filter_stopwords = configure_filter_stopwords
    configure_filter_dates = configure_filter_dates
    configure_filter_words = configure_filter_words
    configure_model_hf = configure_model_hf
    configure_model_spacy = configure_model_spacy
    configure_network = configure_network
    configure_preview = configure_preview
    display_artifact = display_artifact
    display_configure = display_configure
    display_debug = display_debug
    display_download = display_download
    display_kwic = display_kwic
    display_network = display_network
    display_overview = display_overview
    display_power = display_power
    display_start = display_start
    display_themes = display_themes
    reader = reader
    process = process
    sidebar = sidebar
    uploader = uploader

    def __init__(self) -> None:
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
                self.display()
            else:
                self.configure()


    @classmethod
    def configure(self) -> None:
        st.subheader("Configuration")
        st.session_state.config = st.session_state.get("config", {})

        self.title("File uploader", h=5)
        self.uploader()

        if "data" in st.session_state:
            self.display_configure()
            st.divider()
            self.display_start()


    def display(self) -> None:
        if not st.session_state.get("page"):
            self.info("Please select a page from the sidebar.")
            return

        self.title(SIDEBAR[st.session_state.page], h=1, spacing=False)

        # Reset previously applied settings on page change.
        if st.session_state.page != st.session_state.get("last_shown"):
            st.session_state.last_shown = st.session_state.page
            st.session_state.pagination = {}
            st.session_state.scale_y = 0

        # Content containers.
        # a1, a2, a3 = st.container(), st.container(), st.container()
        a1, a3 = st.container(), st.container()

        # Keywords in context.
        # with a2:
        #     if st.session_state.page != "debug":
        #         self.display_kwic()

        # Artifact content.
        with a1:
            artifact = st.session_state.artifacts.get(st.session_state.page, None)
            display_func = getattr(self, f"display_{st.session_state.page}", None)

            # Display overview, network, or themes.
            if display_func is not None:
                display_func()

            # Missing artifact.
            elif artifact is None:
                self.warning(f"Artifact missing or not yet implemented.")
                return

            # No results returned.
            elif not len(st.session_state.artifacts[st.session_state.page]):
                st.info(f"No objects of this type identified.")
                return

            # Display results from artifact.
            elif artifact is not None:
                self.display_artifact()

        # Artifact download.
        with a3:
            if st.session_state.page != "debug":
                self.display_download()

        st.caption(f"Total artifacts generated: `{len(st.session_state.artifacts)}` in `{st.session_state.time_elapsed}` seconds.")
