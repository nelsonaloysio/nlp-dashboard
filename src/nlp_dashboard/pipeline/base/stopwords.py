import json
import os.path as osp
from functools import reduce
from typing import Optional, Union

from nltk.corpus import stopwords as nltk_stopwords

PATH = osp.dirname(osp.dirname((osp.realpath(__file__))))

LANGUAGES = [
    "catalan",     # 825 strings
    "chinese",     # 119 strings
    "common",      # 4 strings
    "english",     # 777 strings
    "french",      # 1317 strings
    "german",      # 616 strings
    "italian",     # 443 strings
    "japanese",    # 44 strings
    "portuguese",  # 806 strings
    "russian",     # 421 strings
    "spanish",     # 491 strings
]


def load_stopwords(
    languages: Optional[Union[str, list]] = None,
    use_common_stopwords: bool = True,
    use_nltk: bool = False
) -> set:
    if languages == False:
        return set()

    if languages in (True, None):
        languages = None if use_nltk else LANGUAGES

    if type(languages) == str:
        languages = [languages]

    if use_common_stopwords and not use_nltk:
        languages.append("common")

    return set(
        reduce(
            lambda x, y: x + y,
            [(nltk_stopwords.words(lang) if use_nltk else __load_stopwords(lang)) for lang in languages]
        )
    )


def __load_stopwords(language: str) -> list:
    json_file = osp.join(PATH, f"lib/stopwords/{language}.json")

    if osp.isfile(json_file):
        with open(json_file, "r") as j:
            return json.load(j)

    raise FileNotFoundError(f"File not foud: '{json_file}'.")
