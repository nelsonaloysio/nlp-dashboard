from datetime import datetime
from typing import Optional, Union

import logging as log
import numpy as np
import pandas as pd


@staticmethod
def drop_empty(series: pd.Series) -> pd.Series:
    return series.apply(lambda x: None if str(x).strip() == "" else x).dropna()


@staticmethod
def get_min_max(series: pd.Series) -> tuple:
    min_, max_ = None, None

    dtype = series.dtype.type

    if dtype == np.float64:
        dtype = float

    elif dtype == np.int64:
        dtype = int

    if dtype in (float, int):
        try:
            min_, max_ = dtype(series.min()), dtype(series.max())
        except:
            pass

    return min_, max_


@staticmethod
def to_datetime(series: pd.Series, fmt: Optional[str] = None) -> pd.Series:
    try:
        if fmt:
            dates = series.map(lambda x: strptime(x, fmt))
        else:
            try:
                dates = pd.to_datetime(series, unit="s")
            except:
                try:
                    dates = pd.to_datetime(series, format=fmt)
                except:
                    dates = series.map(lambda x: pd.to_datetime(x, errors="coerce", format=fmt))
    except:
        dates = []

    if not len(dates) or not len(dates.dropna()):
        dates = []

    return dates


@staticmethod
def to_number(number: str) -> Union[float, int]:
    if any(_ in number for _ in (",", ".")):
        return float(number.replace(".", ","))
    return int(number)


def strptime(string: str, fmt: str) -> datetime:
    try:
        return datetime.strptime(string, fmt)
    except:
        return None
