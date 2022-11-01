import random
from typing import Callable, List, Optional, Tuple

import numpy as np
import torch
from sklearn.pipeline import Pipeline

from .transformer.hf import HF
from .transformer.kmeans import KMeans
from .transformer.nltk import NLTK
from .transformer.pandas import Pandas
from .transformer.processor import Processor
from .transformer.reader import Reader
from .transformer.spacy import Spacy
from .transformer.tokenizer import Tokenizer
from .transformer.tsne import TSNE
from .transformer.umap import UMAP


class DataPipeline(Pipeline):

    def __init__(
        self,
        use_hf: bool = False,
        use_kmeans: bool = False,
        use_nltk: bool = False,
        use_pandas: bool = False,
        use_processor: bool = False,
        use_reader: bool = False,
        use_spacy: bool = False,
        use_tokenizer: bool = False,
        use_tsne: bool = False,
        use_umap: bool = False,
        named_steps: Optional[List[str]] = None,
        seed: Optional[int] = None,
    ):
        self.seed = seed

        self.use_hf = use_hf or "hf" in (named_steps or [])
        self.use_kmeans = use_kmeans or "kmeans" in (named_steps or [])
        self.use_nltk = use_nltk or "nltk" in (named_steps or [])
        self.use_pandas = use_pandas or "pandas" in (named_steps or [])
        self.use_processor = use_processor or "processor" in (named_steps or [])
        self.use_reader = use_reader or "reader" in (named_steps or [])
        self.use_spacy = use_spacy or "spacy" in (named_steps or [])
        self.use_tokenizer = use_tokenizer or "tokenizer" in (named_steps or [])
        self.use_tsne = use_tsne or "tsne" in (named_steps or [])
        self.use_umap = use_umap or "umap" in (named_steps or [])

        if self.seed is not None:
            random.seed(self.seed)
            np.random.seed(self.seed)
            torch.manual_seed(self.seed)

        steps = []

        if self.use_reader:
            steps.append(("reader", Reader()))
        if self.use_pandas:
            steps.append(("pandas", Pandas()))
        if self.use_tokenizer:
            steps.append(("tokenizer", Tokenizer()))
        if self.use_nltk:
            steps.append(("nltk", NLTK()))
        if self.use_spacy:
            steps.append(("spacy", Spacy()))
        if self.use_hf:
            steps.append(("hf", HF()))
        if self.use_kmeans:
            steps.append(("kmeans", KMeans()))
        if self.use_tsne:
            steps.append(("tsne", TSNE()))
        if self.use_umap:
            steps.append(("umap", UMAP()))
        if self.use_processor:
            steps.append(("processor", Processor()))

        assert steps != [], "At least one step must be enabled."

        assert not (self.use_tsne and self.use_umap),\
            "Steps `tsne` and `umap` should not be enabled together."

        if named_steps:
            steps = self.reorder_steps(steps, named_steps)

        super().__init__(steps=steps)

    def set_passthroughs(self, **hyperparams):
        passthroughs = []

        if not hyperparams.get("spacy__model"):
            passthroughs.append("spacy")

        if not hyperparams.get("hf__model"):
            passthroughs += ["hf", "kmeans", "tsne", "umap"]

        for step in passthroughs:
            if step in self.named_steps:
                self.steps[list(self.named_steps).index(step)] = (step, "passthrough")

    @staticmethod
    def reorder_steps(steps: List[Tuple[str, Callable]], named_steps: List[str]) -> None:
        ordered_steps = []

        for named_step in named_steps:
            step = [step for step in steps if step[0] == named_step]
            assert step != [], f"Step `{named_step}` not found in pipeline."
            ordered_steps.append(step[0])

        return ordered_steps
