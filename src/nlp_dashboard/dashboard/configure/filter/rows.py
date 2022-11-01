import streamlit as st


@classmethod
def configure_filter_rows(self) -> None:
    self.title("Number of rows", h=5)

    c = st.empty()
    c1, c2 = st.columns([1, 5])

    unique = c1.checkbox(
        "Consider only unique rows.",
        value=st.session_state.get("unique", False),
    )

    max_value = (
        st.session_state.data.drop_duplicates().shape[0]
        if unique else
        st.session_state.data.shape[0]
    )

    disabled = max_value < 2

    value = c.slider(
        "Please select the number of rows below to consider for analysis.",
        disabled=disabled,
        max_value=max_value,
        min_value=0 if disabled else 1,
        value=1 if disabled else max_value,
    )

    random = c2.checkbox(
        "Randomize rows for analysis.",
        disabled=value == max_value,
    )

    if disabled:
        value == st.session_state.data.shape[0]

    st.session_state.config["rows"] = {
        "value": value,
        "unique": unique,
        "random": None if value == max_value else random,
    }
