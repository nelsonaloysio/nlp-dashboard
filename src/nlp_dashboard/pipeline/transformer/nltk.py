import logging as log
import nltk

from .abc import BaseTransformer

MIN_GRAM_SIZE = 2


class NLTK(BaseTransformer):

    def fit(self, X, y=None, min_gram_size: int = MIN_GRAM_SIZE):
        self.min_gram_size = min_gram_size
        return self

    def transform(self, X: list):
        log.info(f"Generating n-grams with NLTK.")

        ngrams = [
            {
            "bigrams": self.ngrams(x, 2, min_gram_size=self.min_gram_size),
            "trigrams": self.ngrams(x, 3, min_gram_size=self.min_gram_size),
            }
            for x in [x["tokens"] if type(x) == dict else x for x in X]
        ]

        if type(next(iter(X))) == dict:
            list(x.update(g) for x, g in zip(X, ngrams))
            return X

        return ngrams

    @staticmethod
    def ngrams(lst: list, gram_size: int, min_gram_size: int = MIN_GRAM_SIZE) -> list:
        ngrams = []

        for gram in nltk.ngrams(lst, gram_size):
            if all(g for g in gram)\
            and all(len(g) > min_gram_size for g in gram):
                ngrams.append(" ".join(list(gram)))

        return ngrams
