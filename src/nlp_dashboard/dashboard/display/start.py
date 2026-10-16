import streamlit as st

URL = "https://github.com/nelsonaloysio/nlp-dashboard"


@classmethod
def display_start(self) -> None:
    self.title("Start analysis", h=4, spacing=False)
    st.write("Process uploaded data and generate artifacts for analysis.")

    if st.session_state.config.get("model_hf") is None and st.session_state.config.get("model_spacy") is None:
        self.warning("Clustering and language models not loaded, some artifacts will not be generated.")

    elif st.session_state.config.get("model_hf") is None:
        self.warning("Clustering model not loaded, some artifacts will not be generated.")

    elif st.session_state.config.get("model_spacy") is None:
        self.warning("Language model not loaded, some artifacts will not be generated.")

    container = st.empty()

    if container.button("Process", type="primary"):
        container.empty()
        exception = None

        with container:
            try:
                with st.spinner("Processing..."):
                    self.process()

            except Exception as e:
                exception = e

        if "artifacts" not in st.session_state:
            self.error("Failed to generate artifacts, please refresh your browser before trying again.", icon="💔")

        if exception is not None:
            st.write(exception)

    else:
        st.caption("Press the button above to commence analysis considering `%s` text column(s)." %
                   (len(st.session_state.config.get("columns") or st.session_state.data.columns)))
