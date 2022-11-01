import streamlit as st

from .utils import drop_empty


@classmethod
def configure_network(self) -> None:
    self.title("Network fields", h=5)

    options = [False] + st.session_state.data.columns.tolist()
    disabled = 2 >= len(options)

    edges = None
    auto = "source" in options and "target" in options

    columns = st.columns([0.6, 0.6, 0.2])

    with columns[0]:
        source = st.selectbox(
            "Please select the source field for the edges.",
            disabled=disabled,
            index=options.index("source") if auto else options.index(st.session_state.config.get("network", {}).get("source", False)),
            options=options,
            format_func=lambda x: "Choose an option" if x == False else x,
        )

    with columns[1]:
        target = st.selectbox(
            "Please select the target field for the edges.",
            disabled=disabled,
            index=options.index("target") if auto else options.index(st.session_state.config.get("network", {}).get("target", False)),
            options=options,
            format_func=lambda x: "Choose an option" if x == False else x,
        )

    disabled = any(_ == False for _ in (source, target))

    with columns[2]:
        st.write(""); st.write("")
        directed = st.checkbox("Directed edges.", disabled=disabled, value=True)

    if any(c == False for c in (source, target)):
        self.info("No %s, network analysis will be skipped." % ("other columns available" if 2 >= len(options) else "column selected"))
        disabled = True

    elif not all(len(drop_empty(st.session_state.data[c])) for c in (source, target)):
        self.error(f"Error: column contains empty values only.")
        disabled = True

    else:
        edges = st.session_state.data[[source, target]].map(lambda x: None if x == "" else x).dropna()
        order = edges.apply(list, axis=1).explode().drop_duplicates().shape[0]
        size = edges.drop_duplicates().shape[0]
        self.info(f"Graph will be created with `{order}` nodes and `{size}` connections.")
        if order > 1000:
            self.warning(f"Medium-scale graph detected, please consider filtering the data or downloading the resulting artifact for futher analysis.")

    st.session_state.config["network"] = {
        "source": source if not disabled else False,
        "target": target if not disabled else False,
        "directed": directed
    }
    st.caption("Columns named `source` and `target` are selected by default if both are found.")
