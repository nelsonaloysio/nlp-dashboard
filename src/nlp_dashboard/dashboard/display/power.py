from typing import Union

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ..base.sidebar import SIDEBAR

MAX_ROWS = 100

OPTIONS = [
    "bigrams",
    "ents_gpe",
    "ents_loc",
    "ents_org",
    "ents_person",
    "hashtags",
    "mentions",
    "noun_chunks",
    "pos_adj",
    "pos_noun",
    "pos_verb",
    "trigrams",
    "tokens"
]

@classmethod
def display_power(self) -> None:
    themes = list(st.session_state.artifacts["themes"])

    st.write("Sunburst plot displaying hierarchical discourse structure from the identified themes.")

    options = [_ for _ in OPTIONS if _ in st.session_state.artifacts]
    table = st.session_state.series
    table.name = "Text"

    columns = st.columns([4, .2, .8])

    with columns[-1]:
        if themes:
            t = st.radio(
                "Select theme:",
                [None] + themes,
                # key="network_theme",
                index=0,
                format_func=lambda x: "All themes" if x is None else f"Theme {x}",
            )
        k = st.selectbox(
            "Object type:",
            options=options,
            index=options.index("tokens"),
            format_func=SIDEBAR.get
        )
        n = st.slider(
            "Tokens per theme:",
            max_value=100,
            min_value=1,
            value=10,
        )
        s = st.checkbox(
            "Normalize and fill space.",
            value=True
        )

        with columns[0]:
            fig = sunburst(themes, k=k, t=t, n=n, s=s)

            if fig is None:
                st.info(f"No objects of this type identified.")
            else:
                st.plotly_chart(fig, use_container_width=True)

    with st.expander("Show objects"):
        if t is not None:
            table = table.iloc[st.session_state.artifacts["themes"][t]["index"]]
        st.table(table[:MAX_ROWS])

    st.caption(f"Maximum of `{MAX_ROWS}` rows displayed in table. "
               "Number of objects displayed per theme is limited to first level occurrences..")

    self.display_kwic(theme=t)


@staticmethod
def sunburst(themes: list, k: str = "tokens", t: int = None, n: int = None, s: bool = False):
    themes = [t] if type(t) == int else (t or themes)
    ids = [""] + [f"Theme {t}" for t in themes]
    labels = [""] + [f"Theme {t}" for t in themes]
    parents = [""] + ["" for t in themes]
    values = [0] + [0 if s else st.session_state.artifacts["themes"][t][k][:n].sum() for t in themes]

    for t in themes:
        for i, v in st.session_state.artifacts["themes"][t][k][:n].items():
            ids.append(f"{t}-{i} - Theme {t}")
            labels.append(i.replace(" ", "<br>"))
            parents.append(f"Theme {t}")
            values.append(st.session_state.artifacts["themes"][t][k][:n].sum()/v)

    if len(ids) == len(themes) + 1:
        return None

    fig = go.Figure(
        go.Sunburst(
            ids=ids,
            labels=labels,
            parents=parents,
            values=values,
            domain=dict(column=0),
            insidetextorientation="radial",
        ),
    )

    fig.update_layout(
        height=750,
    )

    return fig