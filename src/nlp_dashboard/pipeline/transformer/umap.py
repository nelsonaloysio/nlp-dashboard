import logging as log

import numpy as np
from umap import UMAP as UMAP_

from .abc import BaseTransformer

METRIC = "euclidean"
MIN_DIST = 0.1
N_COMPONENTS = 3
N_NEIGHBORS = 15


class UMAP(BaseTransformer):

    def fit(
        self,
        X,
        y=None,
        metric: str = METRIC,
        min_dist: float = MIN_DIST,
        n_components: int = N_COMPONENTS,
        n_neighbors: int = N_NEIGHBORS,
    ):
        self.metric = metric
        self.min_dist = min_dist
        self.n_components = n_components
        self.n_neighbors = n_neighbors

        assert type(n_components) == int, "Invalid number of components, expected an integer."
        assert n_components > 1, "Invalid number of components, must be greater than 1."

        return self

    def transform(self, X):
        if type(next(iter(X))) == dict and "embedding" not in next(iter(X)):
            log.warn("Missing 'embedding' key in dictionary, skipping UMAP...")
            return X

        log.info("Applying UMAP to embeddings.")

        Z = UMAP_(
            metric=self.metric,
            n_neighbors=self.n_neighbors,
            n_components=self.n_components,
            min_dist=self.min_dist,
        )\
        .fit_transform(
            np.array([x["embedding"] if type(x) == dict else x for x in X])
        )

        if type(next(iter(X))) == dict:
            list(x.update({"embedding": Z[i]}) for i, x in enumerate(X))
            return X

        return Z
