import logging as log
from random import sample
from time import time

import numpy as np
import streamlit as st


class Artifacts():

    def __init__(self) -> None:
        """ Initializes class. """

    def generate_artifacts(self) -> None:
        t0 = time()

        data = st.session_state.data
        log.info(f"Processing {data.shape} objects with parameters: {st.session_state.config}...")

        # Get index intersection.
        index = data.index.get_indexer(data.index)

        for f in ("filter_text", "filter_interval", "filter_dates"):
            index_ = st.session_state.get(f)
            if index_ is not None:
                index = index[np.in1d(index, index_)]  # assume_unique=True

        # Get text data considering new index.
        st.session_state.series = (
            data
            [st.session_state.config["columns"] or data.columns]
            .iloc[index]
            .astype(str)
            .apply(" ".join, axis=1)
        )

        # Filter out empty and null rows...
        st.session_state.series = st.session_state.series\
            .apply(lambda x: None if not x.strip() else x)\
            .dropna()

        # ...and proceed only if data is still valid.
        if st.session_state.series.shape[0] == 0:
            return

        # Filter duplicates out, get N-rows sample from data set.
        if st.session_state.config["rows"]["unique"]:
            st.session_state.series = st.session_state.series.drop_duplicates()

        if st.session_state.config["rows"]["random"]:
            st.session_state.series = st.session_state.series.iloc[
                sample(st.session_state.series.index.get_indexer(st.session_state.series.index).tolist(),
                       st.session_state.config["rows"]["value"])
            ]

        st.session_state.series = st.session_state.series[:st.session_state.config["rows"]["value"]]

        # Store dates considering newly created series.
        if type(st.session_state.get("dates")) != type(None):
            st.session_state.dates = st.session_state.dates.iloc[st.session_state.series.index.get_indexer(st.session_state.series.index)]

        # Generate artifacts, cache them to disk.
        st.session_state.artifacts = self.cache_to_disk(
            self.pipeline,
            X=st.session_state.series,
            processor__custom_stopwords=st.session_state.config["stopwords"]["custom"],
            processor__dates=st.session_state.get("dates"),
            processor__stopwords=st.session_state.config["stopwords"]["language"],
            spacy__model=st.session_state.config.get("model"),
        )

        # Render word cloud from tokens.
        st.session_state.artifacts["wordcloud"] = self.wordcloud(st.session_state.artifacts["tokens"])

        # Store time elapsed to complete as string.
        st.session_state.time_elapsed = f"{float(time()-t0):.2f}"
        log.info(f"Processed {st.session_state.data.shape} objects ({st.session_state.series.shape[0]} rows) in {st.session_state.time_elapsed}s.")

        # Render page again if successful.
        self.rerun(True if "artifacts" in st.session_state else False)
