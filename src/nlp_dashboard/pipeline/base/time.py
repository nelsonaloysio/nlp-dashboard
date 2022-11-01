from typing import Union

import pandas as pd


def fill_time_series(
    time_series: Union[pd.Series, pd.DataFrame],
    index: pd.Index,
    x="index",
    y="value",
    c="category",
):
    if type(time_series) == pd.DataFrame:
        cats = time_series[c].unique()
        locs = [time_series[time_series[c] == cat].index for cat in cats]
        dtype = time_series[y].dtype

        d = {
            cat: fill_time_series(
                pd.Series(
                    time_series.loc[loc, y].reset_index(drop=True).values,
                    index=time_series.loc[loc, x].reset_index(drop=True).values,
                ),
                index=index
            )
            for cat, loc in zip(cats, locs)
        }

        df = pd.concat([
            pd.DataFrame(
                {x: d[cat].index, c: cat, y: d[cat].astype(dtype)},
            )
            for cat in cats
        ])\
        .sort_index()\
        .reset_index(drop=True)

        return df

    return pd.Series(
        time_series,
        index=index
    )\
    .fillna(0)\
    .astype(time_series.dtype)\
    .sort_index()
