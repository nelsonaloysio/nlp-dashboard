import logging as log
from typing import Callable, Literal, Optional

import numpy as np
import torch
import torch.multiprocessing as mp
from sklearn.metrics.pairwise import cosine_similarity
from tqdm.contrib.concurrent import process_map
from transformers import AutoModel, AutoTokenizer

from .abc import BaseTransformer


class HF(BaseTransformer):

    def fit(
        self,
        X,
        y=None,
        model: str = None,
        max_workers: Optional[int] = None,
        chunksize: Optional[int] = None,
        device: Optional[Literal["cpu", "cuda", "mps"]] = None,
    ):
        assert device in (None, "cpu", "cuda", "mps"),\
              "Invalid device, expected 'cpu', 'cuda', or 'mps'."

        if not device:
            device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

        self.chunksize = chunksize
        self.device = device
        self.max_workers = max_workers

        self.model = self._load_model(model).to(self.device)
        self.tokenizer = self._load_tokenizer(model)

        # TODO: Set up multi-GPU support.
        # self.model.share_memory()
        # self.model.eval()

        assert self.model is not None, f"Unable to load specified HF model '{model}'."

        return self

    def fit_transform(self, X, y=None, **kwargs):
        return self.fit(X, y, **kwargs).transform(X)

    @torch.no_grad()
    def transform(self, X: list) -> list:
        log.info(f"Generating embeddings (model: '{self.model.name_or_path}', device: '{self.device}').")

        # TODO: Introduce parallel processing on CPU.
        # if self.device == "cpu":
        #     H = self.process_map(X)
        # else:
        # self._set_start_method("spawn", force=True)
        H = [self.embedding(x) for x in X]

        if type(next(iter(X))) == dict:
            list(x.update({"embedding": h}) for x, h in zip(X, H))
            return X

        return H

    def embedding(self, x: str) -> np.ndarray:
        h = self.tokenizer(" ".join(x["tokens"]) if type(x) == dict else x,
                           padding=True,
                           truncation=True,
                           return_tensors="pt")

        h = {k: v.to(self.device) for k, v in h.items()}
        z = self.model(**h)
        z = self._mean_pooling(z, h["attention_mask"])[0]

        return z.numpy() if self.device == "cpu" else z.cpu().numpy()

    def process_map(self, X: list, max_workers: Optional[int] = None, chunksize: Optional[int] = None) -> list:
        max_workers = self.max_workers or max_workers or 1
        chunksize = self.chunksize or chunksize or max(len(X) // (max_workers + 2), 1)

        return [h for h in process_map(self.embedding,
                                       X,
                                       ascii=True,
                                       max_workers=max_workers,
                                       chunksize=chunksize,
                                       total=len(X),
                                       desc=f"Embedding (w={max_workers}, c={chunksize})")]

    @staticmethod
    def _load_model(model: str) -> Callable:
        return AutoModel.from_pretrained(model)

    @staticmethod
    def _load_tokenizer(model: str) -> Callable:
        return AutoTokenizer.from_pretrained(model)

    @staticmethod
    def _set_start_method(start_method: str = "fork", force: bool = False) -> None:
        return mp.set_start_method(start_method, force=force)

    @staticmethod
    def _mean_pooling(z, attention_mask):
        token_embeddings = z[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    @staticmethod
    def _calculate_similarity(h1, h2):
        return cosine_similarity([h1], [h2])[0][0]
