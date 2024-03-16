# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from pathlib import Path
from sphinx.util.console import color_terminal
from sphinx.util.console import nocolor  # pylint: disable=no-name-in-module
from sphinxcontrib.confluencebuilder import __version__ as version
from sphinxcontrib.confluencebuilder.cmd.build import build_main
from sphinxcontrib.confluencebuilder.cmd.conntest import conntest_main
from sphinxcontrib.confluencebuilder.cmd.report import report_main
from sphinxcontrib.confluencebuilder.cmd.wipe import wipe_main
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger as logger
import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(
        prog='sphinx-build-confluence',
        add_help=False,
        description='Sphinx extension to output Atlassian Confluence content.',
    )

    parser.add_argument('action', nargs='?')
    parser.add_argument('--color', default='auto',
        action='store_const', const='yes')
    parser.add_argument('--help', '-h', action='store_true')
    parser.add_argument('--no-color', '-N', dest='color',
        action='store_const', const='no')
    parser.add_argument('--verbose', '-V', action='count', default=0)
    parser.add_argument('--version', action='version',
        version='%(prog)s ' + version)
    parser.add_argument('--work-dir', type=Path)

    args, _ = parser.parse_known_args()
    if args.help:
        print(usage())
        sys.exit(0)

    if args.color == 'no' or (args.color == 'auto' and
            'MSYSTEM' not in os.environ and not color_terminal()):
        nocolor()

    # pre-load logging support if sphinx is not loaded (to prevent blank lines)
    logger.initialize(preload=True)

    # invoke a desired command mainline
    if args.action == 'connection-test':
        rv = conntest_main(parser)
    elif args.action == 'report':
        rv = report_main(parser)
    elif args.action == 'wipe':
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
    return '''\
sphinx-build-confluence [action] <options>

(actions)
 <builder>             specify a builder to invoke (defaults to 'confluence')
 connection-test       Performs a connection test to a Confluence instance
 report                generate a report of this system and the configuration
                        to be shared when generating an issue for developers
 wipe                  wipe the contents of a configured Confluence space

(builder arguments)
 -o, --output-dir      alter the output directory for generated documentation
                        (defaults to `_build/confluence`)

(connection-test arguments)
 --no-sanitize         Do not sanitize configuration content

(report arguments)
 -C, --full-config     include all known sphinx configuration entries
 --no-sanitize         do not sanitize report content
 --offline             do not attempt to interact with a configured Confluence
                        instance when generating a report

(wipe arguments)
 --danger              flag that must be set to use this action
 -P, --parent          only remove pages from the configured parent page

(other options)
 --color[=WHEN]        when to colorize output: never, always or auto
 -h, --help            show this help
 -N, --no-color        explicitly disable colorized output
 -V, --verbose         enable verbose messages
 --version             show the version
 --work-dir            working (documentation) directory to use
                        (defaults to working directory)
'''


if __name__ == '__main__':
    sys.exit(main())
