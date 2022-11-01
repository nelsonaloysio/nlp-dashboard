from datetime import datetime

import streamlit as st

from ..utils import drop_empty, to_datetime
from ....pipeline.base.filters import filter_dates


@classmethod
def configure_filter_dates(self) -> None:
    self.title("Time interval", h=5, spacing=1)

    c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 1])
    options = [False] + st.session_state.data.columns.tolist()
    default = st.session_state.config.get("dates")

    column = c1.selectbox(
        "Please select the field to filter dates from.",
        disabled=len(options) < 3,
        index=(st.session_state.data.columns.tolist().index(default) + 1) if default else 0,
        key="dates_column",
        options=options,
        format_func=lambda x: "Choose an option" if x == False else x,
    )

    disabled = column == options[0]

    if not disabled:

        if not drop_empty(st.session_state.data[column]).shape[0]:
            self.error(f"Error: column contains empty values only.")
            disabled = True

        elif st.session_state.data[column].shape[0] != drop_empty(st.session_state.data[column]).shape[0]:
            self.error(f"Error: column contains empty values.")
            disabled = True

        elif not len(dates := to_datetime(st.session_state.data[column])):
            self.error(f"Error: column contains invalid date/time values.")
            disabled = True

    min_date = c2.date_input(
        "Select the minimum date/time.",
        disabled=disabled,
        value=None if disabled else dates.min().replace(second=00).date(),
    )

    min_time = c3.time_input(
        " ",
        disabled=disabled,
        value=datetime.strptime("00:00:00", "%H:%M:%S"),
    )

    max_date = c4.date_input(
        "Select the maximum date/time.",
        disabled=disabled,
        value=None if disabled else dates.max().replace(second=59).date(),
    )

    max_time = c5.time_input(
        "  ",
        disabled=disabled,
        value=datetime.strptime("23:59:59", "%H:%M:%S"),
    )

    st.session_state.config["filter_dates"] = {
        "column": None if disabled else column,
        "minimum": None if disabled else (min_date, min_time),
        "maximum": None if disabled else (max_date, max_time),
    }

    if not disabled and len(dates):
        index = filter_dates(dates, min_date, min_time, max_date, max_time)

        if not len(index):
            self.warning(f"No rows matched within the selected interval.")

        else:
            st.session_state.filter_dates = index
            self.info(f"Matching: **`{len(index)}`** out of **`{st.session_state.data.shape[0]}`** rows "
                      f"({float(len(index)/st.session_state.data.shape[0]*100):.2f}%). "
                      f"Range: from **`{dates.min()}`** to **`{dates.max()}`**.")
