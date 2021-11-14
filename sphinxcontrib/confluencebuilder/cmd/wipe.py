# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020-2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from __future__ import print_function
from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace
from sphinxcontrib.confluencebuilder.compat import input
from sphinxcontrib.confluencebuilder.config import process_ask_configs
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger as logger
from sphinxcontrib.confluencebuilder.publisher import ConfluencePublisher
from sphinxcontrib.confluencebuilder.util import temp_dir
import os
import sys


def wipe_main(args_parser):
    """
    wipe mainline

    The mainline for the 'wipe' action.

    Args:
        args_parser: the argument parser to use for argument processing

    Returns:
        the exit code
    """

    args_parser.add_argument('--danger', action='store_true')
    args_parser.add_argument('--parent', '-P', action='store_true')

    known_args = sys.argv[1:]
    args, unknown_args = args_parser.parse_known_args(known_args)
    if unknown_args:
        logger.warn('unknown arguments: {}'.format(' '.join(unknown_args)))

    work_dir = args.work_dir if args.work_dir else os.getcwd()

    # protection warning
    if not args.danger:
        print('')
        sys.stdout.flush()
        logger.warn('!!! DANGER DANGER DANGER !!!')
        print("""
A request has been made to attempt to wipe the pages from a configured
Confluence instance. This is a helper utility call to assist a user in cleaning
out a space since removing a bulk set of data may not be trivial for a user.

Note that this action is not reversible with this tool and may require
assistance from an administrator from a Confluence instance to recover pages.
Only use this action if you know what you are doing.

To use this action, the argument '--danger' must be set.
            """)
        sys.stdout.flush()
        logger.warn('!!! DANGER DANGER DANGER !!!')
        print('')
        return 1

    # check configuration and prepare publisher
    dryrun = False
    publisher = None
    with temp_dir() as tmp_dir:
        with docutils_namespace():
            app = Sphinx(
                work_dir,           # document sources
                work_dir,           # directory with configuration
                tmp_dir,            # output for built documents
                tmp_dir,            # output for doctree files
                'confluence',       # builder to execute
                status=sys.stdout,  # sphinx status output
                warning=sys.stderr) # sphinx warning output

            aggressive_search = app.config.confluence_adv_aggressive_search
            dryrun = app.config.confluence_publish_dryrun
            server_url = app.config.confluence_server_url
            space_key = app.config.confluence_space_key
            parent_name = app.config.confluence_parent_page

            # initialize the publisher (if permitted)
            if app.config.confluence_publish:
                process_ask_configs(app.config)

                publisher = ConfluencePublisher()
                publisher.init(app.config)

    if not publisher:
        print('(error) publishing not configured in sphinx configuration')
        return 1

    if args.parent and not parent_name:
        print('(error) parent option provided but no parent page is configured')
        return 1

    # reminder warning
    print('')
    sys.stdout.flush()
    logger.warn('!!! DANGER DANGER DANGER !!!')
    print("""
A request has been made to attempt to wipe the pages from a configured
Confluence instance.  This action is not reversible with this tool and may
require assistance from an administrator from a Confluence instance to recover
pages. Only use this action if you know what you are doing.
        """)
    sys.stdout.flush()

    logger.warn('!!! DANGER DANGER DANGER !!!')
    print('')

    if not ask_question('Are you sure you want to continue?'):
        return 0
    print('')

    # user has confirmed; start an attempt to wipe
    publisher.connect()

    base_page_id = None
    if args.parent:
        base_page_id = publisher.getBasePageId()

    if aggressive_search:
        legacy_pages = publisher.getDescendantsCompat(base_page_id)
    else:
        legacy_pages = publisher.getDescendants(base_page_id)

    print('         URL:', server_url)
    print('       Space:', space_key)
    if base_page_id:
        logger.note('       Pages: Child pages of ' + parent_name)
    else:
        logger.note('       Pages: All Pages')
    print(' Total pages:', len(legacy_pages))
    if dryrun:
        print('     Dry run:', 'Enabled (no pages will be removed)')

    if not legacy_pages:
        print('')
        print('No pages detected on this space. Exiting...')
        return 0

    if args.verbose:
        print('-------------------------')
        page_names = []
        for p in legacy_pages:
            page_names.append(publisher._name_cache[p])
        sorted(page_names)
        print('\n'.join(page_names))
        print('-------------------------')

    print('')
    if not ask_question('Are you sure you want to REMOVE these pages?'):
        return 0
    print('')

    logger.info('Removing pages...', nonl=True)
    if dryrun:
        logger.info('')
    for page_id in legacy_pages:
        publisher.removePage(page_id)
        if not dryrun:
            logger.info('.', nonl=True)
    if not dryrun:
        logger.info(' done\n')

    return 0


def ask_question(question, default='no'):
    """
    ask the user a question

    The mainline for the 'wipe' action.

    Args:
        question: the question
        default (optional): the default state

    Returns:
        the users response to the question
    """

    if default is None:
        prompt = ' [y/n] '
    elif default == 'yes':
        prompt = ' [Y/n] '
    elif default:
        prompt = ' [y/N] '

    while True:
        rsp = input(question + prompt).strip().lower()
        if default is not None and rsp == '':
            return default == 'yes'
        elif rsp in ('y', 'yes'):
            return True
        elif rsp in ('n', 'no', 'q'): # q for 'quit'
            return False
        else:
            print("Please respond with 'y' or 'n'.\n")
