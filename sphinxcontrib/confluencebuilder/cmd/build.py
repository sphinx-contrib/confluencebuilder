# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from contextlib import suppress
from pathlib import Path
from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger as logger
import sys

#: default builder to invoke when one is not specified
DEFAULT_BUILDER = 'confluence'


def build_main(args_parser):
    """
    build mainline

    The mainline for the 'build' action.

    Args:
        args_parser: the argument parser to use for argument processing

    Returns:
        the exit code
    """

    args_parser.add_argument('-D', action='append', default=[], dest='define')
    args_parser.add_argument('--output-dir', '-o', type=Path)

    known_args = sys.argv[1:]
    args, unknown_args = args_parser.parse_known_args(known_args)
    if unknown_args:
        logger.warn('unknown arguments: {}'.format(' '.join(unknown_args)))

    defines = {}
    try:
        for define in args.define:
            key, val = define.split('=', 1)
            defines[key] = val
    except ValueError:
        logger.error('invalid define provided in command line')
        return 1

    work_dir = args.work_dir if args.work_dir else Path.cwd()
    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = work_dir / '_build' / 'confluence'
    doctrees_dir = output_dir / '.doctrees'
    builder = args.action if args.action else DEFAULT_BUILDER

    verbosity = 0
    if args.verbose:
        with suppress(ValueError):
            verbosity = int(args.verbose)

    # run sphinx engine
    with docutils_namespace():
        app = Sphinx(
            work_dir,               # document sources
            work_dir,               # directory with configuration
            output_dir,             # output for generated documents
            doctrees_dir,           # output for doctree files
            builder,                # builder to execute
            confoverrides=defines,  # configuration overload
            status=sys.stdout,      # sphinx status output
            warning=sys.stderr,     # sphinx warning output
            freshenv=True,          # fresh environment
            verbosity=verbosity)    # verbosity
        app.build(force_all=True)

    return 0
