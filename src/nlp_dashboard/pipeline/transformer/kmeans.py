import logging as log
from typing import Literal, Optional, Union

import numpy as np
import pandas as pd
import torch
from kneed import KneeLocator
from sklearn.cluster import KMeans as KMeansCPU, MiniBatchKMeans
from torch_kmeans import KMeans as KMeansCUDA

from .abc import BaseTransformer

INIT = "k-means++"
MAX_ITER = 300
MIN_K = 2
MAX_K = 8
N_INIT = 20
TOL = 1e-4


class KMeans(BaseTransformer):
    """
    K-means clustering algorithm using either CPU or GPU.

    - CPU uses scikit-learn implementation:
        https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html

    - GPU uses torch_kmeans implementation:
        https://torch-kmeans.readthedocs.io/en/latest/
    """
    def fit(
        self,
        X,
        y=None,
        n_clusters: Union[int, list] = None,
        init: Literal["k-means++", "random"] = INIT,
        n_init: int = N_INIT,
        max_iter: int = MAX_ITER,
        tol: float = TOL,
        minibatch: bool = False,
        device: Optional[Literal["cpu", "cuda", "mps"]] = None,
        seed: Optional[int] = None,
        verbose: bool = False,
    ):
        assert device in (None, "cpu", "cuda", "mps"),\
              "Invalid device, expected 'cpu', 'cuda', or 'mps'."

        assert not (type(n_clusters) == int and n_clusters < 2),\
              "Invalid number of clusters, must be greater than 1."

        if not device:
            device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

        if n_clusters is None:
            n_clusters = (MIN_K, MAX_K)

        self.n_clusters = (n_clusters, n_clusters+1) if type(n_clusters) == int else (n_clusters[0], n_clusters[1]+1)
        self.init = init
        self.n_init = n_init
        self.max_iter = max_iter
        self.tol = tol
        self.minibatch = minibatch
        self.device = device
        self.seed = seed
        self.verbose = verbose

        return self

    def transform(self, X: list) -> list:
        if len(X) < 2:
            if type(next(iter(X))) == dict:
                list(x.update({"cluster": 0}) for x in X)
                return X
            return [0]

        kmeans = {}
        min_k, max_k = self.n_clusters[0], min(self.n_clusters[1], len(X))

        z = torch.tensor(np.array([x if type(x) != dict else x["embedding"] for x in X]))
        log.info(f"Clustering samples with K-Means algorithm (device: {self.device}).")

        for k in range(min_k, max_k):
            kmeans[k] = self._init(k)
            self._fit(kmeans[k], z)
            log.info(f"Inertia (k={k}): {self._inertia(kmeans[k])}")

        if len(kmeans) > 1:
            k = self._knee(kmeans)

            # Default to k-value with lower inertia if elbow method is inconclusive.
            if not k:
                inertia = {k: self._inertia(kmeans[k]) for k in kmeans}
                k = next(iter(sorted(inertia, key=lambda x: inertia[x])))

        else:
            k = min_k

        log.info(f"Number of clusters: k={k}")
        kmeans = kmeans[k]

        if self.device == "cpu":
            labels = kmeans.predict(z.data.cpu().numpy())
        else:
            labels = kmeans.predict(z.view(1, z.shape[0], z.shape[1]))\
                           .detach()\
                           .data\
                           .cpu()\
                           .numpy()\
                           .flatten()

        # Reorder labels from largest (1) to smallest (k) cluster.
        top_k = {label: i+1 for i, label in enumerate(pd.Series(labels).value_counts().index)}
        labels = [top_k[label] for label in labels]

        if type(next(iter(X))) == dict:
            list(x.update({"cluster": label}) for x, label in zip(X, labels))
            return X

        return labels

    def _fit(self, km, z):
        if self.device == "cpu":
            km.fit(z.data.cpu().numpy())
        else:
            km.fit(z.view(1, z.shape[0], z.shape[1]))

    def _knee(self, kms: dict):
        inertia = {k: self._inertia(kms[k]) for k in kms}
        return KneeLocator(list(inertia.keys()), list(inertia.values()), curve="convex", direction="decreasing").elbow

    def _inertia(self, km):
        return km.inertia_ if self.device == "cpu" else float(km._result.inertia.numpy())

    def _init(self, k):
        if self.device == "cpu":

            return (MiniBatchKMeans if self.minibatch else KMeansCPU)(
                n_clusters=k,
                init=self.init,
                n_init=self.n_init,
                max_iter=self.max_iter,
                random_state=self.seed,
                verbose=1 if self.verbose else 0,
            )

        elif self.device == "cuda":

            if self.minibatch is True:
                log.warn("MiniBatch K-Means algorithm is only supported in the CPU implementation. "
                         "Defaulting to regular K-Means (torch_kmeans) algorithm.")

            return KMeansCUDA(
                n_clusters=k,
                init=self.init,
                num_init=self.n_init,
                max_iter=self.max_iter,
                seed=self.seed,
                verbose=self.verbose,
            )

        raise AssertionError("Invalid device, expected 'cpu' or 'cuda'.")
