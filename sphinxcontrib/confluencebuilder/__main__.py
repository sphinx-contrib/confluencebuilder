# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2017-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

import argparse
import sys

from sphinx.util.console import nocolor  # pylint: disable=no-name-in-module
from sphinx.util.console import color_terminal

from sphinxcontrib.confluencebuilder import __version__ as version
from sphinxcontrib.confluencebuilder.cmd.build import build_main
from sphinxcontrib.confluencebuilder.cmd.report import report_main
from sphinxcontrib.confluencebuilder.cmd.wipe import wipe_main
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger as logger


def main():
    parser = argparse.ArgumentParser(
        prog="sphinx-build-confluence",
        add_help=False,
        description="Sphinx extension to output Atlassian Confluence content.",
    )

    parser.add_argument("action", nargs="?")
    parser.add_argument("--help", "-h", action="store_true")
    parser.add_argument("--no-color", "-N", dest="color")
    parser.add_argument("--verbose", "-V", action="count", default=0)
    parser.add_argument("--version", action="version", version="%(prog)s " + version)
    parser.add_argument("--work-dir")

    args, _ = parser.parse_known_args()
    if args.help:
        print(usage())
        sys.exit(0)

    logger.initialize(preload=True)
    if args.color == "no" or (args.color == "auto" and not color_terminal()):
        nocolor()
    # disable color (on windows) by default when using virtualenv since it
    # appears to be causing issues
    elif getattr(sys, "base_prefix", sys.prefix) != sys.prefix:
        if sys.platform == "win32":
            nocolor()

    # invoke a desired command mainline
    if args.action == "report":
        rv = report_main(parser)
    elif args.action == "wipe":
        rv = wipe_main(parser)
    else:
        rv = build_main(parser)

    return rv


def usage():
    """
    display the usage for this tool

    Returns a command line usage string for all options available by the
    sphinx-build-confluence extension.

    Returns:
        the usage string
    """
    return """sphinx-build-confluence [action] <options>

(actions)
 <builder>             specify a builder to invoke (defaults to 'confluence')
 report                generate a report of this system and the configuration
                        to be shared when generating an issue for developers
 wipe                  wipe the contents of a configured Confluence space

(builder arguments)
 -o, --output-dir      alter the output directory for generated documentation
                        (defaults to `_build/confluence`)

(report arguments)
 -C, --full-config     include all known sphinx configuration entries
 --no-sanitize         do not sanitize report content
 --offline             do not attempt to interact with a configured Confluence
                        instance when generating a report

(wipe arguments)
 --danger              flag that must be set to use this action

(other options)
 -h, --help            show this help
 --no-color            explicitly disable colorized output
 -V, --verbose         enable verbose messages
 --version             show the version
 --work-dir            working (documentation) directory to use
                        (defaults to working directory)
"""


if __name__ == "__main__":
    sys.exit(main())
