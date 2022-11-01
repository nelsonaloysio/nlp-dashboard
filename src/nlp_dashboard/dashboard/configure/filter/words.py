import streamlit as st

from ....pipeline.base.filters import filter_text


@classmethod
def configure_filter_words(self) -> None:
    self.title("Words in text", h=5)

    c1, c2 = st.columns([1, 2])
    c3, c4 = st.columns([1, 4])

    columns = c1.multiselect(
        "Please select the field(s) to filter text from.",
        options=st.session_state.data.columns.tolist(),
    )

    value = c2.text_input(
        "Please enter the tags to match below (comma-separated, example: `tag, another tag`).",
        disabled=columns == [],
        value="",
    )

    case_sensitive = c3.checkbox(
        "Consider case accents (AaBbCc).",
        disabled=columns == [],
        value=False,
    )

    partial_matches = c4.checkbox(
        "Consider partial matches ('book' => 'books').",
        disabled=columns == [],
        value=False,
    )

    if columns and value:
        value = [x.strip() for x in value.split(",")]
        index = filter_text(st.session_state.data[columns], value, case_sensitive=case_sensitive, whole_words=not partial_matches)

        if len(index):
            self.info(f"Matching `{len(index)}` out of `{st.session_state.data.shape[0]}` rows ({float(len(index)/st.session_state.data.shape[0]*100):.2f}%).")
            st.session_state.filter_text = index

        else:
            self.warning(f"No rows matched with the selected tags.")

    st.session_state.config["filter_text"] = {
        "columns": columns or None,
        "value": value or None,
    }
