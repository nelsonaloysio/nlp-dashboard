import logging as log
from multiprocessing import cpu_count
from typing import Callable, Literal, Optional, Union

import spacy

from .abc import BaseTransformer

BATCH_SIZE = 500
MIN_LEMMA_SIZE = 1
N_PROCESS = 1


class Spacy(BaseTransformer):

    def fit(
        self,
        X,
        y=None,
        model: Union[str, Callable] = None,
        batch_size: int = BATCH_SIZE,
        min_lemma_size: int = MIN_LEMMA_SIZE,
        n_process : Union[int, Literal["auto"]] = N_PROCESS,
        device: Optional[Literal["cpu", "gpu"]] = None,
    ):
        assert device in (None, "cpu", "gpu"),\
              "Invalid device, expected 'cpu' or 'gpu'."

        if device == "gpu":
            gpu = spacy.require_gpu()
        elif device == "cpu":
            gpu = spacy.require_cpu()
        else:
            try:
                gpu = spacy.prefer_gpu()
            except:
                gpu = spacy.require_cpu()

        self.device = "gpu" if gpu else "cpu"

        self.batch_size = batch_size
        self.min_lemma_size = min_lemma_size

        # NOTE: `n_process` does not support multi-GPUs [spaCy/issues/8783].
        self.n_process = int(cpu_count() if n_process == "auto" else n_process)

        self.model = self._load_model(model)
        assert self.model is not None, f"Unable to load specified spaCy model '{model}'."

        return self

    def transform(self, X: list) -> list:
        log.info(f"Natural language processing (model: {self.model.__module__}, device: {self.device}).")

        docs = [
            self.process_doc(doc, min_lemma_size=self.min_lemma_size)
            for doc in
            self.model.pipe(
                [" ".join(x["tokens"]) if type(x) == dict else x for x in X],
                batch_size=self.batch_size,
                n_process=self.n_process)
        ]

        if type(next(iter(X))) == dict:
            list(x.update(doc) for x, doc in zip(X, docs))
            return X

        return docs

    def process_doc(self, doc, **params) -> dict:
        return {
            "pos_adj": [x[0] for x in self._pos(doc, ["ADJ"], **params)],
            "pos_noun": [x[0] for x in self._pos(doc, ["NOUN"], **params)],
            "pos_verb": [x[0] for x in self._pos(doc, ["VERB"], **params)],
            "noun_chunks": [" ".join([x for x in x.split()]) for x in self._noun_chunks(doc, **params)],
            "ents_person": [" ".join([x for x in x[0].split()]) for x in self._ents(doc, ["PERSON"], **params)],
            "ents_loc": [" ".join([x for x in x[0].split()]) for x in self._ents(doc, ["LOC"], **params)],
            "ents_gpe": [" ".join([x for x in x[0].split()]) for x in self._ents(doc, ["GPE"], **params)],
            # "ents_org": [" ".join([x for x in x[0].split()]) for x in self._ents(doc, ["ORG"], **params)],
            # "lemmas": [x for x in self._lemmas(doc)],
            # "tags": self._tags(doc),
        }


    @staticmethod
    def _ents(x, labels: list = [], min_lemma_size: int = MIN_LEMMA_SIZE) -> list:
        return [
            (ent.text, ent.label_)
            for ent in x.ents
            if (labels == [] or ent.label_ in labels)
            and len(ent.text) >= min_lemma_size
        ]

    @staticmethod
    def _lemmas(x, min_lemma_size: int = MIN_LEMMA_SIZE) -> list:
        return [
            w.lemma_
            for w in x
            if len(w.text) >= min_lemma_size
        ]

    @staticmethod
    def _noun_chunks(x, min_lemma_size: int = MIN_LEMMA_SIZE) -> list:
        return [
            noun_chunk.text
            for noun_chunk in x.noun_chunks
            if len(noun_chunk) >= min_lemma_size
        ]

    @staticmethod
    def _pos(x, pos: list = [], min_lemma_size: int = MIN_LEMMA_SIZE) -> list:
        return [
            (w.text, w.pos_)
            # (w.lemma_, w.pos_)
            for w in x
            if (pos == [] or w.pos_ in pos)
            and len(w.text) >= min_lemma_size
        ]

    @staticmethod
    def _tags(x, tags: list = [], min_lemma_size: int = MIN_LEMMA_SIZE) -> list:
        return [
            (w.lemma_, w.tag_)
            for w in x
            if (tags == [] or w.tag_ in tags)
            and len(w.text) >= min_lemma_size
        ]

    @staticmethod
    def _load_model(model) -> Callable:
        if type(model) == str:
            try:
                return spacy.load(model)
            except OSError:
                try:
                    spacy.cli.download(model)
                    return spacy.load(model)
                except:
                    raise ModuleNotFoundError(model)

        if type(model).__dict__.get("__module__", "").startswith("spacy"):
            return model
