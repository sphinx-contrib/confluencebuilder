# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2019-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib import assertExpectedWithOutput
from tests.lib import prepareConfiguration
from tests.lib import prepareDirectories
from tests.lib import prepareSphinx
import os
import unittest

class TestConfluenceHeaderFooter(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        test_dir = os.path.dirname(os.path.realpath(__file__))

        self.config = prepareConfiguration()
        self.dataset = os.path.join(test_dir, 'dataset-header-footer')
        self.expected = os.path.join(test_dir, 'expected')
        self.template_dir = os.path.join(test_dir, 'templates')

    def test_legacy_headerfooter_absolute(self):
        config = dict(self.config)
        footer_tpl = os.path.join(self.template_dir, 'sample-footer.tpl')
        header_tpl = os.path.join(self.template_dir, 'sample-header.tpl')
        config['confluence_footer_file'] = footer_tpl
        config['confluence_header_file'] = header_tpl

        doc_dir, doctree_dir = prepareDirectories()

        with prepareSphinx(self.dataset, doc_dir, doctree_dir, config) as app:
            app.build(force_all=True)
            assertExpectedWithOutput(self, 'header-footer', self.expected,
                doc_dir, tpn='header-footer')

    def test_legacy_headerfooter_relative(self):
        config = dict(self.config)
        config['confluence_footer_file'] = '../templates/sample-footer.tpl'
        config['confluence_header_file'] = '../templates/sample-header.tpl'

        doc_dir, doctree_dir = prepareDirectories()
        with prepareSphinx(self.dataset, doc_dir, doctree_dir, config) as app:
            app.build(force_all=True)
            assertExpectedWithOutput(self, 'header-footer', self.expected,
                doc_dir, tpn='header-footer')
