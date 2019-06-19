# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2019 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""
from sphinxcontrib_confluencebuilder_util import ConfluenceTestUtil as _
import os
import sys

def main():
    _.enableVerbose()

    # find sandbox base folder
    test_dir = os.path.dirname(os.path.realpath(__file__))
    sandbox_dir = os.path.join(test_dir, 'sandbox')
    doc_dir, doctree_dir = _.prepareDirectories('sandbox-test')

    _.buildSphinx(sandbox_dir, doc_dir, doctree_dir)
    return 0

if __name__ == '__main__':
    sys.exit(main())
