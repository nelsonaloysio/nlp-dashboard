from datetime import datetime
from typing import Optional, Union

import pandas as pd

from .base import Transformer
from .stopwords import stopwords

MAX_GROUPS = 100
MAX_OBJECTS = 100
MIN_TIME_STEPS = 3


class Processor(Transformer):

    def fit(
        self,
        X,
        y=None,
        custom_stopwords: Optional[list] = None,
        dates: Optional[list] = None,
        max_groups: int = MAX_GROUPS,
        max_objects: int = MAX_OBJECTS,
        min_time_steps: int = MIN_TIME_STEPS,
        stopwords: Optional[Union[str, list, bool]] = True,
    ):
        self.custom_stopwords = custom_stopwords
        self.dates = self.__dates(dates, min_time_steps)
        self.max_groups = max_groups
        self.max_objects = max_objects
        self.min_time_steps = min_time_steps
        self.stopwords = stopwords
        return self

    def transform(self, X) -> list:
        keys = sorted(set([x for x in X for x in x]))

        stop_words = []
        if self.stopwords:
            stop_words += stopwords(self.stopwords)
        if self.custom_stopwords:
            stop_words += (self.custom_stopwords or [])

        # Expand lists and transform syntagmas to lowercases.
        X_ = {
            key:
                pd
                .Series([x.get(key, []) for x in X], index=self.dates)
                .apply(lambda x: set(x) if type(x) == list else x)
                .explode()
                .dropna()
                .apply(lambda x: x.lower() if len(x) > 1 else None)
                .dropna()
            for key in keys
        }

        # Count values above and drop stop words.
        Y = {
            key:
                X_[key]
                .value_counts()
                .drop(stop_words, errors="ignore")
                [:self.max_objects]
            for key in keys
        }
        for key, value in (("bigrams", 2), ("trigrams", 2)):
            Y[key] = Y[key].loc[[
                x
                for x in Y[key].index
                if len([_ for _ in x.split() if _ not in stop_words]) >= value
            ]]

        # Generate time series for each key, if available.
        if type(self.dates) != type(None):
            X_.update(
                {
                "time_series":
                    self.dates.value_counts()
                }
            )
            X_.update(
                {
                f"{key}_over_time":
                    self
                    .__groupby_series(X_[key], Y[key].index[:self.max_groups])
                    .value_counts()
                for key in keys
                }
            )

        # Update remaining keys with value counts.
        X_.update({
            key:
                Y[key]
            for key in keys
        })

        # Capitalize syntagmas in series indices.
        X_ = {k: self.__capitalize(X_[k]) for k in X_}

        # Transform multi-index series to data frames.
        X_.update({k: self.__series_multi_to_df(X_[k]) for k in X_ if k.endswith("_over_time")})

        # Return sorted dictionary keys.
        return {k: X_[k] for k in sorted(X_)}

    @staticmethod
    def __capitalize(series: pd.Series):
        return pd.Series(
            series.values,
            index=(
                [" ".join([w.capitalize() for w in x.split()]) for x in series.index]
                if
                    type(series.index[0]) == str
                else
                    [(x[0], " ".join([w.capitalize() for w in x[1].split()])) for x in series.index]
            ) if series.shape[0] else series.index,
        )

    @staticmethod
    def __dates(dates: list, min_time_steps: int = MIN_TIME_STEPS):
        dates_ = None
        if type(dates) != type(None):
            dates = pd.to_datetime(dates)
            for time_format in ["", "%H", "%H:%M", "%H:%M:%S"]:
                dates_ = dates.apply(lambda x: datetime.strftime(x, f"%Y-%m-%d {time_format}"))
                if dates_.unique().shape[0] >= min_time_steps:
                    break
        return dates_

    @staticmethod
    def __groupby_series(x: pd.Series, y: list):
        x = x.iloc[[i for i, value in enumerate(x.values) if value in y]]
        return x.groupby(x.index)

    @staticmethod
    def __series_multi_to_df(series: pd.Series, x="index", y="value", c="category"):
        return pd.DataFrame({
            x: [x[0] for x in series.index],
            c: [x[1] for x in series.index],
            y: [v for v in series.values],
        })
