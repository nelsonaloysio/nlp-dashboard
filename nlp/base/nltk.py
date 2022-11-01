import nltk

from .base import Transformer

MIN_GRAM_SIZE = 2


class NLTK(Transformer):

    def fit(self, X, y=None, min_gram_size: int = MIN_GRAM_SIZE):
        self.min_gram_size = min_gram_size
        return self

    def transform(self, X):
        list(
            x.update(
                {
                "bigrams": self.ngrams(x["tokens"], 2, min_gram_size=self.min_gram_size),
                "trigrams": self.ngrams(x["tokens"], 3, min_gram_size=self.min_gram_size),
                }
            )
            for x in X
        )
        return X

    @staticmethod
    def ngrams(lst: list, gram_size: int, min_gram_size: int = MIN_GRAM_SIZE) -> list:
        ngrams = []

        for gram in nltk.ngrams(lst, gram_size):
            if all(g for g in gram)\
            and all(len(g) > min_gram_size for g in gram):
                ngrams.append(" ".join(list(gram)))

        return ngrams
