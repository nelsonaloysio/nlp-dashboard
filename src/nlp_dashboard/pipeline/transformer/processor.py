import json
import logging as log
from datetime import datetime
from typing import Optional, Union

import pandas as pd

from ..base.stopwords import load_stopwords
from ..base.time import fill_time_series
from .abc import BaseTransformer

INDENT = 0
MAX_GROUPS = 100
MAX_OBJECTS = 100
MIN_TIME_STEPS = 3


class Processor(BaseTransformer):

    def fit(
        self,
        X,
        y=None,
        dates: Optional[list] = None,
        json: bool = False,
        max_groups: int = MAX_GROUPS,
        max_objects: int = MAX_OBJECTS,
        min_time_steps: int = MIN_TIME_STEPS,
        stopwords_custom: Optional[list] = None,
        stopwords_language: Optional[Union[str, list, bool]] = True,
        time_format: str = None,
    ):
        self.dates = self.__dates(dates, min_time_steps, time_format)
        self.json = json
        self.max_groups = max_groups
        self.max_objects = max_objects
        self.min_time_steps = min_time_steps
        self.stopwords = []

        if stopwords_language:
            self.stopwords += load_stopwords(stopwords_language)

        if stopwords_custom:
            self.stopwords += (stopwords_custom or [])

        return self

    def transform(self, X, iloc=None) -> list:
        log.info("Processing output into artifacts.")

        keys = sorted(set([x for x in X for x in x]))

        X = X if iloc is None else X.iloc[iloc]
        dates = self.dates.iloc[iloc] if self.dates is not None and iloc is not None else self.dates

        # Store cluster labels and embeddings as lists.
        cluster, embedding = None, None

        if iloc is not None:
            keys.remove("cluster")
            keys.remove("embedding")

        if "cluster" in keys:
            cluster = [x["cluster"] for x in X]
            keys.remove("cluster")

        if "embedding" in keys:
            embedding = [x["embedding"].tolist() if self.json else x["embedding"] for x in X]
            keys.remove("embedding")

        # Process data into a single dictionary.
        X_ = {
            key:
                pd
                .Series([x.get(key, []) for x in X], index=dates)
                .apply(lambda x: set(x) if type(x) == list else x)
                .explode()
                .dropna()
                .apply(lambda x: x if type(x) != str else x.lower() if len(x) > 1 else None)
                .dropna()
            for key in keys
        }

        # Add '#' and '@' to hashtags and mentions.
        for key, prefix in (("hashtags", "#"), ("mentions", "@")):
            if key in keys:
                X_[key] = X_[key].apply(lambda x: f"{prefix}{x.lower()}")

        # Count values and drop stop words.
        Y = {
            key:
                X_[key]
                .value_counts()
                .drop(self.stopwords, errors="ignore")
                [:self.max_objects]
            for key in keys
        }

        # Drop bigrams and trigrams with >2 valid words.
        for key, minimum in (("bigrams", 2), ("trigrams", 2)):
            if key in keys:
                Y[key] = Y[key].loc[[
                    x
                    for x in Y[key].index
                    if len([_ for _ in x.split() if _ not in self.stopwords]) >= minimum
                ]]

        # Generate time series for each key, if available.
        if dates is not None:
            X_.update({
                "time_series":
                    dates.value_counts().sort_index()
            })
            X_.update({
                f"{key}_over_time":
                    self
                    .__groupby_series(X_[key], Y[key].index[:self.max_groups])
                    .value_counts()
                for key in keys
            })

        # Update remaining keys with value counts.
        X_.update({
            key: Y[key]
            for key in keys
        })

        # Capitalize tokens if not uppercased.
        X_.update({
            k: self.__capitalize(X_[k])
            for k in X_
            if type(X_[k]) in (pd.Series, pd.DataFrame)
        })

        # Transform multi-index series to data frames.
        X_.update({
            k: pd.DataFrame({
                "index": [x[0] for x in X_[k].index],
                "category": [x[1] for x in X_[k].index],
                "value": X_[k].values.tolist(),
            })
            for k in X_
            if k.endswith("_over_time")
        })

        # Add index to dictionary.
        if iloc is not None:
            X_["index"] = iloc

        # Generate artifacts for each subset.
        if cluster is not None:
            X_["cluster"] = cluster

            X_["themes"] = {
                k: self.transform(X, iloc=[i for i, k_ in enumerate(cluster) if k == k_])
                for k in sorted(set(cluster))
            }

            if dates is not None:
                X_["themes_over_time"] = pd.concat([
                    pd.DataFrame(
                        [(i, k, v) for i, v in (json.loads(X_["themes"][k]["time_series"]) if self.json else X_["themes"][k]["time_series"]).items()],
                        columns=["index", "category", "value"]
                    )
                    for k in X_["themes"]
                ])\
                .reset_index()\
                .drop("level_0", axis=1)

                X_["attention"] = [
                    fill_time_series(X_["themes_over_time"], index=X_["time_series"].index)
                    .query(f"category == {c}")
                    ["value"]
                    .values
                    .tolist()
                    for c in X_["themes_over_time"].category.unique()
                ]

        # Store embedding vectors.
        if embedding is not None:
            X_["embedding"] = embedding

        # Return output as JSON-structured data.
        if self.json:
            X_.update({
                k: X_[k].to_json(indent=INDENT)
                if type(X_[k]) in (pd.Series, pd.DataFrame)
                else json.dumps(X_[k])
                for k in X_
            })

        # Sort dictionary keys.
        X_ = {k: X_[k] for k in sorted(X_)}

        return X_

    @staticmethod
    def __capitalize(series: pd.Series):
        return pd.Series(
            series.values,
            index=(
                [" ".join([w.capitalize() for w in x.split() if not w.isupper()]) for x in series.index]
                if
                    type(series.index[0]) == str
                else
                    [(x[0], " ".join([w.capitalize() for w in x[1].split() if not w.isupper()])) for x in series.index]
            ) if series.shape[0] else series.index,
        )

    @staticmethod
    def __dates(dates: list, min_time_steps: int = MIN_TIME_STEPS, time_format: str = None):
        dates_ = None

        if dates is not None:

            if len(dates) and type(dates) != pd.Series:
                dates = pd.Series(dates)

            dates = pd.to_datetime(dates)

            if time_format:
                dates_ = dates.apply(lambda x: datetime.strftime(x, time_format))
            else:
                for time_format in ["", "%H", "%H:%M", "%H:%M:%S"]:
                    dates_ = dates.apply(lambda x: datetime.strftime(x, f"%Y-%m-%d {time_format}"))
                    if dates_.unique().shape[0] >= min_time_steps:
                        break

        return dates_

    @staticmethod
    def __groupby_series(x: pd.Series, y: list):
        x = x.iloc[[i for i, value in enumerate(x.values) if value in y]]
        return x.groupby(x.index)
