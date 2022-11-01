import streamlit as st


@classmethod
def configure_filter_stopwords(self) -> None:
    self.title("Stopwords", h=5)
    c1, c2 = st.columns([1, 2])
    options = [True, False, "catalan", "chinese", "english", "french", "german", "italian", "japanese", "portuguese", "russian", "spanish"]

    stopwords = c1.selectbox(
        "Please choose the language to consider for stopwords below.",
        options,
        index=0,
        format_func=lambda x: "All languages" if x == True else "Disable stopwords" if x == False else x.capitalize(),
    )

    c1.caption("By default, all available languages are considered.")

    custom_stopwords = c2.text_input(
        "Please enter any additional terms to block below (comma-separated).",
        value="",
    )

    c2.caption(
        'Example: `USA, United States of America`.'
    )

    st.session_state.config["stopwords"] = {
        "language": stopwords,
        "custom": [x.strip() for x in custom_stopwords.split()] or None,
    }
