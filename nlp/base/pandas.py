import json
from typing import Union

import pandas as pd

from .base import Transformer


class Pandas(Transformer):
    """
    Transform path or data frame into series object.
    """
    def fit(
        self,
        X,
        y=None,
        applymap=lambda x: x,
        column=None,
        compression="infer",
        drop_duplicates=False,
        dropna=False,
        engine=None,
        json_lines=False,
        json_normalize=False,
        low_memory=True,
        nrows=None,
        sep=None,
        sort=[],
    ):
        self.applymap = applymap
        self.column = column
        self.compression = compression
        self.drop_duplicates = drop_duplicates
        self.dropna = dropna
        self.engine = engine
        self.json_lines = json_lines
        self.json_normalize = json_normalize
        self.low_memory = low_memory
        self.nrows = nrows
        self.sep = sep
        self.sort = sort
        return self

    def transform(self, path_or_df: Union[str, pd.Series, pd.DataFrame]):
        """ Returns Pandas Series from data frame or file path. """
        usecols = [self.column] + self.sort if self.column else None

        # Load data from all or specified columns
        series = (
            path_or_df
            if
                isinstance(path_or_df, pd.Series)\
            else
                pd.Series()\
            if
                isinstance(path_or_df, pd.DataFrame)\
            and
                path_or_df.empty\
            else
                self._filter_column(
                    self._sort_values(
                        self._read_table(
                            self._read_json(
                                path_or_df,
                                json_lines=self.json_lines,
                                json_normalize=self.json_normalize,
                            ),
                            compression=self.compression,
                            engine=self.engine,
                            low_memory=self.low_memory,
                            nrows=self.nrows,
                            sep=self.sep if self.column else None,
                            usecols=usecols,
                            ),
                        columns=self.sort
                        ),
                    column=self.column
                )
        )[:self.nrows]

        # Check if type is correct
        if isinstance(series, pd.DataFrame):
            series = series.astype(str).apply(" ".join, axis=1)
            # raise TypeError(f"Expected a Pandas Series or 1-dimensional DataFrame (column='{self.column}').")

        # Apply map and drop duplicates/nulls
        series = series.copy()
        self.index_ = series.index
        if self.applymap:
            series = series.apply(self.applymap)
        if self.drop_duplicates:
            series.drop_duplicates(inplace=True)
        if self.dropna:
            series.dropna(inplace=True)

        # Store difference between indices
        self.skiprows_ = self.index_.difference(series.index)

        return series.copy()

    def _read_table(
        self,
        path_or_df: Union[str, list, pd.Series, pd.DataFrame],
        compression="infer",
        engine=None,
        nrows=None,
        sep=None,
        skiprows=None,
        usecols=None,
        low_memory=True,
    ):
        """ Returns or loads Pandas data frame from file path. """
        return (
            pd.read_table(
                path_or_df,
                compression=compression,
                engine=engine,
                low_memory=low_memory,
                nrows=nrows,
                sep=sep if sep else self._get_file_delimiter(path_or_df) if not compression else None,
                skiprows=skiprows,
                usecols=usecols if usecols else None,
            )
            if
                isinstance(path_or_df, str)
            else
                self.concat(
                    path_or_df,
                    usecols
                )
            if
                isinstance(path_or_df, list)
            else
                path_or_df[usecols]
            if
                usecols
            and
                any(x for x in path_or_df.shape)\
            else
                path_or_df
        )

    def _read_json(self, path_or_df: Union[str, list, pd.Series, pd.DataFrame], json_lines=False, json_normalize=False):
        """ Return Pandas data frame from JSON file. """
        if isinstance(path_or_df, str) and path_or_df.endswith(".json"):
            if json_lines:
                with open(path_or_df, "r") as f:
                    return pd.DataFrame([json.loads(x) for x in f.readlines()])

            if json_normalize:
                return pd.json_normalize(path_or_df)

            return pd.read_json(path_or_df)

        return path_or_df

    def _filter_column(self, df: Union[pd.Series, pd.DataFrame], column=None):
        """ Returns Pandas series from loaded data frame. """
        return (
            df[df.columns[column] if isinstance(column, int) else column]
            if
                column\
            and
                any(x for x in df.shape)\
            else
                df
        )

    def _sort_values(self, df: Union[pd.Series, pd.DataFrame], columns=None):
        """ Returns Pandas series from loaded data frame. """
        return (
            df.sort_values(
                [df.columns[column] if isinstance(column, int) else column for column in columns],
                ascending=False
            )
            if
                columns
            and
                any(x for x in df.shape)\
            else
                df
        )

    def _concat(self, dfs: list, columns=None):
        """ Return a single data frame with concatenated rows. """
        if not isinstance(dfs, list):
            return dfs

        if columns:
            dfs = [df.filter(columns) for df in dfs]

        df = pd.concat(dfs)
        df.index = range(df.shape[0])
        return df

    @staticmethod
    def _get_file_delimiter(path):
        """ Returns character delimiter from file. """
        delimiters = ["|", "\t", ";", ","]
        with open(path, "rt") as f:
            header = f.readline()
        for _ in delimiters:
            if _ in header:
                return _
        return None
