import logging as log
import re
from string import ascii_letters, digits, punctuation
from typing import Union

import pandas as pd
# from sklearn.feature_extraction.text import strip_accents_ascii

from .abc import BaseTransformer

ACCENT_REPLACEMENTS = {
    ord("á"): "a", ord("ã"): "a", ord("â"): "a",
    ord("à"): "a", ord("è"): "e", ord("ê"): "e",
    ord("é"): "e", ord("í"): "i", ord("ì"): "i",
    ord("ñ"): "n", ord("ò"): "o", ord("ó"): "o",
    ord("ô"): "o", ord("õ"): "o", ord("ù"): "u",
    ord("ú"): "u", ord("ü"): "u", ord("ç"): "c"}

INVALID_CHARACTERS = punctuation + "'\\\"–—¡¿…‘’“”„,•·|"
CHARACTER_REPLACEMENTS = str.maketrans(" ", " ", INVALID_CHARACTERS)
VALID_CHARACTERS = ascii_letters + digits + "áãâàèêéíìñòóôõùúüç"

# Usernames, Hashtags and mentions
USERNAME_CHARACTERS = VALID_CHARACTERS + "_@#."

EMOJI_REPLACEMENTS = re.compile(
    "["
    u"\U0001F600-\U0001F64F"  # Emoticons
    u"\U0001F300-\U0001F5FF"  # Symbols & pictographs
    u"\U0001F680-\U0001F6FF"  # Transport & map symbols
    u"\U0001F1E0-\U0001F1FF"  # Flags (iOS)
    u"\U00002702-\U000027B0"  # Extra (1)
    u"\U000024C2-\U0001F251"  # Extra (2)
    "]+",
    flags=re.UNICODE
)

REPLACE_WITH = {
    "’": "'",
    "'s": " ",
    "\n": " ",
    "\r": " ",
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


class Tokenizer(BaseTransformer):

    def fit(
        self,
        X,
        y=None,
        text: bool = False,
        tokens: bool = True,
        hashtags: bool = True,
        mentions: bool = True,
        numbers: bool = False,
        urls: bool = False,
        clear_accents: bool = False,
        clear_characters: bool = False,
        clear_emojis: bool = False,
    ):
        self.text = text
        self.tokens = tokens
        self.hashtags = hashtags
        self.mentions = mentions
        self.numbers = numbers
        self.urls = urls
        self.clear_accents = clear_accents
        self.clear_characters = clear_characters
        self.clear_emojis = clear_emojis
        return self

    def transform(self, X: Union[list, pd.Series]):
        log.info("Tokenizing text.")

        hashed = {x: None for x in X}
        hashed = {x: self.tokenize(x) for x in list(hashed)}

        if type(X) == pd.Series:
            z = X.map(lambda x: {"text": x}|hashed[x] if self.text else hashed[x])
        else:
            z = [{"text": x}|hashed[x] if self.text else hashed[x] for x in X]

        return z

    def tokenize(self, s: str):
        x = {}

        s = self._replace_with(s)

        if self.clear_accents:
            s = self._clear_accents(s)
        if self.clear_characters:
            s = self._clear_characters(s)
        if self.clear_emojis:
            s = self._clear_emojis(s)

        s = s.split()

        x = {
            "hashtags": [Tokenizer._clear_token(s.pop(i).lstrip("#"), USERNAME_CHARACTERS) for i in self._find_hashtags(s)[::-1]],
            "mentions": [Tokenizer._clear_token(s.pop(i).lstrip("@"), USERNAME_CHARACTERS) for i in self._find_mentions(s)[::-1]],
            "numbers": [s.pop(i) for i in self._find_numbers(s)[::-1]],
            "urls": [s.pop(i) for i in self._find_urls(s)[::-1]],
            "tokens": self._get_tokens(s),
        }

        return {key: x[key]
               for key in ("tokens", "hashtags", "mentions", "numbers", "urls")
               if getattr(self, key)}

    @staticmethod
    def _clear_accents(s: str, replacements: dict = ACCENT_REPLACEMENTS) -> str:
        return s.translate(replacements)

    @staticmethod
    def _clear_characters(s: str, replacements: dict = CHARACTER_REPLACEMENTS) -> str:
        return s.translate(replacements)

    @staticmethod
    def _clear_emojis(s: str, pattern: re.Pattern) -> str:
        return pattern.sub(r"", s)

    @staticmethod
    def _clear_token(s: str, valid_characters: str = VALID_CHARACTERS) -> str:
        return "".join([_ for _ in s if _ in valid_characters])

    @staticmethod
    def _find_hashtags(lst: list) -> list:
        return [i for i, x in enumerate(lst) if len(x) > 1 and x[:1] == "#"]

    @staticmethod
    def _find_mentions(lst: list) -> list:
        return [i for i, x in enumerate(lst) if len(x) > 1 and x[:1] == "@"]

    @staticmethod
    def _find_numbers(lst: list) -> list:
        return [i for i, x in enumerate(lst) if x.lstrip("-").replace(".", "", 1).replace(",", "", 1).replace("e-", "", 1).replace("e", "", 1).isdigit()]

    @staticmethod
    def _find_urls(lst: list) -> list:
        return [i for i, x in enumerate(lst) if any(x.startswith(_) for _ in URL_STARTSWITH)]

    @staticmethod
    def _get_tokens(lst: list) -> list:
        lst = [Tokenizer._clear_token(x) for x in lst]
        return [token for i, token in enumerate(lst) if token and i not in Tokenizer._find_numbers(lst)]

    @staticmethod
    def _replace_with(s: str, replacements: dict = REPLACE_WITH):
        for k, v in replacements.items():
            s = s.replace(k, v)
        return s

    @staticmethod
    def _split_words(s: str) -> list:
        return re.findall(r"(\w+)", s)

    @staticmethod
    def _strip_characters(s: str, characters: str = INVALID_CHARACTERS) -> str:
        return s.strip(characters)
