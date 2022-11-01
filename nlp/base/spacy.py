from multiprocessing import cpu_count
from typing import Callable, Literal, Union

import spacy

from .base import Transformer

BATCH_SIZE = 500
MIN_LEMMA_SIZE = 1
N_PROCESS = 1


class Spacy(Transformer):

    def fit(
        self,
        X,
        y=None,
        batch_size: int = BATCH_SIZE,
        min_lemma_size: int = MIN_LEMMA_SIZE,
        model: Union[str, Callable] = None,
        n_process : Union[int, Literal["auto"]] = N_PROCESS,
    ):
        self.batch_size = batch_size
        self.min_lemma_size = min_lemma_size
        self.model = self.__model(model)
        self.n_process = self.__n_process(n_process)
        return self

    def transform(self, X: list) -> list:
        if type(self.model) != type(None):
            list(
                x.update(
                    {
                    "pos_adj": [x[0] for x in self._pos(doc, ["ADJ"], min_lemma_size=self.min_lemma_size)],
                    "pos_noun": [x[0] for x in self._pos(doc, ["NOUN"], min_lemma_size=self.min_lemma_size)],
                    "pos_verb": [x[0] for x in self._pos(doc, ["VERB"], min_lemma_size=self.min_lemma_size)],
                    "noun_chunks": [" ".join([x for x in x.split()]) for x in self._noun_chunks(doc, min_lemma_size=self.min_lemma_size)],
                    "ents_person": [" ".join([x for x in x[0].split()]) for x in self._ents(doc, ["PERSON"], min_lemma_size=self.min_lemma_size)],
                    "ents_loc": [" ".join([x for x in x[0].split()]) for x in self._ents(doc, ["LOC"], min_lemma_size=self.min_lemma_size)],
                    "ents_gpe": [" ".join([x for x in x[0].split()]) for x in self._ents(doc, ["GPE"], min_lemma_size=self.min_lemma_size)],
                    # "ents_org": [" ".join([x for x in x[0].split()]) for x in self._ents(doc, ["ORG"], min_lemma_size=self.min_lemma_size)],
                    # "lemmas": [x for x in self._lemmas(doc)],
                    # "tags": self._tags(doc),
                    }
                )
                for x, doc in zip(X, self.doc(X))
            )
        return X

    def doc(self, X: list) -> list:
        return self.model.pipe(
            [" ".join(x["tokens"]) for x in X],
            batch_size=self.batch_size,
            n_process=self.n_process,
        )

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
    def __model(model) -> Callable:
        if type(model) == str:
            return spacy.load(model) if model else None
        return model

    @staticmethod
    def __n_process(n_process) -> int:
        return int(cpu_count() if n_process == "auto" else n_process)
