import re
from string import punctuation
from typing import Optional

import numpy as np
import pandas as pd

from .filters import Filters, grep


@staticmethod
def prepare_keywords(keywords):
    return [
        keyword.strip().strip(punctuation)
        for keyword in (keywords.split(",") if isinstance(keywords, str) else keywords)
    ]


class Kwic():

    @staticmethod
    def kwic(
        series: pd.Series,
        keywords: list,
        case_sensitive: bool = False,
        whole_words: bool = False,
        wrap_keywords: bool = True,
    ) -> pd.Series:

        kwic = []
        kwic_index = []

        keywords = prepare_keywords(keywords)

        if not case_sensitive:
            keywords = [keyword.lower() for keyword in keywords]

        for keyword in keywords:
            index = series.index.get_indexer(series.index)
            kws = keyword.split()

            index = index[
                np.in1d(
                    index,
                    Filters.filter_text(
                        series.iloc[index],
                        kws,
                        case_sensitive=case_sensitive,
                        method=all,
                        whole_words=whole_words,
                    )
                )
            ]

            for i, row in enumerate(series.iloc[index]):
                text = (row if case_sensitive else row.lower())
                start = text.find(kws[0])
                end = start + len(kws[0]) + (text[start + len(kws[0]):].find(kws[-1]) + len(kws[-1]) if len(kws) > 1 else 0)

                # Ensure order of keywords is correct.
                matches = [text[start:end].find(kw) for kw in kws]
                if any([matches[i] < matches[i-1] for i in range(len(matches)) if i]):
                    continue

                # Fix: consider rightmost context when multiple matches are found.
                while (start_ := find_word(kws[0], text[start + len(kws[0]):end], whole_words)) != -1\
                and all(text[start + start_ + len(kws[0]):].find(kw) != -1 for kw in kws[:-1]):
                    start += start_ + len(kws[0])

                if all([
                    # Keyword isn't empty.
                    (text[start:end].strip() != ""),
                    # Left and right contexts aren't both empty.
                    ((text[:start].strip() != "") or (text[:-end].strip() != "")),
                    # Optionally consider wrapped keywords only.
                    (" ".join(re.findall(r"(\w+)", text[start:end])) == " ".join([kw.lower() for kw in kws]) if wrap_keywords else True),
                    # Ensure keywords are present, either wholly or partially.
                    all([(grep(kw, text[start:end]) if whole_words else (text[start:end].find(kw) != -1)) for kw in kws]),
                ]):
                    kwic.append((start, end))
                    kwic_index.append(index[i])

        return pd.Series(kwic, index=kwic_index)

    @staticmethod
    def _build_kwic(
        series: pd.Series,
        kwic: list,
        add_more_context_if_pdf_rows: Optional[int] = 0,
        context_size: Optional[int] = None,
        context_split: str = " ",
        value_counts: bool = True
    ) -> pd.DataFrame:

        def add_more_context_if_pdf(head, keyword, tail, index, add_rows=add_more_context_if_pdf_rows):
            if series.index[index].lower().rstrip(")").endswith(".pdf"):
                head = " ".join([" ".join(series.iloc[index - add_rows:index]) if index > 0 else "", head])
                tail = " ".join([tail, " ".join(series.iloc[index + 1:index + 1 + add_rows]) if index < series.shape[0] else ""])
            return (head, keyword, tail)

        def head(text):
            return f"{'… ' if context_size and len(text) > context_size else ''}{' '.join(text[(-context_size) if context_size else None:]).strip()}"

        def tail(text):
            return f"{' '.join(text[:context_size]).strip()}{' …' if context_size and len(text) > context_size else ''}"

        rows = (
            (
            head(row[:context[0]].split(context_split)),
            row[context[0]:context[1]].strip(),
            tail(row[context[1]:].split(context_split)),
            )
            for row, context in zip(series.iloc[kwic.index], kwic.values)
        )

        if not context_size and add_more_context_if_pdf_rows:
            rows = (
                add_more_context_if_pdf(
                    row[0],
                    row[1],
                    row[2],
                    index
                )
            for row, index in zip(rows, kwic.index)
        )

        if value_counts:
            kwic = pd.Series(rows, index=series.iloc[kwic.index].index).value_counts()

            return pd.DataFrame(
                [[match[0], match[1], match[2], value] for match, value in zip(kwic.index, kwic.values)],
                columns=["Left Context", "Keyword", "Right Context", "Occurrences"]
            )

        return pd.DataFrame(
            rows,
            columns=["Left Context", "Keyword", "Right Context"],
            index=series.iloc[kwic.index].index,
        )

    _prepare_keywords = prepare_keywords


def find_word(word: str, text: str, whole_words: bool):
    if whole_words:
        found = re.search(rf"\b{word}\b", text)
        return found.span()[0] if found else -1
    return text.find(word)
