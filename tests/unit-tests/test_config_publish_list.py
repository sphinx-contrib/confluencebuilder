# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from sphinxcontrib.confluencebuilder.builder import ConfluenceBuilder
from sphinxcontrib.confluencebuilder.publisher import ConfluencePublisher
from tests.lib.testcase import ConfluenceTestCase
from unittest.mock import ANY
from unittest.mock import call
from unittest.mock import patch


class TestConfluenceConfigPublishList(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = cls.datasets / 'publish-list'

        cls.config['confluence_publish'] = True
        cls.config['confluence_server_url'] = 'https://dummy.example.com/'
        cls.config['confluence_space_key'] = 'DUMMY'

    def run(self, result=None):
        with patch.object(ConfluencePublisher, 'connect'), \
                patch.object(ConfluencePublisher, 'disconnect'), \
                patch.object(ConfluenceBuilder, 'publish_asset'):
            super().run(result)

    def test_config_publishlist_allow_empty(self):
        config = dict(self.config)
        config['confluence_publish_allowlist'] = []

        with patch.object(ConfluenceBuilder, 'publish_doc') as mm:
            self.build(self.dataset, config=config)

        mm.assert_not_called()

    def test_config_publishlist_allow_list_cli_default(self):
        config = dict(self.config)
        config['confluence_publish_allowlist'] = 'page-a,folder/page-b'

        with patch.object(ConfluenceBuilder, 'publish_doc') as mm:
            self.build(self.dataset, config=config)

        mm.assert_has_calls([
            call('page-a', ANY),
            call('folder/page-b', ANY),
        ], any_order=True)

    def test_config_publishlist_allow_list_cli_empty(self):
        config = dict(self.config)
        config['confluence_publish_allowlist'] = ''

        with patch.object(ConfluenceBuilder, 'publish_doc') as mm:
            self.build(self.dataset, config=config)

        # special case: typically, a set allow list that is empty could be
        # considered as an empty list which hints to no documents published;
        # however, we want to ensure support for users trying to "unset" the
        # configured option via command line -- if users wanted to help
        # enforce denying publication for all documents via command line, they
        # can achieve this by forcing the publish option off
        mm.assert_has_calls([
            call('index', ANY),
            call('page-a', ANY),
            call('folder/page-b', ANY),
        ], any_order=True)

    def test_config_publishlist_allow_list_file_default_abs(self):
        publish_list = self.dataset / 'publish-list-default'

        config = dict(self.config)
        config['confluence_publish_allowlist'] = publish_list

        with patch.object(ConfluenceBuilder, 'publish_doc') as mm:
            self.build(self.dataset, config=config)

        mm.assert_has_calls([
            call('page-a', ANY),
            call('folder/page-b', ANY),
        ], any_order=True)

    def test_config_publishlist_allow_list_file_default_relative(self):
        config = dict(self.config)
        config['confluence_publish_allowlist'] = 'publish-list-default'

        with patch.object(ConfluenceBuilder, 'publish_doc') as mm:
            self.build(self.dataset, config=config)

        mm.assert_has_calls([
            call('page-a', ANY),
            call('folder/page-b', ANY),
        ], any_order=True)

    def test_config_publishlist_allow_list_file_empty(self):
        publish_list = self.dataset / 'publish-list-empty'

        config = dict(self.config)
        config['confluence_publish_allowlist'] = publish_list

        with patch.object(ConfluenceBuilder, 'publish_doc') as mm:
            self.build(self.dataset, config=config)

        mm.assert_not_called()

    def test_config_publishlist_allow_multiple(self):
        config = dict(self.config)
        config['confluence_publish_allowlist'] = ['index', 'page-a']

        with patch.object(ConfluenceBuilder, 'publish_doc') as mm:
            self.build(self.dataset, config=config)

        mm.assert_has_calls([
            call('index', ANY),
            call('page-a', ANY),
        ], any_order=True)

    def test_config_publishlist_allow_none(self):
        config = dict(self.config)
        config['confluence_publish_allowlist'] = None

        with patch.object(ConfluenceBuilder, 'publish_doc') as mm:
            self.build(self.dataset, config=config)

        mm.assert_has_calls([
            call('index', ANY),
            call('page-a', ANY),
            call('folder/page-b', ANY),
        ], any_order=True)

    def test_config_publishlist_allow_singledoc_root(self):
        config = dict(self.config)
        config['confluence_publish_allowlist'] = ['page-a']

        with patch.object(ConfluenceBuilder, 'publish_doc') as mm:
            self.build(self.dataset, config=config)

        mm.assert_has_calls([
            call('page-a', ANY),
        ], any_order=True)

    def test_config_publishlist_allow_singledoc_subfolder(self):
        config = dict(self.config)
        config['confluence_publish_allowlist'] = ['folder/page-b']

        with patch.object(ConfluenceBuilder, 'publish_doc') as mm:
            self.build(self.dataset, config=config)

        mm.assert_has_calls([
            call('folder/page-b', ANY),
        ], any_order=True)

    def test_config_publishlist_default(self):
        with patch.object(ConfluenceBuilder, 'publish_doc') as mm:
            self.build(self.dataset)

        mm.assert_has_calls([
            call('index', ANY),
            call('page-a', ANY),
            call('folder/page-b', ANY),
        ], any_order=True)

    def test_config_publishlist_deny_empty(self):
        config = dict(self.config)
        config['confluence_publish_denylist'] = []

        with patch.object(ConfluenceBuilder, 'publish_doc') as mm:
            self.build(self.dataset, config=config)

        mm.assert_has_calls([
            call('index', ANY),
            call('page-a', ANY),
            call('folder/page-b', ANY),
        ], any_order=True)

    def test_config_publishlist_deny_list_cli_default(self):
        config = dict(self.config)
        config['confluence_publish_denylist'] = 'page-a,folder/page-b'

        with patch.object(ConfluenceBuilder, 'publish_doc') as mm:
            self.build(self.dataset, config=config)

        mm.assert_has_calls([
            call('index', ANY),
        ], any_order=True)

    def test_config_publishlist_deny_list_cli_empty(self):
        config = dict(self.config)
        config['confluence_publish_denylist'] = ''

        with patch.object(ConfluenceBuilder, 'publish_doc') as mm:
            self.build(self.dataset, config=config)

        mm.assert_has_calls([
            call('index', ANY),
            call('page-a', ANY),
            call('folder/page-b', ANY),
        ], any_order=True)

    def test_config_publishlist_deny_list_file_default_abs(self):
        publish_list = self.dataset / 'publish-list-default'

        config = dict(self.config)
        config['confluence_publish_denylist'] = publish_list

        with patch.object(ConfluenceBuilder, 'publish_doc') as mm:
            self.build(self.dataset, config=config)

        mm.assert_has_calls([
            call('index', ANY),
        ], any_order=True)

    def test_config_publishlist_deny_list_file_default_relative(self):
        config = dict(self.config)
        config['confluence_publish_denylist'] = 'publish-list-default'

        with patch.object(ConfluenceBuilder, 'publish_doc') as mm:
            self.build(self.dataset, config=config)

        mm.assert_has_calls([
            call('index', ANY),
        ], any_order=True)

    def test_config_publishlist_deny_list_file_empty(self):
        publish_list = self.dataset / 'publish-list-empty'

        config = dict(self.config)
        config['confluence_publish_denylist'] = publish_list

        with patch.object(ConfluenceBuilder, 'publish_doc') as mm:
            self.build(self.dataset, config=config)

        mm.assert_has_calls([
            call('index', ANY),
            call('page-a', ANY),
            call('folder/page-b', ANY),
        ], any_order=True)

    def test_config_publishlist_deny_multiple(self):
        config = dict(self.config)
        config['confluence_publish_denylist'] = ['index', 'page-a']

        with patch.object(ConfluenceBuilder, 'publish_doc') as mm:
            self.build(self.dataset, config=config)

        mm.assert_has_calls([
            call('folder/page-b', ANY),
        ], any_order=True)

    def test_config_publishlist_deny_none(self):
        config = dict(self.config)
        config['confluence_publish_denylist'] = None

        with patch.object(ConfluenceBuilder, 'publish_doc') as mm:
            self.build(self.dataset, config=config)

        mm.assert_has_calls([
            call('index', ANY),
            call('page-a', ANY),
            call('folder/page-b', ANY),
        ], any_order=True)

    def test_config_publishlist_deny_singledoc_root(self):
        config = dict(self.config)
        config['confluence_publish_denylist'] = ['page-a']

        with patch.object(ConfluenceBuilder, 'publish_doc') as mm:
            self.build(self.dataset, config=config)

        mm.assert_has_calls([
            call('index', ANY),
            call('folder/page-b', ANY),
        ], any_order=True)

    def test_config_publishlist_deny_singledoc_subfolder(self):
        config = dict(self.config)
        config['confluence_publish_denylist'] = ['folder/page-b']

        with patch.object(ConfluenceBuilder, 'publish_doc') as mm:
            self.build(self.dataset, config=config)

        mm.assert_has_calls([
            call('index', ANY),
            call('page-a', ANY),
        ], any_order=True)
