# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from pathlib import Path
from sphinx.application import Sphinx
from sphinx.locale import __
from sphinx.util.docutils import docutils_namespace
from sphinxcontrib.confluencebuilder.config import process_ask_configs
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger as logger
from sphinxcontrib.confluencebuilder.publisher import ConfluencePublisher
from sphinxcontrib.confluencebuilder.util import temp_dir
import sys
import traceback


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

    work_dir = args.work_dir if args.work_dir else Path.cwd()

    # protection warning
    if not args.danger:
        print()
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
        return 1

    # check configuration and prepare publisher
    dryrun = False
    publisher = None

    try:
        with temp_dir() as tmp_dir, docutils_namespace():
            app = Sphinx(
                str(work_dir),       # document sources
                str(work_dir),       # directory with configuration
                str(tmp_dir),        # output for built documents
                str(tmp_dir),        # output for doctree files
                'confluence',        # builder to execute
                status=sys.stdout,   # sphinx status output
                warning=sys.stderr)  # sphinx warning output

            dryrun = app.config.confluence_publish_dryrun
            server_url = app.config.confluence_server_url
            space_key = app.config.confluence_space_key
            parent_ref = app.config.confluence_parent_page

            # initialize the publisher (if permitted)
            if app.config.confluence_publish:
                process_ask_configs(app.config)

                publisher = ConfluencePublisher()
                publisher.init(app.config)

    except Exception:  # noqa: BLE001
        sys.stdout.flush()
        logger.error(traceback.format_exc())
        if Path(work_dir / 'conf.py').is_file():
            logger.error('unable to load configuration')
        else:
            logger.error('no documentation/missing configuration')
        return 1

    if not publisher:
        logger.error('publishing not configured in sphinx configuration')
        return 1

    if args.parent and not parent_ref:
        logger.error('parent option provided but no parent page is configured')
        return 1

    # reminder warning
    print()
    sys.stdout.flush()
    logger.warn('!!! DANGER DANGER DANGER !!!')
    print("""
A request has been made to attempt to wipe the pages from a configured
Confluence instance. This action is not reversible with this tool and may
require assistance from an administrator from a Confluence instance to recover
pages. Only use this action if you know what you are doing.
        """)
    sys.stdout.flush()

    logger.warn('!!! DANGER DANGER DANGER !!!')
    print()

    if not ask_question('Are you sure you want to continue?'):
        return 0
    print()

    # user has confirmed; start an attempt to wipe
    publisher.connect()

    base_page_id = None
    if args.parent:
        base_page_id = publisher.get_base_page_id()

    # find all legacy pages; always search aggressive to prevent any Confluence
    # caching issues/delays
    legacy_pages = publisher.get_descendants(base_page_id, 'search-aggressive')

    print('         URL:', server_url)
    print('       Space:', space_key)
    if base_page_id:
        logger.note('       Pages: Child pages of ' + parent_ref)
    else:
        logger.note('       Pages: All Pages')
    print(' Total pages:', len(legacy_pages))
    if dryrun:
        print('     Dry run:', 'Enabled (no pages will be removed)')

    if not legacy_pages:
        print()
        print('No pages detected on this space. Exiting...')
        return 0

    if args.verbose:
        print('-------------------------')
        name_cache = publisher._name_cache  # noqa: SLF001
        page_names = [name_cache[p] for p in legacy_pages]
        sorted(page_names)
        print('\n'.join(page_names))
        print('-------------------------')

    print()
    if not ask_question('Are you sure you want to REMOVE these pages?'):
        return 0
    print()

    logger.info('Removing pages...', nonl=True)
    if dryrun:
        logger.info('')
    for page_id in legacy_pages:
        publisher.remove_page(page_id)
        if not dryrun:
            logger.info('.', nonl=True)
    if not dryrun:
        logger.info(__('done'))

    return 0


def ask_question(question, default='no'):
    """
    ask the user a question

    Prompt for asking yes or no for a wipe action.

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
    else:
        prompt = ' [y/N] '

    while True:
        rsp = input(question + prompt).strip().lower()

        if default is not None and rsp == '':
            return default == 'yes'

        if rsp in ('y', 'yes'):
            return True

        if rsp in ('n', 'no', 'q'):  # q for 'quit'
            return False

        print("Please respond with 'y' or 'n'.\n")
