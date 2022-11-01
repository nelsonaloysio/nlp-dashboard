import logging as log

import numpy as np
from sklearn.manifold import TSNE as TSNE_

from .abc import BaseTransformer

N_COMPONENTS = 2
PERPLEXITY = 30.0


class TSNE(BaseTransformer):

    def fit(self, X, y=None, n_components: int = N_COMPONENTS, perplexity: float = PERPLEXITY):
        self.n_components = n_components
        self.perplexity = perplexity

        assert type(n_components) == int, "Invalid number of components, expected an integer."
        assert n_components > 1, "Invalid number of components, must be greater than 1."

        return self

    def transform(self, X):
        if type(next(iter(X))) == dict and "embedding" not in next(iter(X)):
            log.warn("Missing 'embedding' key in dictionary, skipping t-SNE...")
            return X

        log.info("Applying t-SNE to embeddings.")

        Z = TSNE_(
            n_components=self.n_components,
            perplexity=min(self.perplexity, len(X)-1)
        )\
        .fit_transform(
            np.array([x["embedding"] if type(x) == dict else x for x in X])
        )

        if type(next(iter(X))) == dict:
            list(x.update({"embedding": Z[i]}) for i, x in enumerate(X))
            return X

        return Z
