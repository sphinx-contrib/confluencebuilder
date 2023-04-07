# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os


class TestConfluenceMentions(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'mentions')

    @setup_builder('html')
    def test_html_confluence_mention_role_ignore(self):
        # build attempt should not throw an exception/error
        self.build(self.dataset, relax=True)

    @setup_builder('confluence')
    def test_storage_confluence_mention_role_default_expected(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            links = data.find_all('ac:link')
            self.assertEqual(len(links), 3)

            # ##########################################################
            # Confluence Server (username) mention
            # ##########################################################
            link = links.pop(0)

            user_tag = link.find('ri:user')
            self.assertTrue(user_tag.has_attr('ri:username'))
            self.assertEqual(user_tag['ri:username'], 'myuser')

            self.assertFalse(user_tag.has_attr('ri:account-id'))
            self.assertFalse(user_tag.has_attr('ri:userkey'))

            # ##########################################################
            # Confluence Server (key) mention
            # ##########################################################
            link = links.pop(0)

            user_tag = link.find('ri:user')
            self.assertTrue(user_tag.has_attr('ri:userkey'))
            self.assertEqual(user_tag['ri:userkey'],
                'b9aaf35e80441f415c3a3d3c53695d0e')

            self.assertFalse(user_tag.has_attr('ri:account-id'))
            self.assertFalse(user_tag.has_attr('ri:username'))

            # ##########################################################
            # Confluence Cloud mention
            # ##########################################################
            link = links.pop(0)

            user_tag = link.find('ri:user')
            self.assertTrue(user_tag.has_attr('ri:account-id'))
            self.assertEqual(user_tag['ri:account-id'],
                '3c5369:fa8b5c24-17f8-4340-b73e-50d383307c59')

            self.assertFalse(user_tag.has_attr('ri:userkey'))
            self.assertFalse(user_tag.has_attr('ri:username'))

    @setup_builder('confluence')
    def test_storage_confluence_mention_role_replacing(self):
        replacing_ref = 'myuser'
        expected_id = '546458:bce30352-7ea5-4f93-a473-b64015f4f4f0'

        config = dict(self.config)
        config['confluence_mentions'] = {
            replacing_ref:  expected_id,
        }

        out_dir = self.build(self.dataset,  config=config)

        with parse('index', out_dir) as data:
            links = data.find_all('ac:link')
            self.assertGreaterEqual(len(links), 3)

            # ##########################################################
            # Replaced ID mention
            # ##########################################################
            link = links.pop(0)

            user_tag = link.find('ri:user')
            self.assertTrue(user_tag.has_attr('ri:account-id'))
            self.assertEqual(user_tag['ri:account-id'], expected_id)

            self.assertFalse(user_tag.has_attr('ri:userkey'))
            self.assertFalse(user_tag.has_attr('ri:username'))
