from urllib.error import URLError

import pandas as pd
import streamlit as st
from streamlit.components.v1 import html

from ...pipeline.base.network import network_html

MAX_ROWS = 100
ARROW_LENGTH = 6


@classmethod
def display_network(self) -> None:
    themes = list(st.session_state.artifacts.get("themes", []))
    columns = st.columns([4, .2, .8])

    table = st.session_state.series
    table.name = "Text"

    G = st.session_state.artifacts["network"]
    nodes = pd.DataFrame(G.nodes(data="community"), index=G.nodes()).iloc[:, -1]
    edges = pd.DataFrame(G.edges(data="index"), columns=["source", "target", "index"])
    modules = nodes.value_counts()

    with columns[2]:
        t = None

        if themes:
            t = st.radio(
                "Select theme:",
                [None] + themes,
                # key="network_theme",
                index=0,
                format_func=lambda x: "All themes" if x is None else f"Theme {x}",
            )

        if t is not None:
            G = G.subgraph(
                edges
                .loc[edges["index"].isin(st.session_state.series.iloc[st.session_state.artifacts["themes"][t]["index"]].index)]
                [["source", "target"]]
                .apply(list, axis=1)
                .explode()
            )
            # G = nx.edge_subgraph(
            #     G, [(edge[0], edge[1], edge[2]) for edge in edges.loc[edges["index"].isin(
            #         st.session_state.series.iloc[st.session_state.artifacts["themes"][t]["index"]].index)].values]
            # )

        c = st.selectbox(
            "Select community:",
            [None] + sorted((nodes if not t else nodes.loc[list(G.nodes())]).unique())[:100],
            # key="network_community",
            index=0,
            disabled=st.session_state.artifacts.get("network") is None,
            format_func=lambda x: "All communities" if x is None else f"Community {x+1} ({modules[x]})",
        )
        s = st.slider(
            "Node size:",
            max_value=100.0,
            min_value=1.0,
            value=2.5,
        )
        b = st.checkbox(
            "Show node labels."
        )
        a = st.checkbox(
            "Show edge arrows.",
            value=False,
            disabled=st.session_state.config["network"]["directed"] is False
        )

        if c is not None:
            G = G.subgraph(
                nodes[nodes == c].index.tolist()
            )

    # Visualize and download graph.
    with columns[0]:
        st.write(message_network(G, t, c)) if G.order() else st.info(f"No relations identified within this theme.")

        try:
            html(
                network_html(G, membership=nodes, node_size=s, node_label=b, edge_arrow=ARROW_LENGTH if a else 0),
                width=1000,
                height=815,
                scrolling=False
            )

        except URLError as e:
            st.warning(
                """
                **This content requires internet access.**
                Connection error: %s
                """
                % e.reason
            )


    with st.expander("Show objects"):
        index = [_[-1] for _ in G.edges(data="index")]
        st.table(table.loc[index][:MAX_ROWS])

    st.caption(f"Maximum of `{MAX_ROWS}` rows displayed in table. "
               f"Node colors represent the `{modules.shape[0]}` communities"
               "found by modularity optimization [[1](https://leidenalg.readthedocs.io)], "
               "suitable for descriptive or exploratory tasks only.")

    self.display_kwic(theme=t)


def message_network(G, t=None, c=None) -> str:
    g = "community" if c is not None else "theme" if t is not None else "graph"

    s = f"Displaying {g} with "\
        f"`{G.order()}` nodes and "\
        f"`{G.size()}` edges ("\
        f"`{st.session_state.config['network']['source']}` → "\
        f"`{st.session_state.config['network']['target']}`), "\
        f"with an average degree of `{sum([_[1] for _ in G.degree()])/G.order():.3f}`. "

    if st.session_state.config["network"]["directed"]:
        in_deg = [f'`{_[0]}` (`{_[1]}`)' for _ in sorted(G.in_degree(), key=lambda x: x[1], reverse=True)[:3]]
        out_deg = [f'`{_[0]}` (`{_[1]}`)' for _ in sorted(G.out_degree(), key=lambda x: x[1], reverse=True)[:3]]
        s += f"Nodes with highest in-degree: {', '.join(in_deg)}, out-degree: {', '.join(out_deg)}."
    else:
        deg = [f'`{_[0]}` (`{_[1]}`)' for _ in sorted(G.degree(), key=lambda x: x[1], reverse=True)[:3]]
        s += f"Nodes with highest degree: {', '.join(deg)}."

    return s