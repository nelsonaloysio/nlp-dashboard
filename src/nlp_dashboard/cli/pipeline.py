#!/usr/bin/env python3

import json
import logging as log
import os
import sys
from argparse import ArgumentParser, Namespace
from inspect import signature
from pathlib import Path
from time import time
from typing import Callable, Optional, Tuple

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent.parent))
from ..pipeline import DataPipeline

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
log.basicConfig(format=LOG_FORMAT, level=log.INFO)


def getargs(args: list = sys.argv[1:]) -> Tuple[Namespace, list]:
    parser = ArgumentParser("Natural Language Processing Dashboard App Pipeline")

    parser.add_argument("inputs",
                        type=str,
                        metavar="INPUT",
                        nargs="+",
                        help="Input file(s) or folder(s).")

    parser.add_argument("--output",
                        metavar="FOLDER",
                        help="Path of folder to save files.")

    parser.add_argument("--seed",
                        type=int,
                        help="Random seed number.")

    parser.add_argument("--no-hf",
                        action="store_false",
                        dest="use_hf",
                        help="Disable HuggingFace pipeline step.")

    parser.add_argument("--no-kmeans",
                        action="store_false",
                        dest="use_kmeans",
                        help="Disable K-Means pipeline step.")

    parser.add_argument("--no-nltk",
                        action="store_false",
                        dest="use_nltk",
                        help="Disable NLTK pipeline step.")

    parser.add_argument("--no-pandas",
                        action="store_false",
                        dest="use_pandas",
                        help="Disable Pandas pipeline step.")

    parser.add_argument("--no-processor",
                        action="store_false",
                        dest="use_processor",
                        help="Disable processor pipeline step.")

    parser.add_argument("--no-reader",
                        action="store_false",
                        dest="use_reader",
                        help="Disable reader pipeline step.")

    parser.add_argument("--no-spacy",
                        action="store_false",
                        dest="use_spacy",
                        help="Disable spaCy pipeline step.")

    parser.add_argument("--no-tokenizer",
                        action="store_false",
                        dest="use_tokenizer",
                        help="Disable tokenizer pipeline step.")

    parser.add_argument("--no-umap",
                        action="store_false",
                        dest="use_umap",
                        help="Disable UMAP pipeline step.")

    parser.add_argument("--use-tsne",
                        action="store_true",
                        dest="use_tsne",
                        help="Enable TSNE pipeline step.")

    parser.add_argument("--steps",
                        action="store",
                        default=None,
                        dest="named_steps",
                        metavar="STEPS",
                        type=lambda x: x.split(","),
                        help="Order of steps in pipeline (comma-separated).")

    return parser.parse_known_args(args)


def gethypers(pipeline: Callable, unwargs: list) -> dict:
    assert len(unwargs) % 2 == 0,\
        "Pipeline hyperparameters must be set in pairs."

    assert all(k.startswith("--") for k in unwargs[::2]),\
        "Pipeline hyperparameters must start with two hyphens, e.g.: '--spacy-model en_core_web_sm'."

    hyperparams = {k.lstrip("-").replace("-", "__", 1).replace("-", "_"): v for k, v in zip(unwargs[::2], unwargs[1::2])}
    steps = [k.split("__", 1)[0] for k in list(hyperparams)]
    unwsteps = [step for step in steps if step not in list(pipeline.named_steps)]

    assert not unwsteps,\
        f"Invalid parameter step(s) {unwsteps}, not found in pipeline steps {list(pipeline.named_steps)}."

    for named_step in list(pipeline.named_steps):
        hypers = [k.split("__", 1)[-1] for k in hyperparams if k.startswith(f"{named_step}__")]
        params = list(signature(pipeline.named_steps[named_step].fit).parameters.keys())[2:]  # X, y

        assert all(hyper in params for hyper in hypers),\
            f"Invalid parameter(s) {hypers} for step '{named_step}', not found in step parameters {params}."

    for k, v in hyperparams.items():
        if v.lower() == "true":
            hyperparams[k] = True

        elif v.lower() == "false":
            hyperparams[k] = False

        elif v.lower() == "none":
            hyperparams[k] = None

        elif v.isdigit():
            hyperparams[k] = int(v)

        else:
            try:
                hyperparams[k] = float(v)
            except:
                pass

    return hyperparams


def load_dates(inputs, column: str) -> pd.Series:
    return DataPipeline(
        use_reader=True,
        use_pandas=True,
    )\
    .fit_transform(
        inputs,
        pandas__column=column,
    )


def write_artifacts_to_disk(results: dict, output: Optional[str] = None) -> None:

    def writer(key, value, output):
        os.makedirs(output, exist_ok=True)

        if type(value) in (list, dict):
            value = pd.Series(value).to_frame()

        value.name = "value"
        value.index.name = "object"
        value.to_csv(f"{output}/{key}.csv")
        value.to_excel(f"{output}/{key}.xlsx")
        value.to_json(f"{output}/{key}.json", indent=2)

    if not output:
        output = f"output/{int(time())}"

    os.makedirs(output, exist_ok=True)

    for key, value in results.items():

        if key in ("attention", "embedding"):
            with open(f"{output}/{key}.json", "w") as j:
                json.dump(np.array(value).tolist(), j, indent=2)

        elif key == "themes":
            if value:
                for theme, dct in value.items():
                    for key_, value_ in dct.items():
                        if value_ is not None and key_ != "index":
                                writer(key_, value_, output=f"{output}/themes/{theme}")

        elif value is not None:
            writer(key, value, output=output)


def main() -> None:
    args, unwargs = getargs()
    args = vars(args)

    inputs = args.pop("inputs")
    output = args.pop("output")

    pipeline = DataPipeline(**args)

    try:
        hyperparams = gethypers(pipeline, unwargs)
    except AssertionError as e:
        print("\nℹ️ Pipeline hyperparameters accepted:\n")
        for i, named_step in enumerate(list(pipeline.named_steps)):
            params = list(signature(pipeline.named_steps[named_step].fit).parameters.keys())[2:]  # X, y
            print(f"Step {i+1}/{len(pipeline.named_steps)} '{named_step}':\n  {params}")
        print()
        raise e

    if "processor" in pipeline.named_steps and hyperparams.get("processor__dates"):
        hyperparams["processor__dates"] = load_dates(inputs, hyperparams["processor__dates"])

    pipeline.set_passthroughs(**hyperparams)
    t0 = time()

    try:
        results = pipeline.fit_transform(inputs, **hyperparams)
    except Exception as e:
        print("❌ Pipeline failed to execute.\n")
        raise e

    print("✅ Pipeline executed successfully!\n⏰ Finished in %.2fs." % (time() - t0))

    if "processor" in pipeline.named_steps:
        write_artifacts_to_disk(results, output=output)


if __name__ == "__main__":
    sys.exit(main())
