import codecs
import json
from charset_normalizer import detect
from io import BytesIO, StringIO, TextIOWrapper

import csv
import docx
import odf.opendocument
import odf.teletype
import pandas as pd
import pdfplumber

DELIMITERS = [
    "|",
    "\t",
    ",",
    ";",
    ":",
    " ",
]

ENCODINGS = {
    "ascii": "utf-8",
}


@staticmethod
def load_csv(uploaded_file, compression=None) -> pd.DataFrame:
    bio = BytesIO(uploaded_file.read())
    bio.seek(0)
    encoding = get_encoding(bio)
    bio.seek(0)
    info = codecs.lookup(encoding)
    srw = codecs.StreamReaderWriter(bio, info.streamreader, info.streamwriter, errors="strict")
    header = srw.readline().strip()
    delimiter = csv.Sniffer().sniff(header).delimiter
    return pd.read_csv(srw, compression=compression, delimiter=delimiter, names=header.split(delimiter))


@staticmethod
def load_docx(uploaded_file) -> pd.DataFrame:
    return pd.Series(
        list(paragraph.text for paragraph in docx.Document(uploaded_file).paragraphs)
    ).to_frame()


@staticmethod
def load_excel(uploaded_file) -> pd.DataFrame:
    return pd.concat([
        pd.read_excel(uploaded_file, sheet_name=sheet_name)
        for sheet_name in pd.ExcelFile(uploaded_file).sheet_names
    ])


@staticmethod
def load_json(uploaded_file) -> pd.DataFrame:
    try:
        return pd.read_json(uploaded_file)
    except:
        return pd.DataFrame.from_records([json.loads(line) for line in open(uploaded_file, "r").readlines()])


@staticmethod
def load_ods(uploaded_file, engine="odf") -> pd.DataFrame:
    return pd.concat([
        pd.read_excel(uploaded_file, engine=engine, sheet_name=sheet_name)
        for sheet_name in pd.ExcelFile(uploaded_file, engine=engine).sheet_names
    ])


@staticmethod
def load_odt(uploaded_file) -> pd.DataFrame:
    return pd.Series([
        odf.teletype.extractText(paragraph)
        for paragraph in odf.opendocument.load(uploaded_file).getElementsByType(odf.text.P)
    ]).to_frame()


@staticmethod
def load_parquet(uploaded_file) -> pd.DataFrame:
    return pd.read_parquet(uploaded_file)


@staticmethod
def load_pdf(uploaded_file) -> pd.DataFrame:
    series = [
        pd.Series(
            [page.extract_text().split("\n")],
            index=[page.page_number],
        )\
        .explode()\
        for page in pdfplumber.open(uploaded_file).pages
    ]

    for i in range(len(series)):
        series[i].index = [f"Page {page}, Row {i + 1}" for i, page in enumerate(series[i].index)]

    return pd.concat(series).to_frame()


"""
@staticmethod
def load_pdf(uploaded_file) -> pd.DataFrame:
    return pd.Series(
        text
        for text in list(page.extract_text() for page in pdfplumber.open(uploaded_file).pages)
        for text in text.split("\n")
    ).to_frame()
"""


@staticmethod
def load_txt(uploaded_file, header=None) -> pd.DataFrame:
    return pd.read_table(uploaded_file, header=header)


@staticmethod
def get_delimiter(uploaded_file):
    uploaded_file.seek(0)
    header = uploaded_file.readline().decode()
    uploaded_file.seek(0)
    try:
        sep = csv.Sniffer().sniff(header, delimiters=DELIMITERS).delimiter
    except:
        for sep in DELIMITERS:
            if sep in header:
                break
    return sep


@staticmethod
def get_encoding(uploaded_file, chunksize=1024):
    encoding = detect(uploaded_file.read(chunksize))["encoding"]
    return ENCODINGS.get(encoding, encoding)
