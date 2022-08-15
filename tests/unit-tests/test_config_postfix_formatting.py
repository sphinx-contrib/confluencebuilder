# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020-2022 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

import os
from sphinxcontrib.confluencebuilder.exceptions import \
    ConfluenceConfigurationError
from sphinxcontrib.confluencebuilder.state import ConfluenceState
from tests.lib.testcase import ConfluenceTestCase
from tests.lib import parse
from tests.lib.testcase import setup_builder
from unittest.mock import patch


class TestCreateDocnameUniqueHash(ConfluenceTestCase):
    def test_no_parent_or_root_page_or_project_configured(self):
        test_docname = 'docs/test_file.rst'
        hash = ConfluenceState._create_docname_unique_hash(
            docname=test_docname, config=self.config)
        self.assertEqual(hash, '75b0047d7552a5e4d91481e992f5ed339d868b3c')

    def test_parent_page_configured(self):
        test_docname = 'docs/test_file.rst'
        config = self.config
        config['confluence_parent_page'] = 'parent_page'
        hash = ConfluenceState._create_docname_unique_hash(
            docname=test_docname, config=self.config)
        self.assertEqual(hash, '9ca6dcc0b0e9eff175f1182ed75a2c43f359ed24')

    def test_publish_root_configured(self):
        test_docname = 'docs/test_file.rst'
        config = self.config
        config['confluence_publish_root'] = 'publish_root'
        hash = ConfluenceState._create_docname_unique_hash(
            docname=test_docname, config=self.config)
        self.assertEqual(hash, '02fe177ef99b746ed60cb1959d6134d3ea54fab9')

    def test_project_configured(self):
        test_docname = 'docs/test_file.rst'
        config = self.config
        config['project'] = 'grand_project'
        hash = ConfluenceState._create_docname_unique_hash(
            docname=test_docname, config=self.config)
        self.assertEqual(hash, '67e8ac11ab088e763c3cf2e577037b510a54ba41')

class TestFormatPostfix(ConfluenceTestCase):
    def setUp(self):
        self.test_hash = 'test_hash_abc_def'
        self.create_docname_unique_hash_patch = patch(
            'sphinxcontrib.confluencebuilder.state.ConfluenceState.'
            '_create_docname_unique_hash',
            return_value=self.test_hash
        )
        self.create_docname_unique_hash_patch.start()

    def tearDown(self):
        self.create_docname_unique_hash_patch.stop()

    def test_placeholders(self):
        test_docname = 'docs/test_file.rst'
        config = self.config
        confluence_publish_prefix = '- ({hash})'
        postfix = ConfluenceState._format_postfix(
            postfix=confluence_publish_prefix, docname=test_docname,
            config=config)
        self.assertEqual(postfix, '- ({hash})'.format(hash=self.test_hash))

    def test_no_placeholders(self):
        test_docname = 'docs/test_file.rst'
        config = self.config
        confluence_publish_prefix = '- Great Postfix'
        postfix = ConfluenceState._format_postfix(
            postfix=confluence_publish_prefix, docname=test_docname, 
            config=config)
        self.assertEqual(postfix, confluence_publish_prefix)

    def test_unknown_placeholder(self):
        test_docname = 'docs/test_file.rst'
        config = self.config
        confluence_publish_prefix = '- ({unknown_placeholder})'
        with self.assertRaises(ConfluenceConfigurationError):
            ConfluenceState._format_postfix(
                postfix=confluence_publish_prefix, docname=test_docname,
                config=config)

    def test_placeholder_with_format_type(self):
        test_docname = 'docs/test_file.rst'
        config = self.config
        confluence_publish_prefix = '- ({hash:.10})'
        postfix = ConfluenceState._format_postfix(
            postfix=confluence_publish_prefix, docname=test_docname,
            config=config)
        self.assertEqual(postfix, '- ({hash})'.format(
            hash=self.test_hash[0:10]))


class TestRegisterTitle(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestRegisterTitle, cls).setUpClass()
        cls.config['root_doc'] = 'index'
        cls.dataset = os.path.join(cls.datasets, 'postfix_formatting')

    @setup_builder('confluence')
    def test_postfix_hash_fixing_name_conflict(self):
        config = dict(self.config)
        config['confluence_publish_postfix'] = ' -{hash:.10}'

        out_dir = self.build(self.dataset, config=config)
        with parse('index', out_dir) as data:
            page_refs = data.find_all('ri:page')
            assert len(page_refs) == 2
            self.assertEqual(
                page_refs[0]['ri:content-title'], 'readme -cef4211633')
            self.assertEqual(
                page_refs[1]['ri:content-title'], 'readme -b222cd6b2a')
