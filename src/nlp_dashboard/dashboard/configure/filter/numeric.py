import streamlit as st
from streamlit.errors import StreamlitAPIException

from ..utils import drop_empty, get_min_max, to_number
from ....pipeline.base.filters import filter_numeric

MAX_SLIDER = 100000


@classmethod
def configure_filter_numeric(self) -> None:
    self.title("Numeric interval", h=5)

    c1, c2 = st.columns([1, 2])
    options = [False] + st.session_state.data.columns.tolist()

    column = c1.selectbox(
        "Please select the field to filter interval from.",
        disabled=len(options) < 3,
        index=0,
        options=options,
        format_func=lambda x: "Choose an option" if x == False else x,
    )

    disabled = column == options[0]
    min_value, max_value = (-1, 1)

    if not disabled:

        if not drop_empty(st.session_state.data[column]).shape[0]:
            self.error(f"Error: column contains empty values only.")
            disabled = True

        elif st.session_state.data[column].shape[0] != drop_empty(st.session_state.data[column]).shape[0]:
            self.error(f"Error: column contains empty values.")
            disabled = True

        elif min_max := get_min_max(st.session_state.data[column]):
            if min_max[0] == min_max[1]:
                self.error(f"Error: column contains only one unique value.")
                disabled = True

            elif not all(isinstance(_, (int, float)) for _ in min_max):
                self.error(f"Error: column values do not have an expected type (`int`, `float`).")
                # self.error("Error: unable to obtain minimum and maximum values from column.")
                disabled = True

            min_value, max_value = min_max

        else:
            disabled = True

    with c2:
        # Avoids StreamlitAPIException caused by exceeding MAX_SLIDER.
        if not disabled and (max_value - min_value > MAX_SLIDER):
            c2a, c2b = st.columns(2)
            min_value = to_number(c2a.text_input("Please enter the minimum value.", min_value))
            max_value = to_number(c2b.text_input("Please enter the maximum value.", max_value))

        else:
            try:
                values = st.slider(
                    "Please enter the range to filter.",
                    disabled=disabled,
                    min_value=None if disabled else min_value,
                    max_value=None if disabled else max_value,
                    value=None if disabled else (min_value, max_value),
                )
                if not disabled:
                    min_value, max_value = values
            except StreamlitAPIException as e:
                self.error(f"Maximum supported value exceeded: {e}.")

    st.session_state.config["filter_numeric"] = {
        "column": None if disabled else column,
        "minimum": None if disabled else min_value,
        "maximum": None if disabled else max_value,
    }

    if not disabled:
        index = filter_numeric(st.session_state.data[column], min_value, max_value)

        if not len(index):
            self.warning(f"No rows matched within the selected interval.")

        else:
            self.info(f"Matching `{len(index)}` out of `{st.session_state.data.shape[0]}` "
                      f"rows ({float(len(index)/st.session_state.data.shape[0]*100):.2f}%).")
            st.session_state.filter_numeric = index
