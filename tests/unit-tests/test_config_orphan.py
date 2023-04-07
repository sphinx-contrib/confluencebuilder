# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from sphinxcontrib.confluencebuilder.builder import ConfluenceBuilder
from sphinxcontrib.confluencebuilder.publisher import ConfluencePublisher
from tests.lib.testcase import ConfluenceTestCase
from unittest.mock import ANY
from unittest.mock import call
from unittest.mock import patch
import os


class TestConfluenceConfigOrphan(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'orphan')

        cls.config['confluence_publish'] = True
        cls.config['confluence_server_url'] = 'https://dummy.example.com/'
        cls.config['confluence_space_key'] = 'DUMMY'

    def run(self, result=None):
        with patch.object(ConfluencePublisher, 'connect'), \
                patch.object(ConfluencePublisher, 'disconnect'), \
                patch.object(ConfluenceBuilder, 'publish_asset'):
            super().run(result)

    def test_config_orphan_allow_explicit(self):
        config = dict(self.config)
        config['confluence_publish_orphan'] = True

        with patch.object(ConfluenceBuilder, 'publish_doc') as mm:
            self.build(self.dataset, config=config)

        self.assertEqual(mm.call_count, 3)
        mm.assert_has_calls([
            call('index', ANY),
            call('pagea', ANY),
            call('pageb', ANY),
        ], any_order=True)

    def test_config_orphan_allow_default(self):
        with patch.object(ConfluenceBuilder, 'publish_doc') as mm:
            self.build(self.dataset)

        self.assertEqual(mm.call_count, 3)
        mm.assert_has_calls([
            call('index', ANY),
            call('pagea', ANY),
            call('pageb', ANY),
        ], any_order=True)

    def test_config_orphan_deny_explicit(self):
        config = dict(self.config)
        config['confluence_publish_orphan'] = False

        with patch.object(ConfluenceBuilder, 'publish_doc') as mm:
            self.build(self.dataset, config=config)

        self.assertEqual(mm.call_count, 2)
        mm.assert_has_calls([
            call('index', ANY),
            call('pagea', ANY),
        ], any_order=True)
