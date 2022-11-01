import logging as log
from io import BytesIO
from zipfile import ZipFile

import json
import networkx as nx
import numpy as np
import pandas as pd
import streamlit as st

from ..base.sidebar import SIDEBAR

INDENT = 2


@classmethod
def display_download(self) -> None:
    self.title("Download results", h=3)
    st.write("Press the button below to compress and download all generated artifacts.")

    e = st.empty()
    disabled = st.session_state.get("artifacts_download", False)
    label = "Artifacts downloaded! 🎉" if disabled else "Compress"

    if e.button(label, key="artifacts_compress", disabled=disabled):
        e.empty()

        # Create in-memory buffer to write and store zipped contents.
        with st.spinner(f"Compressing artifacts..."):
            with BytesIO() as buffer:
                with ZipFile(buffer, "w") as z:
                    for name, content in prepare_download(st.session_state.artifacts).items():
                        z.writestr(name, content)
                buffer.seek(0)

                e.download_button(
                    "Download",
                    data=buffer,
                    key="artifacts_download",
                    file_name="CHL Dashboard Analysis.zip",
                    type="primary",
                )


@staticmethod
def prepare_download(artifacts: dict):
    output = {}

    def get_name(key):
        return SIDEBAR\
            .get(key.replace("_over_time", ""), key.capitalize())\
            .replace(":", " -")\
            .replace("_", " ")\
            + (" over time" if "over_time" in key else "")

    def writer(key, value):
        if type(value) in (list, dict):
            value = pd.Series(value).to_frame()

        value.name = "value"
        value.index.name = "object"

        try:
            output[f"{key}.csv"] = value.to_csv()
            try:
                output[f"{key}.xlsx"] = value.to_excel()
            except:
                log.warn(f"Failed to write artifact '{key}' as Excel, returning JSON and CSV only.")
        except:
            log.warn(f"Failed to write artifact '{key}' as CSV, returning JSON only.")

        output[f"{key}.json"] = value.to_json()

    for key, value in artifacts.items():

        if key == "attention" or key.startswith("embedding"):
            output[f"{key.capitalize()}.json"] = json.dumps(np.array(value).tolist(), indent=INDENT)

        elif key == "network" and value is not None:
            output["Network.graphml"] = "\n".join(nx.generate_graphml(value))

        elif key == "themes":
            if value:
                for theme, dct in value.items():
                    for key_, value_ in dct.items():
                        if value_ is not None and key_ != "index":
                                writer(f"Theme {theme+1}/{get_name(key_)}", value_)

        elif key == "wordcloud":
            # output["Wordcloud.html"] = value
            continue

        elif value is not None:
            writer(get_name(key), value)

    return output
