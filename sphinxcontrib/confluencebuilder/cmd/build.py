# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger as logger
import os
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
    args_parser.add_argument('--output-dir', '-o')

    known_args = sys.argv[1:]
    args, unknown_args = args_parser.parse_known_args(known_args)
    if unknown_args:
        logger.warn('unknown arguments: {}'.format(' '.join(unknown_args)))

    defines = {}
    for val in args.define:
        try:
            key, val = val.split('=', 1)
            defines[key] = val
        except ValueError:
            logger.error('invalid define provided in command line')
            return 1

    work_dir = args.work_dir if args.work_dir else os.getcwd()
    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = os.path.join(work_dir, '_build', 'confluence')
    doctrees_dir = os.path.join(output_dir, '.doctrees')
    builder = args.action if args.action else DEFAULT_BUILDER

    verbosity = 0
    if args.verbose:
        try:
            verbosity = int(args.verbose)
        except ValueError:
            pass

    # run sphinx engine
    with docutils_namespace():
        app = Sphinx(
            work_dir,               # document sources
            work_dir,               # directory with configuration
            output_dir,             # output for generated documents
            doctrees_dir,           # output for doctree files
            builder,                # builder to execute
            confoverrides=defines,  # configuration overload
            freshenv=True,          # fresh environment
            verbosity=verbosity)    # verbosity
        app.build(force_all=True)

    return 0
