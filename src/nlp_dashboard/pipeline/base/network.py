import json
import os.path as osp
from typing import Optional, Union
from urllib.request import urlopen

import igraph as ig
import leidenalg
import networkx as nx
import pandas as pd

PATH = osp.dirname(osp.realpath(__file__))

HTML_PATH = osp.abspath(osp.join(PATH, "../../vendor/network.html"))
HTML_3D_PATH = osp.abspath(osp.join(PATH, "../../vendor/network-3d.html"))

JS_PATH = osp.abspath(osp.join(PATH, "../../vendor/force-graph-min.js"))
JS_URL = "https://unpkg.com/force-graph"

JS_3D_PATH = osp.abspath(osp.join(PATH, "../../vendor/3d-force-graph-min.js"))
JS_3D_URL = "https://unpkg.com/3d-force-graph"

COLORS = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]


def network(
    edges: pd.DataFrame,
    source: str = "source",
    target: str = "target",
    edge_attr: Optional[Union[str, list]] = None,
    edge_key: Optional[str] = None,
    create_using: nx.Graph = nx.Graph,
) -> tuple:

    G = nx.from_pandas_edgelist(
        edges,
        source=source,
        target=target,
        edge_attr=edge_attr,
        edge_key=edge_key,
        create_using=create_using,
    )

    mod = leidenalg.find_partition(
        ig.Graph.from_networkx(G),
        leidenalg.ModularityVertexPartition,
    )

    nx.set_node_attributes(
        G,
        {node: mod.membership[i] for i, node in enumerate(G.nodes())},
        "community"
    )

    return G, mod


def network_html(
    G: nx.Graph,
    colors: list = COLORS,
    membership: dict = None,
    node_size: float = 1,
    node_label: bool = False,
    edge_arrow: int = 0,
) -> str:
    ids = {node: i for i, node in enumerate(list(G.nodes()))}
    size = pd.Series(dict(G.in_degree()))

    nodes = [
        {
        "id": ids[node],
        "name": node,
        "val": (node_size - 1) * (size[node] - size.min()) / (size.max() - size.min()) + 1,
        "color": colors[membership[node] % len(colors)],
        }
        for node in list(G.nodes())
    ]

    edges = [
        {
        "source": ids[u],
        "target": ids[v],
        "color": "#cccccc",
        }
        for u, v in list(G.edges())
    ]

    with open(HTML_PATH if node_label else HTML_3D_PATH, "r") as f:
        return f.read()\
                .replace("{FORCE_GRAPH}", load_js(JS_PATH, JS_URL))\
                .replace("{FORCE_GRAPH_3D}", load_js(JS_3D_PATH, JS_3D_URL))\
                .replace("{NODES}", json.dumps(nodes))\
                .replace("{LINKS}", json.dumps(edges))\
                .replace("{ARROW_LENGTH}", f"{edge_arrow}")


def load_js(path: str, url: str) -> str:
    if osp.isfile(path):
        with open(path, "r") as f:
            return f.read()
    else:
        content = urlopen(url).read().decode('utf8')
        with open(path, "w") as f:
            f.write(content)
        return content
