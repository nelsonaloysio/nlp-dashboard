import codecs
import gzip
import json
import logging as log
import os
import os.path as osp
from charset_normalizer import detect
from io import BytesIO  # StringIO, TextIOWrapper
from zipfile import ZipFile

import csv
import docx
import odf.opendocument
import odf.teletype
import pandas as pd
import pdfplumber

from ..base.ocr import load_image
from .abc import BaseTransformer

DELIMITERS = ["|", "\t", ",", ";", ":", " "]
ENCODINGS = {"ascii": "utf-8"}

EXTENSION_MAP = {
    "gz": "gzip",
    "jpg": "image",
    "jpeg": "image",
    "png": "image",
    "tsv": "csv",
    "xls": "excel",
    "xlsx": "excel",
}


class Reader(BaseTransformer):
    load_image = load_image

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        """ Reads data frame or file path. """
        log.info("Reading input data.")

        if type(X) in (pd.Series, pd.DataFrame):
            return X

        elif isinstance(X, str):

            if osp.exists(X):

                if osp.isfile(X):
                    file_extension = osp.splitext(X)[-1].lower().lstrip(".")
                    func = getattr(Reader, f"load_{EXTENSION_MAP.get(file_extension, file_extension)}")

                    with open(X, "rb") as f:
                        return func(f, **({"func": self.reader} if file_extension in ("gzip", "zip") else {}))

                if osp.isfolder(X):
                    return self.transform([osp.join(X, x) for x in os.listdir(X)])

            return pd.Series(X.split("\n"))

        elif isinstance(X, (list, tuple)):
            return pd.concat([self.transform(x) for x in X])

        return pd.DataFrame()

    @staticmethod
    def load_csv(file, compression=None) -> pd.DataFrame:
        bio = BytesIO(file.read())
        bio.seek(0)
        encoding = Reader._get_encoding(bio)
        bio.seek(0)
        info = codecs.lookup(encoding)
        srw = codecs.StreamReaderWriter(bio, info.streamreader, info.streamwriter, errors="strict")
        header = srw.readline().strip()
        delimiter = Reader._get_delimiter(header)
        return pd.read_csv(srw, compression=compression, delimiter=delimiter, names=header.split(delimiter))

    @staticmethod
    def load_docx(file) -> pd.DataFrame:
        return pd.Series(
            list(paragraph.text for paragraph in docx.Document(file).paragraphs)
        ).to_frame()

    @staticmethod
    def load_excel(file) -> pd.DataFrame:
        return pd.concat([
            pd.read_excel(file, sheet_name=sheet_name)
            for sheet_name in pd.ExcelFile(file).sheet_names
        ])

    @staticmethod
    def load_gzip(file, func=lambda x: x) -> pd.DataFrame:
        with gzip.open(file, "rb") as g:
            return func((g.name, BytesIO(g.read())))

    @staticmethod
    def load_json(file) -> pd.DataFrame:
        try:
            return pd.read_json(file)
        except:
            return pd.DataFrame.from_records([json.loads(line) for line in open(file, "r").readlines()])

    @staticmethod
    def load_ods(file, engine="odf") -> pd.DataFrame:
        return pd.concat([
            pd.read_excel(file, engine=engine, sheet_name=sheet_name)
            for sheet_name in pd.ExcelFile(file, engine=engine).sheet_names
        ])

    @staticmethod
    def load_odt(file) -> pd.DataFrame:
        return pd.Series([
            odf.teletype.extractText(paragraph)
            for paragraph in odf.opendocument.load(file).getElementsByType(odf.text.P)
        ]).to_frame()

    @staticmethod
    def load_parquet(file) -> pd.DataFrame:
        return pd.read_parquet(file)

    @staticmethod
    def load_pdf(file) -> pd.DataFrame:
        series = [
            pd.Series(
                [page.extract_text().split("\n")],
                index=[page.page_number],
            )\
            .explode()\
            for page in pdfplumber.open(file).pages
        ]

        for i in range(len(series)):
            series[i].index = [f"Page {page}, Row {i + 1}" for i, page in enumerate(series[i].index)]

        return pd.concat(series).to_frame()

    @staticmethod
    def load_txt(file, header=None) -> pd.DataFrame:
        return pd.read_table(file, header=header)

    @staticmethod
    def load_xml(file) -> pd.DataFrame:
        return pd.read_xml(file)

    @staticmethod
    def load_zip(file, func=lambda x: x) -> pd.DataFrame:
        with ZipFile(file, "r") as z:
            return pd.concat([
                func((z_name, BytesIO(z.read(z_name))))
                for z_name in z.namelist()
            ])

    @staticmethod
    def _get_delimiter(header: str, delimiters: list = DELIMITERS) -> str:
        return csv.Sniffer().sniff(header, delimiters=delimiters).delimiter

    """
    @staticmethod
    def _get_delimiter(file, delimiters=DELIMITERS):
        file.seek(0)
        header = file.readline().decode()
        file.seek(0)
        try:
            sep = csv.Sniffer().sniff(header, delimiters=delimiters).delimiter
        except:
            for sep in DELIMITERS:
                if sep in header:
                    break
        return sep
    """

    @staticmethod
    def _get_encoding(file, chunksize=1024) -> str:
        encoding = detect(file.read(chunksize))["encoding"]
        return ENCODINGS.get(encoding, encoding)

    @staticmethod
    def _read_file(path: str) -> BytesIO:
        with open(path, "rb") as f:
            return f # BytesIO(f.read())
