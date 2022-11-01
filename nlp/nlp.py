from sklearn.pipeline import Pipeline

from .base import (
    NLTK,
    Pandas,
    Processor,
    Spacy,
    Tokenizer,
)


class NLP(Pipeline):

    def __init__(
        self,
        use_nltk: bool = True,
        use_pandas: bool = True,
        use_processor: bool = True,
        use_spacy: bool = True,
        use_tokenizer: bool = True,
    ):
        steps = []

        self.use_nltk = use_nltk
        self.use_pandas = use_pandas
        self.use_processor = use_processor
        self.use_spacy = use_spacy
        self.use_tokenizer = use_tokenizer

        if self.use_pandas:
            steps.append(
                ("pandas", Pandas())
            )

        if self.use_tokenizer:
            steps.append(
                ("tokenizer", Tokenizer())
            )

        if self.use_nltk:
            steps.append(
                ("nltk", NLTK())
            )

        if self.use_spacy:
            steps.append(
                ("spacy", Spacy())
            )

        if self.use_processor:
            steps.append(
                ("processor", Processor())
            )

        assert(steps != [])

        super().__init__(steps=steps)
