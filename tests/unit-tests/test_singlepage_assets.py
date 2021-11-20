# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from sphinxcontrib.confluencebuilder.singlebuilder import SingleConfluenceBuilder
from tests.lib import build_sphinx
from tests.lib import parse
from tests.lib import prepare_conf
import os
import unittest


class TestConfluenceSinglepageAssets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        cls.dataset = os.path.join(test_dir, 'datasets', 'shared-asset')

    def test_storage_singlepage_asset_defaults(self):
        """validate single page assets are self-contained (storage)"""
        #
        # Ensure when generating a single page that all assets on a page are
        # pointing (implicitly) to itself (i.e. no `ri:page` entry).

        out_dir = build_sphinx(self.dataset, config=self.config,
            builder=SingleConfluenceBuilder.name)

        with parse('index', out_dir) as data:
            images = data.find_all('ac:image')
            self.assertEqual(len(images), 2)

            for image in images:
                attachment = image.find('ri:attachment')
                self.assertIsNotNone(attachment)
                self.assertTrue(attachment.has_attr('ri:filename'))
                self.assertEqual(attachment['ri:filename'], 'image03.png')

                page_ref = attachment.find('ri:page')
                self.assertIsNone(page_ref)

    def test_storage_singlepage_asset_force_standalone(self):
        """validate single page assets are self-contained alt (storage)"""
        #
        # Ensure when generating a single page that all assets on a page are
        # pointing (implicitly) to itself (i.e. no `ri:page` entry) -- ensure
        # the `confluence_asset_force_standalone` option is not causing issues.

        config = dict(self.config)
        config['confluence_asset_force_standalone'] = True
        out_dir = build_sphinx(self.dataset, config=config,
            builder=SingleConfluenceBuilder.name)

        with parse('index', out_dir) as data:
            images = data.find_all('ac:image')
            self.assertEqual(len(images), 2)

            for image in images:
                attachment = image.find('ri:attachment')
                self.assertIsNotNone(attachment)
                self.assertTrue(attachment.has_attr('ri:filename'))
                self.assertEqual(attachment['ri:filename'], 'image03.png')

                page_ref = attachment.find('ri:page')
                self.assertIsNone(page_ref)
