#!/usr/bin/env python3

import logging as log
from typing import Literal, Optional
from urllib.error import URLError

from app import App
from nlp import NLP

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVELS = Literal["critical", "error", "warning", "info", "debug", "notset"]


def main(log_format: Optional[str] = LOG_FORMAT, log_level: Optional[LOG_LEVELS] = "info"):
    if log_level is not None:
        log.basicConfig(format=log_format, level=getattr(log, log_level.upper()))

    app = App(NLP().fit_transform)

    try:
        app()

    except URLError as e:
        app.error(
            """
            **This application requires internet access.**
            Connection error: %s
            """
            % e.reason
        )


if __name__ == "__main__":
    main()
