import pandas as pd
import plotly.express as px
import streamlit as st

MAX_ROWS = 100
SENTENCE_LENGTH = 80
SENTENCE_LINES = 5


@classmethod
def display_themes(self) -> None:
    themes = list(st.session_state.artifacts["themes"])

    table = st.session_state.series
    table.name = "Text"

    columns = st.columns([4, .2, .8])

    with columns[-1]:
        t = st.radio(
            "Select theme:",
            [None] + themes,
            index=0,
            key="theme_e",
            format_func=lambda x: "All themes" if x is None else f"Theme {x}",
        )
        d = st.radio(
            "Embedding space:",
            [3, 2],
            index=0,
            key="dimensions",
            format_func=lambda x: f"{x}-dimensional",
        )
        s = st.slider(
            "Marker size:",
            max_value=10.0,
            min_value=0.1,
            value=2.5,
        )

        with columns[0]:
            if not t:
                st.write(f"Displaying `{st.session_state.series.shape[0]}` objects from all themes, determined by semantic similarity.")
                chart = scatter(d, t, marker_size=s)
            else:
                index = st.session_state.artifacts["themes"][t]["index"]
                st.write(f"Displaying `{len(index)}` objects from **Theme {t}**, determined by semantic similarity.")
                chart = scatter(d, t, color=None, marker_size=s)

            st.plotly_chart(chart, use_container_width=True)

    with st.expander("Show objects"):
        if t is not None:
            table = table.iloc[index]
        st.table(table[:MAX_ROWS])

    st.caption(f"Maximum of `{MAX_ROWS}` rows displayed in table. "
               "Similar objects are grouped together after clustering and dimensionality reduction. "
               "Hover over points to see the text associated with each object.")

    self.display_kwic(theme=t)


@staticmethod
def scatter(d: int, t: int, color="Theme", marker_size: float = 2.5):
    df = pd.DataFrame({
        "Theme": [str(_) for _ in st.session_state.artifacts["cluster"]],
        "index": st.session_state.series.index,
        "text": st.session_state.series.map(format_text).values.tolist(),
        "x": [h[0] for h in st.session_state.artifacts[f"embedding-{d}d"]],
        "y": [h[1] for h in st.session_state.artifacts[f"embedding-{d}d"]],
        **({"z": [h[2] for h in st.session_state.artifacts["embedding-3d"]]} if d == 3 else {})
    })\
    .sort_values("Theme")

    if t:
        df = df[df["Theme"] == str(t)]

    fig = getattr(px, "scatter_3d" if d == 3 else "scatter")(
        df,
        x="x",
        y="y",
        color=color,
        hover_name="index",
        hover_data=["index", "text"],
        height=600,
        **({"z": "z"} if d == 3 else {})
    )

    axis = dict(
        # showbackground=False,
        # showgrid=False,
        # showline=False,
        showticklabels=False,
        title=None,
        # visible=False,
    )

    hoverlabel = dict(
        font_size=14,
    )

    hovertemplate = "<br>".join([
        "<b>%{customdata[0]}</b><br>",
        "%{customdata[1]}"
        "<extra></extra>"
    ])

    fig.update_layout(
        hoverlabel=hoverlabel,
        scene=dict(xaxis=axis, yaxis=axis, zaxis=axis),
    )

    fig.update_traces(
        marker_size=marker_size,
        hovertemplate=hovertemplate,
    )

    return fig


@staticmethod
def format_text(text: str, length=SENTENCE_LENGTH, lines=SENTENCE_LINES):
    chunks, sentence = [], ""
    tokens = text.split()

    for i, token in enumerate(tokens):
        sentence += token
        if i+1 == len(tokens) or len(sentence) >= length:
            chunks.append(sentence)
            sentence = ""
        else:
            sentence += " "
        if len(chunks) == lines:
            chunks[-1] += "..."
            break

    return "<br>".join(chunks)