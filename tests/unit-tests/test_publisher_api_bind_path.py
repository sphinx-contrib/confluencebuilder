# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from sphinxcontrib.confluencebuilder.publisher import ConfluencePublisher
from tests.lib import autocleanup_publisher
from tests.lib import mock_confluence_instance
from tests.lib import prepare_conf_publisher
import unittest


class TestConfluencePublisherApiBindPath(unittest.TestCase):
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

    def test_publisher_api_bind_path_default(self):
        """validate publisher includes api bind path"""
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

    def test_publisher_api_bind_path_disabled(self):
        """validate publisher can disable api bind path"""
        #
        # Verify that a publisher can perform requests disables the use of
        # the `/rest/api` endpoint.

        config = self.config.clone()
        config.confluence_publish_disable_api_prefix = True

        with mock_confluence_instance(config) as daemon, \
                autocleanup_publisher(ConfluencePublisher) as publisher:
            daemon.register_get_rsp(200, self.std_space_connect_rsp)

            publisher.init(config)
            publisher.connect()

            # connect request
            connect_req = daemon.pop_get_request()
            self.assertIsNotNone(connect_req)
            req_path, _ = connect_req
            self.assertTrue('/rest/api/' not in req_path)
