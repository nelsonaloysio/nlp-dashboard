import streamlit as st

from ..utils import drop_empty, to_datetime


@classmethod
def configure_column_date(self) -> None:
    self.title("Time field", h=5)

    options = [False] + st.session_state.data.columns.tolist()
    default = [option for option in options if type(option) == str and any(_ in option.lower() for _ in ["date", "datetime", "time", "timestamp"])]
    disabled = 2 >= len(options)

    column = st.selectbox(
        "Please select the field containing dates to consider for analysis. Allows timestamps as seconds.",
        disabled=disabled,
        index=options.index(default[0]) if default else 0,
        options=options,
        format_func=lambda x: "Choose an option" if x == False else x,
    )

    if column == options[0]:
        getattr(self, "info" if disabled else "warning")("No %s, time series analysis will be skipped." % ("other columns available" if disabled else "column selected"))
        st.session_state.pop("dates", None)
        disabled = True

    elif not drop_empty(st.session_state.data[column]).shape[0]:
        self.error(f"Error: column contains empty values only.")
        st.session_state.pop("dates", None)
        disabled = True

    elif not len(dates := to_datetime(st.session_state.data[column])):
        self.error(f"Error: column contains invalid or empty values.")
        st.session_state.pop("dates", None)
        disabled = True

    else:
        errors = len(dates) - len(dates.dropna())
        getattr(self, "warning" if errors else "info")(
            f"Selected column range goes from **`{dates.min()}`** to **`{dates.max()}`**" +
            (f" (ignoring `{errors}` invalid or empty values)." if errors else ".")
        )
        st.session_state.dates = dates

    st.session_state.config["dates"] = None if disabled else column
    st.caption("The first column named `date`, `datetime`, `time` or `timestamp` is selected by default if found.")
