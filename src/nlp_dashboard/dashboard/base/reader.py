import logging as log
from os.path import splitext

import pandas as pd

from ...pipeline.transformer.reader import Reader, EXTENSION_MAP

EXTENSION_TYPES = {
    "csv": ["text/csv"],
    "docx": [],
    "excel": [],
    "gzip": [],
    "json": [],
    "ods": [],
    "odt": [],
    "parquet": [],
    "pdf": ["application/pdf"],
    "txt": ["application/octet-stream", "text/plain"],
    "xml": [],
    "zip": ["application/zip"],
}

SUPPORTED_EXTENSIONS = sorted(
    list(EXTENSION_MAP) + list(EXTENSION_TYPES)
)


@classmethod
def reader(self, uploaded_file) -> pd.DataFrame:
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
        func = getattr(Reader, f"load_{EXTENSION_MAP.get(file_extension, file_extension)}")
        data = func(uploaded_file, **({"func": self.reader} if file_extension in ("gzip", "zip") else {}))

        # Reindex with additional information using
        # natural row order (as in Office-like suites).
        if file_extension in ("gzip", "zip"):
            pass
        elif file_extension == "pdf":
            data.index = [f"{x} ({file_name})" for x in data.index]
        else:
            data.index = [f"Row {i + 2} ({file_name})" for i in range(data.shape[0])]

        return data

    self.warning(f"Unsupported `.{file_extension}` file extension.")
    return pd.DataFrame()
