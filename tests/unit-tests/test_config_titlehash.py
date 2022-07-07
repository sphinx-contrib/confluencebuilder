# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020-2022 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
from sphinx.errors import SphinxWarning
import os


class TestConfluenceConfigTitleHash(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestConfluenceConfigTitleHash, cls).setUpClass()

        cls.config['root_doc'] = 'index'
        cls.dataset = os.path.join(cls.datasets, 'titlehash')

    @setup_builder('confluence')
    def test_identical_titles(self):
        config = dict(self.config)
        config['confluence_title_hash_root_path'] = os.path.abspath(self.datasets)

        out_dir = self.build(self.dataset, config=config)
        with parse('index', out_dir) as data:
            page_refs = data.find_all('ri:page')
            assert len(page_refs) == 2
            self.assertEqual(page_refs[0]['ri:content-title'], 'readme -PCgWaWwCGW')
            self.assertEqual(page_refs[1]['ri:content-title'], 'readme -3nk9UaHaqh')

    @setup_builder('confluence')
    def test_hash_root_path_does_not_match(self):
        config = dict(self.config)
        config['confluence_title_hash_root_path'] = 'garbage_path'

        with self.assertRaisesRegex(SphinxWarning, "does not start with defined confluence_title_hash_root_path 'garbage_path'"):
            self.build(self.dataset, config=config)
