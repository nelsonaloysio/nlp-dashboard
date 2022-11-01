import logging as log
from random import sample
from time import time

import networkx as nx
import numpy as np
import pandas as pd
import streamlit as st

from ...pipeline.base.network import network
from ...pipeline.pipeline import DataPipeline
from ...pipeline.transformer.umap import UMAP
from ...pipeline.transformer.tsne import TSNE
from ...pipeline.base.wordcloud import wordcloud

SEED = 42
USING_UMAP = True


@classmethod
def process(self) -> None:
    """
    Start processing data and generating artifacts.
    """
    t0 = time()

    # TODO: Cache preprocessed data in session state.
    preprocess_data()

    hyperparams = dict(
        hf__model=st.session_state.config.get("model_hf"),
        kmeans__n_clusters=st.session_state.config.get("n_clusters"),
        kmeans__seed=SEED,
        processor__dates=st.session_state.get("dates"),
        processor__stopwords_custom=st.session_state.config.get("stopwords", {}).get("custom", []),
        processor__stopwords_language=st.session_state.config.get("stopwords", {}).get("language", True),
        spacy__model=st.session_state.config.get("model_spacy"),
    )

    st.session_state.artifacts = self.cache_to_disk(
        process_data,
        X=st.session_state.series,
        **hyperparams
    )

    # Store time elapsed to complete as string.
    t = time() - t0
    st.session_state.time_elapsed = f"{t:.2f}"
    log.info(f"Processed {st.session_state.data.shape} objects ({st.session_state.series.shape[0]} rows) in {t:.2f}s.")

    # Process edge relations to build network.
    st.session_state.artifacts["network"] = process_network()

    # Render page again if successful.
    if "artifacts" in st.session_state:
        # st.session_state.pop("data")
        st.rerun()


@staticmethod
def process_data(X, **hyperparams) -> dict:
    """
    Process data and returns artifacts.
    """
    log.info(f"Processing data, shape: {st.session_state.series.shape}...")

    pipeline = DataPipeline(
        use_hf=True,
        use_kmeans=True,
        use_nltk=True,
        use_processor=True,
        use_spacy=True,
        use_tokenizer=True,
        use_tsne=False,
        use_umap=False,
    )
    pipeline.set_passthroughs(**hyperparams)

    artifacts = pipeline.fit_transform(X, **hyperparams)
    artifacts["wordcloud"] = wordcloud(artifacts["tokens"])

    if "themes" in artifacts:
        list(artifacts["themes"][t].update({"wordcloud": wordcloud(artifacts["themes"][t]["tokens"])})
             for t in artifacts["themes"])

    if "embedding" in artifacts:
        embedding = artifacts.pop("embedding")

        artifacts.update({
            "embedding-3d": (UMAP if USING_UMAP else TSNE)(n_components=3).fit_transform(embedding),
            "embedding-2d": (UMAP if USING_UMAP else TSNE)(n_components=2).fit_transform(embedding),
        })

    return {k: artifacts[k] for k in sorted(artifacts)}


@staticmethod
def process_network() -> None:
    """
    Process network from source and target relations.
    """
    st.write("Processing network...")

    source = st.session_state.config.get("network", {}).get("source")
    target = st.session_state.config.get("network", {}).get("target")
    directed = st.session_state.config.get("network", {}).get("directed")

    if all(_ in st.session_state.data.columns for _ in (source, target)):
        edges = pd.DataFrame({
            "source": st.session_state.data.loc[st.session_state.series.index, source].values,
            "target": st.session_state.data.loc[st.session_state.series.index, target].values,
            "index": st.session_state.series.index.values
        })\
        .map(lambda x: None if x == "" else x)\
        .dropna()

    else:
        return None

    G, mod = network(edges, edge_attr="index", create_using=nx.MultiDiGraph if directed else nx.MultiGraph)

    log.info(f"Graph generated (V={G.order()}, E={G.size()})")
    log.info(f"Communities: {max(mod.membership)+1} (Q={mod.quality():.3f})")

    return G


@staticmethod
def preprocess_data() -> None:
    """
    Process datetimes and text data using the selected parameters.
    """
    log.info(f"Preprocessing data, shape: {st.session_state.data.shape}...")

    index = st.session_state.data.index\
        .get_indexer(st.session_state.data.index)

    # Filter out rows based on text, numeric, and date filters.
    for f in ("filter_text", "filter_numeric", "filter_dates"):
        index_ = st.session_state.get(f)
        if index_ is not None:
            index = index[np.in1d(index, index_)]  # assume_unique=True

    # Get data considering new index.
    series = st.session_state.data\
        [st.session_state.config.get("columns") or st.session_state.data.columns]\
        .iloc[index]\
        .astype(str)\
        .apply(" ".join, axis=1)

    # Filter out empty and null rows...
    series = series\
        .apply(lambda x: None if not x.strip() else x)\
        .dropna()

    # ...and proceed only if data is still valid.
    if series.shape[0] == 0:
        return

    # Filter duplicates out, get N-rows sample from data set.
    if st.session_state.config.get("rows", {}).get("unique"):
        series = series.drop_duplicates()

    if st.session_state.config.get("rows", {}).get("random"):
        series = series.iloc[
            sample(
                series.index.get_indexer(series.index).tolist(),
                st.session_state.config["rows"]["value"]
            )
        ]

    # Consider only N-rows from data set.
    series = series[:st.session_state.config.get("rows", {}).get("value", None)]

    # Store dates considering newly created series.
    if st.session_state.get("dates") is not None:
        st.session_state.dates.name = "Date"
        st.session_state.dates = st.session_state.dates.iloc[series.index.get_indexer(series.index)].dropna()
        series =  series.iloc[st.session_state.dates.index.get_indexer(st.session_state.dates.index)]

    # Store series in session state.
    st.session_state.series = series
