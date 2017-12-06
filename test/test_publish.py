# -*- coding: utf-8 -*-
"""
    sphinxcontrib.confluencebuilder.test.test_publish
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2017 by the contributors (see AUTHORS file).
    :license: BSD, see LICENSE.txt for details.
"""

from sphinx.application import Sphinx
from sphinxcontrib.confluencebuilder.builder import ConfluenceBuilder
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceConfigurationError
from sphinxcontrib.confluencebuilder.state import ConfluenceState
import os
import sys
import unittest

class TestConfluenceBuilder(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        base_dir = os.path.dirname(os.path.realpath(__file__))
        src_dir = os.path.join(base_dir, 'publish-set')
        build_dir = os.path.join(base_dir, 'build')
        self.out_dir = os.path.join(build_dir, 'publish-out')
        doctree_dir = os.path.join(build_dir, 'publish-doctree')

        self.config = {}
        self.config['extensions'] = ['sphinxcontrib.confluencebuilder']
        self.config['confluence_page_hierarchy'] = True
        self.config['confluence_parent_page'] = 'Documentation'
        self.config['confluence_publish'] = False
        self.config['confluence_remove_title'] = False
        self.config['confluence_space_name'] = 'TEST'
        self.config['master_doc'] = 'toctree'

        self.app = Sphinx(
            src_dir, None, self.out_dir, doctree_dir, 'confluence', self.config)
        self.app.build(force_all=True)

    def test_parent_registration(self):
        root_doc = ConfluenceState.parentDocname('toctree')
        self.assertIsNone(root_doc)

        parent_doc = ConfluenceState.parentDocname('toctree-doc1')
        self.assertEqual(parent_doc, 'toctree')

        parent_doc = ConfluenceState.parentDocname('toctree-doc2')
        self.assertEqual(parent_doc, 'toctree')

        parent_doc = ConfluenceState.parentDocname('toctree-doc3')
        self.assertEqual(parent_doc, 'toctree')

        parent_doc = ConfluenceState.parentDocname('toctree-doc2a')
        self.assertEqual(parent_doc, 'toctree-doc2')

    def test_publish(self):
        builder = ConfluenceBuilder(self.app)
        builder.config.confluence_publish = True
        with self.assertRaises(ConfluenceConfigurationError):
            builder.init(suppress_conf_check=True)

if __name__ == '__main__':
    sys.exit(unittest.main())
