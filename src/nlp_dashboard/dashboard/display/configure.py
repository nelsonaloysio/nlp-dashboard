import streamlit as st


@classmethod
def display_configure(self) -> None:
    self.configure_preview()

    st.divider()
    self.title("Data parameters", h=3, spacing=False)
    self.configure_column_text()
    self.configure_column_date()
    self.configure_network()

    st.divider()
    self.title("Model parameters", h=3, spacing=False)
    self.configure_model_hf()
    self.configure_model_spacy()

    st.divider()
    self.title("Optional parameters", h=3, spacing=False)

    # NOTE: `st.checkbox(...)` resulted in buggy behavior with `key=...`.
    # Workaround: `st.session_state... = st.checkbox(...)` + `st.rerun()`.
    configure_optional = st.session_state.get("configure_optional", False)
    st.session_state.configure_optional = st.checkbox("Show filtering options and additional settings.", value=configure_optional)

    if configure_optional != st.session_state.configure_optional:
        st.rerun()

    if st.session_state.configure_optional:
        self.configure_cluster()
        self.configure_filter_rows()
        self.configure_filter_words()
        self.configure_filter_numeric()
        self.configure_filter_dates()
        self.configure_filter_stopwords()
    else:
        st.caption("Select the checkbox above to display advanced settings.")
