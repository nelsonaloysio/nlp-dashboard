import re
from datetime import datetime
from typing import Union

import pandas as pd


def filter_text(
    data: Union[pd.DataFrame, pd.Series],
    values: list = [],
    case_sensitive: bool = False,
    method: Union[any, all] = any,
    whole_words: bool = True,
) -> pd.Index:

    assert(method == all or method == any)

    df = pd.DataFrame(data.astype(str))

    if not case_sensitive:
        df = df.map(str.lower)
        values = [v.lower() for v in values]

    return df.index.get_indexer(
        df
        .map(
            lambda x:
            # Regular expression is costly, so let's try and avoid it whenever possible.
            True if method(v in x and (not whole_words or grep(v, x)) for v in values) else None
        )
        .dropna(how="all")
        .index
    )


def filter_dates(
    series: pd.Series,
    min_date: datetime.date,
    min_time: datetime.time,
    max_date: datetime.date,
    max_time: datetime.time
) -> pd.Index:

    min_datetime = datetime.strptime(
        "%s %s" % (min_date.strftime("%Y-%m-%d"), min_time.strftime("%H:%M:%S")),
        "%Y-%m-%d %H:%M:%S"
    )
    max_datetime = datetime.strptime(
        "%s %s" % (max_date.strftime("%Y-%m-%d"), max_time.strftime("%H:%M:%S")),
        "%Y-%m-%d %H:%M:%S"
    )
    return series.index.get_indexer(
        series
        [max_datetime >= series]
        [series >= min_datetime]
        .index
    )


def filter_numeric(
    series: pd.Series,
    min_value: Union[float, int],
    max_value: Union[float, int],
) -> pd.Index:

    return series.index.get_indexer(
        series
        [max_value >= series]
        [series >= min_value]
        .index
    )


def grep(word, text=""):
    return True if re.search(rf"\b{word}\b", text) else False  # .group()
