# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from pathlib import Path
from tests.lib import build_sphinx
from tests.lib import enable_sphinx_info
from tests.lib import prepare_dirs
import argparse
import ast
import os
import sys


def main():
    enable_sphinx_info()

    parser = argparse.ArgumentParser(prog=__name__,
        description='Atlassian Confluence Sphinx Extension Sample')
    parser.add_argument('-D', action='append', default=[], dest='define')
    parser.add_argument('--builder', '-b')
    parser.add_argument('--debug', action='store_true')
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

    if args.debug or args.verbose:
        if 'SPHINX_VERBOSITY' not in os.environ:
            os.environ['SPHINX_VERBOSITY'] = '2'

    if 'TOX_INI_DIR' not in os.environ:
        print('[sample] (error) missing tox ini environment variable')
        return 1

    sample_base = Path(os.environ['TOX_INI_DIR'])
    sample_set_dir = sample_base.parent
    sample_name = sample_base.name
    container = 'sample-' + sample_name
    if args.builder:
        container += '-' + args.builder

    # check if there is a sub-folder the documentation will be found under
    if 'SAMPLE_DIR' in os.environ:
        sample_dir = sample_base / os.environ['SAMPLE_DIR']
    else:
        sample_dir = sample_base

    doc_dir = prepare_dirs(container)

    # extract any shared configuration values and inject them into the
    # define list
    shared_config = sample_set_dir / 'config.py'
    if shared_config.is_file():
        with shared_config.open(encoding='utf-8') as f:
            data = f.read()

        ast_data = ast.parse(data, filename=shared_config)
        for ast_body in ast_data.body:
            if isinstance(ast_body, ast.Assign):
                ast_value = ast.literal_eval(ast_body.value)
                for ast_target in ast_body.targets:
                    defines[ast_target.id] = ast_value

    # configuration overrides for all samples
    defines['exclude_patterns'] = [
        # exclude a specific sample's tox working directory
        '.tox',
    ]

    # process sample project
    print()
    print('[sample] processing sample:', sample_name)
    print(' (sample)', sample_dir)
    print(' (output)', doc_dir)

    build_sphinx(sample_dir, out_dir=doc_dir, builder=args.builder,
        extra_config=defines, relax=True)

    print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
