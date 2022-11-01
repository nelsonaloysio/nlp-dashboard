import re
from string import punctuation

import pandas as pd

from .base import Transformer

ACCENT_REPLACEMENTS = {
    ord("á"): "a", ord("ã"): "a", ord("â"): "a",
    ord("à"): "a", ord("è"): "e", ord("ê"): "e",
    ord("é"): "e", ord("í"): "i", ord("ì"): "i",
    ord("ñ"): "n", ord("ò"): "o", ord("ó"): "o",
    ord("ô"): "o", ord("õ"): "o", ord("ù"): "u",
    ord("ú"): "u", ord("ü"): "u", ord("ç"): "c"}

VALID_CHARACTERS = "_@#" # '
INVALID_CHARACTERS = punctuation
INVALID_CHARACTERS += "'\\\"–—¡¿…‘’“”„,•·|"

INVALID_CHARACTERS = "".join(
    set(INVALID_CHARACTERS) - set(VALID_CHARACTERS)
)

CHARACTER_REPLACEMENTS = str.maketrans(" ", " ", INVALID_CHARACTERS)

EMOJI_REPLACEMENTS = re.compile(
    "["
    u"\U0001F600-\U0001F64F"  # emoticons
    u"\U0001F300-\U0001F5FF"  # symbols & pictographs
    u"\U0001F680-\U0001F6FF"  # transport & map symbols
    u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
    u"\U00002702-\U000027B0"  # extra
    u"\U000024C2-\U0001F251"  # extra
    "]+",
    flags=re.UNICODE
)

REPLACE_WITH = {
    "\n": " ",
    "](": " ",
    "&amp;": " & ",
    "ftp": " ftp",
    "http": " http",
    "www": " www",
}

URL_STARTSWITH = [
    "ftp",
    "http",
    "www",
]


class Tokenizer(Transformer):

    def fit(
        self,
        X,
        y=None,
        clear_accents: bool = False,
        clear_characters: bool = False,
        clear_emojis: bool = False,
        find_words: bool = True,
        ignore_numbers: bool = True,
    ):
        self.clear_accents = clear_accents
        self.clear_characters = clear_characters
        self.clear_emojis = clear_emojis
        self.find_words = find_words
        self.ignore_numbers = ignore_numbers
        return self

    def transform(self, X: pd.Series):
        return X.apply(self.tokenize)

    def tokenize(self, text: str):
        if self.clear_accents:
            text = self._clear_accents(text)

        if self.clear_characters:
            text = self._clear_characters(text)

        if self.clear_emojis:
            text = self._clear_emojis(text)

        tokens = [self._strip_characters(s) for s in self._replace_with(text).split()]
        hashtags = [tokens.pop(i) for i in self._find_hashtags(tokens)[::-1]]
        mentions = [tokens.pop(i) for i in self._find_mentions(tokens)[::-1]]
        urls = [tokens.pop(i) for i in self._find_urls(tokens)[::-1]]

        if self.ignore_numbers:
            numbers = [tokens.pop(i) for i in list(range(len(tokens)))[::-1] if self._is_number(tokens[i])]

        if self.find_words:
            tokens = self._find_words(" ".join(tokens))

        return {
            # "text": text,
            "tokens": tokens,
            "hashtags": hashtags,
            "mentions": mentions,
            # "numbers": numbers,
            # "urls": urls,
        }

    @staticmethod
    def _clear_accents(s: str) -> str:
        return s.translate(ACCENT_REPLACEMENTS)

    @staticmethod
    def _clear_characters(s: str) -> str:
        return s.translate(CHARACTER_REPLACEMENTS)

    @staticmethod
    def _clear_emojis(s: str) -> str:
        return EMOJI_REPLACEMENTS.sub(r"", s)

    @staticmethod
    def _find_hashtags(lst: list) -> list:
        return [lst.index(x) for x in lst if x.startswith("#") and len(x) > 1]

    @staticmethod
    def _find_mentions(lst: list) -> list:
        return [lst.index(x) for x in lst if x.startswith("@") and len(x) > 1]

    @staticmethod
    def _find_urls(lst: list) -> list:
        return [lst.index(x) for x in lst if any(x.startswith(_) for _ in URL_STARTSWITH)]

    @staticmethod
    def _find_words(s: str) -> list:
        return re.findall(r"(\w+)", s)

    @staticmethod
    def _is_number(s: str) -> bool:
        try:
            int(s)
        except:
            try:
                float(s)
            except:
                return False
        return True

    @staticmethod
    def _replace_with(s: str):
        for k, v in REPLACE_WITH.items():
            s = s.replace(k, v)
        return s

    @staticmethod
    def _strip_characters(s: str) -> str:
        return s.strip(INVALID_CHARACTERS)
