# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2017-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from sphinxcontrib.confluencebuilder import __version__ as version
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(prog=__name__,
        description='Sphinx extension to output Atlassian Confluence content.')
    parser.add_argument(
        '--version', action='version', version='%(prog)s ' + version)

    parser.parse_args()
    parser.print_help()
    return 0

if __name__ == '__main__':
    sys.exit(main())
