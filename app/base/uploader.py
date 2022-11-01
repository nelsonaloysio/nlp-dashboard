import gzip
import logging as log
from io import BytesIO
from os.path import splitext

import pandas as pd
import streamlit as st
from zipfile import ZipFile

from .ocr import load_image
from .reader import (
    load_csv,
    load_docx,
    load_excel,
    load_json,
    load_ods,
    load_odt,
    load_parquet,
    load_pdf,
    load_txt,
)

EXTENSION_MAP = {
    "gz": "gzip",
    "jpg": "image",
    "jpeg": "image",
    "png": "image",
    "tsv": "csv",
    "xlsx": "xls",
}

EXTENSION_TYPES = {
    "csv": ["text/csv"],
    "docx": [],
    "gzip": [],
    "json": [],
    "ods": [],
    "odt": [],
    "parquet": [],
    "pdf": ["application/pdf"],
    "txt": ["application/octet-stream", "text/plain"],
    "xls": [],
    "zip": ["application/zip"],
}

SUPPORTED_EXTENSIONS = sorted(list(EXTENSION_MAP) + list(EXTENSION_TYPES))


class Uploader():

    def __init__(self):
        """ Initializes class. """

    def uploader(self) -> list:
        with st.form("uploader_form", clear_on_submit=True):
            uploaded_files = st.file_uploader(
                "Please select one or more files to upload below.",
                accept_multiple_files=True,
                # on_change=self._uploader_callback,  # Disabled in forms
            )

            st.caption(
                "Supported file extensions: %s." % ", ".join(
                    f"`.{extension.upper()}`" for extension in SUPPORTED_EXTENSIONS
                )
            )

            c1, c2 = st.columns([1, 15])

            with c1:
                submit = st.form_submit_button(
                    "Upload",
                    type="primary" if "data" not in st.session_state else "secondary",
                )

        with c2:
            st.checkbox(
                "Merge newly uploaded files with existing data.",
                disabled="data" not in st.session_state,
                key="merge_uploaded",
                value=st.session_state.get("merge_uploaded", False)
            )

        if submit:
            if uploaded_files:
                return uploaded_files

    def load_uploaded_files(self, uploaded_files) -> pd.DataFrame:
        data =  pd.concat([
            self.load_uploaded_file(uploaded_file)
            for uploaded_file in uploaded_files
        ])

        if data.shape[1] == 1 and data.columns[0] == 0:
            data.columns = ["text"]

        # Simple way of circumventing Streamlit's default upload size limit.
        # Be warned that your browser might not feel at ease loading large data sets.
        if "data" in st.session_state and st.session_state.get("merge_uploaded"):
            # if data.columns.tolist() != st.session_state.data.columns.tolist():
            #     st.warning("Uploaded data columns do not match existing fields in cache.")
            #     return []
            data = pd.concat([st.session_state.data, data])

        return data\
            .map(lambda x: None if type(x) == str and x.strip() == "" else x)\
            .dropna(axis=0, how="all")\
            .fillna("")

    def load_uploaded_file(self, uploaded_file) -> pd.DataFrame:
        if type(uploaded_file).__name__ == "UploadedFile":
            # Streamlit uploaded file.
            file_name = uploaded_file.name
            file_type = uploaded_file.type
        else:
            # Tuple (file_name: str, content: bytes).
            file_name = uploaded_file[0]
            file_type = None
            uploaded_file = uploaded_file[1]

        log.info(f"Loading uploaded file: '{file_name}'...")
        file_extension = splitext(file_name)[-1].lower().lstrip(".")

        if file_extension == "doc" or file_type == "application/msword":
            self.error("The **`DOC`** file type has been deprecated, please convert it to **`DOCX`** and re-upload.")

        if file_extension in SUPPORTED_EXTENSIONS or file_type in EXTENSION_TYPES.get(file_type, []):
            data = getattr(self, f"load_{EXTENSION_MAP.get(file_extension, file_extension)}")(uploaded_file)

            # Reindex with additional info & natural row order (as in Office-like suites).
            if file_extension in ("gzip", "zip"):
                pass
            elif file_extension == "pdf":
                data.index = [f"{x} ({file_name})" for x in data.index]
            else:
                data.index = [f"Row {i + 2} ({file_name})" for i in range(data.shape[0])]

            return data

        self.warning(f"Unsupported `.{file_extension}` file extension.")
        return pd.DataFrame()

    def load_gzip(self, uploaded_file) -> pd.DataFrame:
        with gzip.open(uploaded_file, "rb") as g:
            return self.load_uploaded_file((g.name, BytesIO(g.read())))

    def load_zip(self, uploaded_file) -> pd.DataFrame:
        with ZipFile(uploaded_file, "r") as z:
            return pd.concat([
                self.load_uploaded_file((z_name, BytesIO(z.read(z_name))))
                for z_name in z.namelist()
            ])

    load_csv = load_csv
    load_docx = load_docx
    load_image = load_image
    load_json = load_json
    load_ods = load_ods
    load_odt = load_odt
    load_parquet = load_parquet
    load_pdf = load_pdf
    load_txt = load_txt
    load_xls = load_excel
    load_xlsx = load_excel
