# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020-2022 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

import os

from sphinx.errors import SphinxWarning

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse


class TestConfluenceConfigTitleHash(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestConfluenceConfigTitleHash, cls).setUpClass()

        cls.config['root_doc'] = 'index'
        cls.dataset = os.path.join(cls.datasets, 'titlehash')

    @setup_builder('confluence')
    def test_no_parent_or_root_page_configured(self):
        config = dict(self.config)
        config['confluence_publish_postfix'] = '&unique_hash'

        out_dir = self.build(self.dataset, config=config)
        with parse('index', out_dir) as data:
            page_refs = data.find_all('ri:page')
            assert len(page_refs) == 2
            self.assertEqual(page_refs[0]['ri:content-title'], 'readme -4fca3e8b2a')
            self.assertEqual(page_refs[1]['ri:content-title'], 'readme -3d2e5ea88a')

    @setup_builder('confluence')
    def test_parent_page_configured(self):
        config = dict(self.config)
        config['confluence_publish_postfix'] = '&unique_hash'
        config['confluence_parent_page'] = 'parent page'

        out_dir = self.build(self.dataset, config=config)
        with parse('index', out_dir) as data:
            page_refs = data.find_all('ri:page')
            assert len(page_refs) == 2
            self.assertEqual(page_refs[0]['ri:content-title'], 'readme -5605474e81')
            self.assertEqual(page_refs[1]['ri:content-title'], 'readme -d64d7f0c67')

    @setup_builder('confluence')
    def test_publish_root_configured(self):
        config = dict(self.config)
        config['confluence_publish_postfix'] = '&unique_hash'
        config['confluence_publish_root'] = '3242342342334'

        out_dir = self.build(self.dataset, config=config)
        with parse('index', out_dir) as data:
            page_refs = data.find_all('ri:page')
            assert len(page_refs) == 2
            self.assertEqual(page_refs[0]['ri:content-title'], 'readme -9e1a9212d2')
            self.assertEqual(page_refs[1]['ri:content-title'], 'readme -51b1dbc890')
