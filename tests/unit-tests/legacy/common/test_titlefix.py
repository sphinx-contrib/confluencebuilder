# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2017-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib import buildSphinx
from tests.lib import parse
from tests.lib import prepareConfiguration
from tests.lib import prepareDirectories
import os
import unittest

class TestConfluenceTitlefix(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepareConfiguration()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset = os.path.join(test_dir, 'dataset-titlefix')

    def test_legacy_titlefix_none(self):
        doc_dir = prepareDirectories()
        buildSphinx(self.dataset, doc_dir, self.config)

        with parse('index', doc_dir) as data:
            page_ref = data.find('ri:page')
            self.assertIsNotNone(page_ref,
                'unable to find child page reference (ri:page)')
            self.assertEqual(page_ref['ri:content-title'], 'child',
                'default child page title does not match')

        with parse('child', doc_dir) as data:
            page_ref = data.find('ri:page')
            self.assertIsNotNone(page_ref,
                'unable to find index page reference (ri:page)')
            self.assertEqual(page_ref['ri:content-title'], 'index',
                'default index page title does not match')

    def test_legacy_titlefix_postfix(self):
        config = dict(self.config)
        config['confluence_publish_postfix'] = '-mypostfix'

        doc_dir = prepareDirectories()
        buildSphinx(self.dataset, doc_dir, config)

        with parse('index', doc_dir) as data:
            page_ref = data.find('ri:page')
            self.assertIsNotNone(page_ref,
                'unable to find child page reference (ri:page)')
            self.assertEqual(page_ref['ri:content-title'], 'child-mypostfix',
                'child page title did not apply postfix')

        with parse('child', doc_dir) as data:
            page_ref = data.find('ri:page')
            self.assertIsNotNone(page_ref,
                'unable to find index page reference (ri:page)')
            self.assertEqual(page_ref['ri:content-title'], 'index-mypostfix',
                'index page title did not apply postfix')

    def test_legacy_titlefix_prefix(self):
        config = dict(self.config)
        config['confluence_publish_prefix'] = 'myprefix-'

        doc_dir = prepareDirectories()
        buildSphinx(self.dataset, doc_dir, config)

        with parse('index', doc_dir) as data:
            page_ref = data.find('ri:page')
            self.assertIsNotNone(page_ref,
                'unable to find child page reference (ri:page)')
            self.assertEqual(page_ref['ri:content-title'], 'myprefix-child',
                'child page title did not apply prefix')

        with parse('child', doc_dir) as data:
            page_ref = data.find('ri:page')
            self.assertIsNotNone(page_ref,
                'unable to find index page reference (ri:page)')
            self.assertEqual(page_ref['ri:content-title'], 'myprefix-index',
                'index page title did not apply prefix')

    def test_legacy_titlefix_prefix_and_postfix(self):
        config = dict(self.config)
        config['confluence_publish_prefix'] = 'myprefix-'
        config['confluence_publish_postfix'] = '-mypostfix'

        doc_dir = prepareDirectories()
        buildSphinx(self.dataset, doc_dir, config)

        with parse('index', doc_dir) as data:
            page_ref = data.find('ri:page')
            self.assertIsNotNone(page_ref,
                'unable to find child page reference (ri:page)')
            self.assertEqual(page_ref['ri:content-title'],
                'myprefix-child-mypostfix',
                'child page title did not apply prefix and postfix')

        with parse('child', doc_dir) as data:
            page_ref = data.find('ri:page')
            self.assertIsNotNone(page_ref,
                'unable to find index page reference (ri:page)')
            self.assertEqual(page_ref['ri:content-title'],
                'myprefix-index-mypostfix',
                'index page title did not apply prefix and postfix')

    def test_legacy_titlefix_ignore_root(self):
        config = dict(self.config)
        config['confluence_ignore_titlefix_on_index'] = True
        config['confluence_publish_postfix'] = '-mypostfix'
        config['confluence_publish_prefix'] = 'myprefix-'

        doc_dir = prepareDirectories()
        buildSphinx(self.dataset, doc_dir, config)

        with parse('index', doc_dir) as data:
            page_ref = data.find('ri:page')
            self.assertIsNotNone(page_ref,
                'unable to find child page reference (ri:page)')
            self.assertEqual(page_ref['ri:content-title'],
                'myprefix-child-mypostfix',
                'child page title did not apply prefix and postfix')

        with parse('child', doc_dir) as data:
            page_ref = data.find('ri:page')
            self.assertIsNotNone(page_ref,
                'unable to find index page reference (ri:page)')
            self.assertEqual(page_ref['ri:content-title'], 'index',
                'index page title should not have applied a prefix/postfix')
