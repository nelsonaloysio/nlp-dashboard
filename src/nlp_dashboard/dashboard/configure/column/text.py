import streamlit as st


@classmethod
def configure_column_text(self) -> None:
    self.title("Text fields", h=5)

    options = st.session_state.data.columns.tolist()

    default = [option
               for option in options
               if type(option) == str and any(_ in option.lower() for _ in ["text", "title", "sentence"])]

    columns = st.multiselect(
        "Please select one or more fields below to consider for text analysis.",
        default=default,
        options=options,
    )

    if not columns:
        self.info("No column field selected. All uploaded data will be considered.")

    st.caption("Columns containing `text`, `title` or `sentence` in their names are selected by default if found.")
    st.session_state.config["columns"] = columns or None
