# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from pathlib import Path
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceBadApiError
from sphinxcontrib.confluencebuilder.publisher import ConfluencePublisher
from tests.lib import build_sphinx
from tests.lib import enable_sphinx_info
from tests.lib import prepare_dirs
from tests.lib import prepare_sphinx
import argparse
import os
import sys


def process_sandbox(target_sandbox, builder=None, defines=None):
    test_dir = Path(__file__).parent.resolve()
    sandbox_dir = test_dir.parent / target_sandbox

    container = 'sandbox-test'
    if builder:
        container += '-' + builder

    doc_dir = prepare_dirs(container)
    build_sphinx(sandbox_dir, out_dir=doc_dir, builder=builder,
        extra_config=defines, relax=True)


def process_raw_upload(target_sandbox):
    test_dir = Path(__file__).parent.resolve()
    sandbox_dir = test_dir.parent / target_sandbox
    raw_file = sandbox_dir / 'raw.conf'

    if not raw_file.is_file():
        print('[sandbox] missing file', raw_file)
        return

    doc_dir = prepare_dirs('sandbox-raw')
    with prepare_sphinx(sandbox_dir, out_dir=doc_dir, relax=True) as app:
        publisher = ConfluencePublisher()
        publisher.init(app.config)
        publisher.connect()

        while True:
            data = {
                'labels': [],
            }

            with raw_file.open(encoding='utf-8') as f:
                data['content'] = f.read()

            print('[sandbox] publishing page...')
            try:
                publisher.store_page('raw', data)
            except ConfluenceBadApiError as ex:
                print('[sandbox] failed to publish content:', ex)

            print('[sandbox] any key to retry; q to quit')
            try:
                if input().lower() == 'q':
                    break
            except EOFError:
                break


def main():
    enable_sphinx_info()

    parser = argparse.ArgumentParser(prog=__name__,
        description='Atlassian Confluence Sphinx Extension Sandbox')
    parser.add_argument('-D', action='append', default=[], dest='define')
    parser.add_argument('--builder', '-b')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--raw-upload', '-R', action='store_true')
    parser.add_argument('--sandbox', default='sandbox')
    parser.add_argument('--verbose', '-v', action='store_true')

    args, ___ = parser.parse_known_args(sys.argv[1:])
    parser.parse_args()

    defines = {}
    try:
        for define in args.define:
            key, val = define.split('=', 1)
            defines[key] = val
    except ValueError:
        print('[sandbox] invalid define provided in command line')
        return 1

    print('[sandbox] target sandbox:', args.sandbox)

    if args.debug or args.verbose:
        if 'SPHINX_VERBOSITY' not in os.environ:
            os.environ['SPHINX_VERBOSITY'] = '2'

    if args.raw_upload:
        print('[sandbox] raw-upload test')
        process_raw_upload(args.sandbox)
    else:
        print('[sandbox] documentation test')
        process_sandbox(args.sandbox, args.builder, defines)

    return 0


if __name__ == '__main__':
    sys.exit(main())
