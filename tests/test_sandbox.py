# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2019-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

import argparse
import os
import sys

from sphinxcontrib.confluencebuilder.exceptions import ConfluenceBadApiError
from sphinxcontrib.confluencebuilder.publisher import ConfluencePublisher
from tests.lib import build_sphinx, enable_sphinx_info, prepare_dirs, prepare_sphinx


def process_sandbox(target_sandbox, builder=None, defines=None):
    test_dir = os.path.dirname(os.path.realpath(__file__))
    base_dir = os.path.join(test_dir, os.pardir)
    sandbox_dir = os.path.join(base_dir, target_sandbox)

    container = "sandbox-test"
    if builder:
        container += "-" + builder

    doc_dir = prepare_dirs(container)
    build_sphinx(
        sandbox_dir, out_dir=doc_dir, builder=builder, extra_config=defines, relax=True
    )


def process_raw_upload(target_sandbox):
    test_dir = os.path.dirname(os.path.realpath(__file__))
    base_dir = os.path.join(test_dir, os.pardir)
    sandbox_dir = os.path.join(base_dir, target_sandbox)
    raw_file = os.path.join(sandbox_dir, "raw.conf")

    if not os.path.exists(raw_file):
        print("[sandbox] missing file", raw_file)
        return

    doc_dir = prepare_dirs("sandbox-raw")
    with prepare_sphinx(sandbox_dir, out_dir=doc_dir, relax=True) as app:
        publisher = ConfluencePublisher()
        publisher.init(app.config)
        publisher.connect()

        while True:
            data = {
                "labels": [],
            }

            with open(raw_file, "r") as f:
                data["content"] = f.read()

            print("[sandbox] publishing page...")
            try:
                publisher.storePage("raw", data)
            except ConfluenceBadApiError as ex:
                print("[sandbox] failed to publish content:", ex)

            print("[sandbox] any key to retry; q to quit")
            if input().lower() == "q":
                break


def main():
    enable_sphinx_info()

    parser = argparse.ArgumentParser(
        prog=__name__, description="Atlassian Confluence Sphinx Extension Sandbox"
    )
    parser.add_argument("-D", action="append", default=[], dest="define")
    parser.add_argument("--builder", "-b")
    parser.add_argument("--raw-upload", "-R", action="store_true")
    parser.add_argument("--sandbox", default="sandbox")
    parser.add_argument("--verbose", "-v", action="store_true")

    args, ___ = parser.parse_known_args(sys.argv[1:])
    parser.parse_args()

    defines = {}
    for val in args.define:
        try:
            key, val = val.split("=", 1)
            defines[key] = val
        except ValueError:
            print("[sandbox] invalid define provided in command line")
            return 1

    print("[sandbox] target sandbox:", args.sandbox)

    if args.verbose:
        if "SPHINX_VERBOSITY" not in os.environ:
            os.environ["SPHINX_VERBOSITY"] = "2"

    if args.raw_upload:
        print("[sandbox] raw-upload test")
        process_raw_upload(args.sandbox)
    else:
        print("[sandbox] documentation test")
        process_sandbox(args.sandbox, args.builder, defines)

    return 0


if __name__ == "__main__":
    sys.exit(main())
