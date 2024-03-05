# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from sphinxcontrib.confluencebuilder.publisher import ConfluencePublisher
from tests.lib import autocleanup_publisher
from tests.lib import mock_confluence_instance
from tests.lib import prepare_conf_publisher
import unittest


class TestConfluencePublisherApiPrefix(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = prepare_conf_publisher()
        cls.config.confluence_space_key = 'MOCK'

        cls.std_space_connect_rsp = {
            'id': 1,
            'key': 'MOCK',
            'name': 'Mock Space',
            'type': 'global',
        }

        cls.std_spaces_connect_rsp = {
            'results': [
                cls.std_space_connect_rsp,
            ],
        }

    def test_publisher_api_prefix_default(self):
        """validate publisher includes an api prefix"""
        #
        # Verify that a publisher will perform requests which target the
        # `/rest/api` endpoint.

        with mock_confluence_instance(self.config) as daemon, \
                autocleanup_publisher(ConfluencePublisher) as publisher:
            daemon.register_get_rsp(200, self.std_space_connect_rsp)

            publisher.init(self.config)
            publisher.connect()

            # connect request
            connect_req = daemon.pop_get_request()
            self.assertIsNotNone(connect_req)
            req_path, _ = connect_req
            self.assertTrue('/rest/api/' in req_path)

    def test_publisher_api_prefix_override_v1(self):
        """validate publisher can disable a v1 api prefix"""
        #
        # Verify that a publisher can perform requests disables the use of
        # the `rest/api` prefix.

        config = self.config.clone()
        config.confluence_api_mode = 'v1'
        config.confluence_publish_override_api_prefix = {
            'v1': 'my-custom-v1/',
        }

        with mock_confluence_instance(config) as daemon, \
                autocleanup_publisher(ConfluencePublisher) as publisher:
            daemon.register_get_rsp(200, self.std_space_connect_rsp)

            publisher.init(config)
            publisher.connect()

            # connect request
            connect_req = daemon.pop_get_request()
            self.assertIsNotNone(connect_req)
            req_path, _ = connect_req
            self.assertFalse('/rest/api/' in req_path)
            self.assertTrue('/my-custom-v1/' in req_path)

    def test_publisher_api_prefix_override_v2(self):
        """validate publisher can disable a v2 api prefix"""
        #
        # Verify that a publisher can perform requests disables the use of
        # the `api/v2` prefix.

        config = self.config.clone()
        config.confluence_api_mode = 'v2'
        config.confluence_publish_override_api_prefix = {
            'v2': 'my-custom-v2/',
        }

        with mock_confluence_instance(config) as daemon, \
                autocleanup_publisher(ConfluencePublisher) as publisher:
            daemon.register_get_rsp(200, self.std_spaces_connect_rsp)

            publisher.init(config)
            publisher.connect()

            # connect request
            connect_req = daemon.pop_get_request()
            self.assertIsNotNone(connect_req)
            req_path, _ = connect_req
            self.assertFalse('/api/v2/' in req_path)
            self.assertTrue('/my-custom-v2/' in req_path)
