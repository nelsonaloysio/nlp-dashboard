import streamlit as st

from ...pipeline.transformer.kmeans import MIN_K, MAX_K


@classmethod
def configure_cluster(self) -> None:
    self.title("Number of clusters", h=5)

    e1, e2 = st.empty(), st.empty()
    disabled = st.session_state.config.get("model_hf") is None

    if disabled:
        self.info("Please load a clustering model first to define the number of clusters.")

    with e2:
        auto = st.checkbox(
            "Automatically select optimal number of clusters.",
            key="kmeans_auto",
            disabled=disabled,
            value=True,
        )

    with e1:
        n_clusters = st.slider(
            "Please specify the number of clusters to discover.",
            key="n_clusters",
            disabled=disabled or auto,
            min_value=MIN_K,
            max_value=MAX_K,
            value=MAX_K//2,
        )

    st.session_state.config["n_clusters"] = None if disabled or auto or st.session_state.kmeans_auto else n_clusters
    st.caption("K-Means clustering is used to discover clusters based on semantic similarity.")
