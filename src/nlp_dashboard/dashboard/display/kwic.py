from io import BytesIO
from zipfile import ZipFile

import pandas as pd
import streamlit as st

from ...pipeline.base.kwic import build_kwic, kwic, prepare_keywords

ADD_MORE_CONTEXT_IF_PDF_ROWS = 3
CONTEXT_SIZE = 10
MAX_KEYWORDS = 100
MAX_ROWS = 100
MORE_CONTEXT_SIZE = 100


@classmethod
def display_kwic(self, artifact=None, theme=None) -> None:
    self.title("Keywords in context", h=3)

    if artifact is None:
        artifact = st.session_state.artifacts["themes"][theme]["tokens"] if theme is not None else st.session_state.artifacts["tokens"]

    theme = "" if theme is None else theme
    options = artifact[:MAX_KEYWORDS].index.tolist()
    disabled = st.session_state.page != "overview" and len(artifact.index.tolist()) == 0

    # Spacing tested on 1920x1080 with sidebar.
    # kwic_container = st.columns([10.4, 0.9, 0.7])
    kwic_container = st.columns([11.2, 0.9])
    kwic_checkbox = st.columns([1.7, 2, 1.3, 1.1, 1.2, 1])

    # Display options as checkbox widgets.
    with kwic_checkbox[0]:
        partial_matches = st.checkbox(
            "Partial matching ('book' → 'books').",
            key=f"kwic_partial_matches{theme}",
            disabled=disabled,
            value=True,
        )
    with kwic_checkbox[1]:
        wrap_keywords = st.checkbox(
            "Wrap keywords ('a book' ≠ 'a great book').",
            key=f"kwic_wrap_keywords{theme}",
            disabled=disabled,
            value=False,
        )
    with kwic_checkbox[2]:
        case_sensitive = st.checkbox(
            "Case sensitive (AaBbCc).",
            key=f"kwic_case_sensitive{theme}",
            disabled=disabled,
            value=False,
        )
    with kwic_checkbox[3]:
        value_counts = st.checkbox(
            "Count occurrences.",
            key=f"kwic_value_counts{theme}",
            disabled=disabled,
            value=False,
        )
    with kwic_checkbox[4]:
        more_context = st.checkbox(
            "Display more context.",
            key=f"kwic_more_context{theme}",
            disabled=disabled,
            value=False,
        )
    with kwic_checkbox[5]:
        multiselect = st.checkbox(
            "Multi-selector.",
            key=f"kwic_multiselect{theme}",
            disabled=disabled,
            value=True,
        )

    # Keyword selector widget.
    with kwic_container[0]:
        # if not and not text_input multiselect:
        #     keywords = st.selectbox(
        #         "Please select a keyword below for context analysis.",
        #         options=[False] + options,
        #         index=0,
        #         key=f"kwic_keywords{theme}",
        #         format_func=lambda x: "Choose an option" if x == False else f"{options.index(x)+1}. {x} ({artifact[x]})"
        #     )

        if not multiselect:
            keywords = st.text_input(
                "Please enter one or more keywords below for context analysis (comma separated).",
                "",
                key=f"kwic_keywords{theme}",
            )

        else:
            keywords = st.multiselect(
                "Please select one or more keywords below for context analysis.",
                options=options,
                default=[],
                key=f"kwic_keywords{theme}",
                format_func=lambda x: f"{options.index(x)+1}. {x} ({artifact[x]})",
                max_selections=10,
            )

    df_kwic, keywords_ = None, []

    if keywords:
        # Construct keywords in context data frame.
        df_kwic = pd.concat([
            build_kwic(
                st.session_state.series,
                # Caches returned data for each keyword.
                self.cache_data(
                    kwic,
                    series=st.session_state.series,
                    keywords=(keyword if case_sensitive else keyword.lower()).strip(),
                    case_sensitive=case_sensitive,
                    whole_words=False if partial_matches else True,
                    wrap_keywords=wrap_keywords,
                ),
                add_more_context_if_pdf_rows=ADD_MORE_CONTEXT_IF_PDF_ROWS,
                context_size=MORE_CONTEXT_SIZE if more_context else CONTEXT_SIZE,
                # value_counts=value_counts,
            )
            for keyword in prepare_keywords(keywords)
        ])

        # Display preview of first MAX_ROWS rows.
        with st.expander(
            f"Preview matches ({len(df_kwic)})",
            expanded=True,
        ):
            st.table(
                pd.concat([df_kwic[:MAX_ROWS], st.session_state.dates.loc[df_kwic[:MAX_ROWS].index]], axis=1)
                if not value_counts and st.session_state.get("dates") is not None
                else (df_kwic.value_counts().rename("Occurrences").reset_index() if value_counts else df_kwic)[:MAX_ROWS]
            )

        # Store proper keywords in a list.
        # keywords_ = [
        keywords_ = [
            keyword.strip() for keyword in (
                keywords.split(",") if isinstance(keywords, str) else keywords
            )
        ]

    with kwic_container[1]:
        st.write("")
        st.write("")
        e = st.empty()

        if e.button(
            "Download" if st.session_state.get(f"kwic_download{theme}") else "Compress",
            key=f"kwic_button{theme}",
            disabled=(st.session_state.get(f"kwic_download{theme}") is not None or not keywords),
        ):
            e.empty()

            # Create in-memory buffer to write and store zipped contents.
            with st.spinner(f"Preparing `{len(st.session_state.artifacts)}` download..."):
                with BytesIO() as buffer:
                    with ZipFile(buffer, "w") as z:
                        z.writestr(
                            "Keywords in Context.csv",
                            df_kwic.to_csv().encode("utf-8")
                        )
                    buffer.seek(0)
                    # Replace button widget.
                    e.download_button(
                        data=buffer,
                        file_name="Keywords in Context.zip",
                        key=f"kwic_download{theme}",
                        label="Download",
                    )

    st.caption(
        f"Total occurrences might differ due to keyword matching rules."
        f" Preview limited to a maximum of `{MAX_ROWS}` top results and"
        f" `{CONTEXT_SIZE}` tokens to the left and right, unless whole context is displayed."
    )

    return df_kwic, keywords_
