import json
import os.path as osp
from urllib.request import urlopen

import pandas as pd

MIN_SIZE = 25
MAX_WORDS = 100

PATH = osp.dirname(osp.realpath(__file__))
D3_JS = osp.abspath(osp.join(PATH, "../../vendor/d3.v3.min.js"))
LAYOUT_JS = osp.abspath(osp.join(PATH, "../../vendor/d3.layout.cloud.js"))
LAYOUT_HTML = osp.abspath(osp.join(PATH, "../../vendor/wordcloud.html"))

D3_JS_URL = "https://d3js.org/d3.v3.min.js"
LAYOUT_JS_URL = "https://raw.githubusercontent.com/jasondavies/d3-cloud/master/build/d3.layout.cloud.js"


def wordcloud(series: pd.Series, max_words: int = MAX_WORDS) -> list:
    series = series[:max_words]
    ratio  = 100.0 / (series.max() - series.min() + 1)

    return list(
        {"text": text, "size": size}
        for text, size in
            series.apply(lambda x: MIN_SIZE + int(x * ratio)).items()
    )


def wordcloud_html(wordcloud: list) -> str:
    with open(LAYOUT_HTML, "r") as f:
        return f.read()\
            .replace("{D3_JS}", load_js(D3_JS, D3_JS_URL))\
            .replace("{LAYOUT_JS}", load_js(LAYOUT_JS, LAYOUT_JS_URL))\
            .replace("{WORDS}", json.dumps(wordcloud))


def load_js(path: str, url: str) -> str:
    if osp.isfile(path):
        with open(path, "r") as f:
            return f.read()
    else:
        content = urlopen(url).read().decode('utf8')
        with open(path, "w") as f:
            f.write(content)
        return content
