import json
from os.path import dirname, isfile, join, realpath
from urllib.request import urlopen

MIN_SIZE = 25
MAX_WORDS = 100

JS_PATH = join(dirname(dirname(realpath(__file__))), "vendor/d3.layout.cloud.js")
JS_URL = "https://raw.githubusercontent.com/jasondavies/d3-cloud/master/build/d3.layout.cloud.js"

HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title></title>
<script src="http://d3js.org/d3.v3.min.js"></script>
</head>
<body>
<script>

// embed Jason Davies' d3-cloud since it's not available in a CDN
%s

var fill = d3.scale.category20();
var words = %s

d3.layout.cloud().size([800, 800])
    .words(words)
    .rotate(function() { return ~~(Math.random() * 2) * 90; })
    .font("Impact")
    .fontSize(function(d) { return d.size; })
    .on("end", draw)
    .start();

function draw(words) {
    d3.select("body").append("svg")
        .attr("width", 1000)
        .attr("height", 1000)
    .append("g")
        .attr("transform", "translate(400,400)")
    .selectAll("text")
        .data(words)
    .enter().append("text")
        .style("font-size", function(d) { return d.size + "px"; })
        .style("font-family", "Impact")
        .style("fill", function(d, i) { return fill(i); })
        .attr("text-anchor", "middle")
        .attr("transform", function(d) {
        return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
        })
        .text(function(d) { return d.text; });
}
</script>
</body>
</html>
"""


class Wordcloud():

    def __init__(self):
        """ Initializes class. """

    @staticmethod
    def wordcloud(series, max_words=MAX_WORDS):
        return HTML % (load_js(), json.dumps(word_dictionary(series, max_words=max_words), indent=2))


def load_js() -> str:
    if isfile(JS_PATH):
        with open(JS_PATH, "r") as f:
            return f.read()
    else:
        return urlopen(JS_URL).read().decode('utf8')


def word_dictionary(series, max_words=MAX_WORDS) -> dict:
    series = series[:max_words]
    ratio  = 100.0 / (series.max() - series.min() + 1)
    return list(
        {"text": text, "size": size}
        for text, size in
            series.apply(lambda x: MIN_SIZE + int(x * ratio)).items()
    )
