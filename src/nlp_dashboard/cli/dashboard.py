#!/usr/bin/env python3

import logging as log
import os.path as osp
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from subprocess import call
from typing import Tuple

log.root.handlers = []
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVELS = ["info", "debug", "warning", "error", "critical"]

PATH = osp.abspath(osp.join(str(Path(__file__).parent.parent), "dashboard/run.py"))


def getargs(args: list = sys.argv[1:]) -> Tuple[Namespace, list]:
    parser = ArgumentParser("Culture Hack Labs Dashboard Application")

    parser.add_argument("--log",
                        action="store",
                        dest="log_file",
                        metavar="FILE",
                        help="File to store output log.")

    parser.add_argument("--log-level",
                        action="store",
                        choices=LOG_LEVELS,
                        default=LOG_LEVELS[0],
                        metavar="LEVEL",
                        help=f"Log level. Default: '{LOG_LEVELS[0]}'. Available: {LOG_LEVELS}.")

    parser.add_argument("--no-log",
                        action="store",
                        dest="log",
                        help="Disable output logging.")

    return parser.parse_known_args(args)


def main() -> None:
    args, unwargs = getargs()

    if args.log_level:
        log.basicConfig(encoding="utf-8", format=LOG_FORMAT, level=getattr(log, args.log_level.upper()))
        if args.log_file:
            log.root.handlers.append(log.FileHandler(args.log_file))

    log.info("Starting Streamlit app...")
    call(["streamlit", "run", PATH, *unwargs])


if __name__ == "__main__":
    sys.exit(main())
