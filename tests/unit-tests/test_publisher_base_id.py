# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from sphinxcontrib.confluencebuilder.publisher import ConfluencePublisher
from tests.lib import autocleanup_publisher
from tests.lib import mock_confluence_instance
from tests.lib import prepare_conf_publisher
import unittest


class TestConfluencePublisherBaseId(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = prepare_conf_publisher()

        cls.std_space_connect_rsp = {
            'size': 1,
            'results': [{
                'name': 'Mock Space',
                'type': 'global',
            }],
        }

    def test_publisher_page_base_id_parent_id(self):
        """validate publisher will search for parent page by id"""
        #
        # Verify that a publisher will find a base (pages) identifier, based
        # off a configured parent page id.

        expected_page_id = 4568436

        config = self.config.clone()
        config.confluence_parent_page = expected_page_id

        with mock_confluence_instance(config) as daemon, \
                autocleanup_publisher(ConfluencePublisher) as publisher:
            daemon.register_get_rsp(200, self.std_space_connect_rsp)

            publisher.init(config)
            publisher.connect()

            # consume connect request
            self.assertIsNotNone(daemon.pop_get_request())

            # prepare response for a page fetch
            page_fetch_rsp = {
                'id': expected_page_id,
                'title': 'mock page',
                'type': 'page',
            }
            daemon.register_get_rsp(200, page_fetch_rsp)

            # perform base page id fetch request
            base_id = publisher.get_base_page_id()

            # check expected page id returned
            self.assertEqual(base_id, expected_page_id)

            # check that the provided page id is set in the request
            fetch_req = daemon.pop_get_request()
            self.assertIsNotNone(fetch_req)
            req_path, _ = fetch_req

            expected_request = f'/rest/api/content/{expected_page_id}'
            self.assertTrue(req_path.startswith(expected_request))

            # verify that no other request was made
            daemon.check_unhandled_requests()

    def test_publisher_page_base_id_parent_name(self):
        """validate publisher will search for parent page by name"""
        #
        # Verify that a publisher will find a base (pages) identifier, based
        # off a configured parent page name.

        expected_page_name = 'refname-31421'

        config = self.config.clone()
        config.confluence_parent_page = expected_page_name

        with mock_confluence_instance(config) as daemon, \
                autocleanup_publisher(ConfluencePublisher) as publisher:
            daemon.register_get_rsp(200, self.std_space_connect_rsp)

            publisher.init(config)
            publisher.connect()

            # consume connect request
            self.assertIsNotNone(daemon.pop_get_request())

            # prepare response for a page fetch
            expected_page_id = '245'

            page_search_fetch_rsp = {
                'size': 1,
                'results': [{
                    'id': expected_page_id,
                    'title': 'mock page',
                    'type': 'page',
                }],
            }
            daemon.register_get_rsp(200, page_search_fetch_rsp)

            # perform base page id fetch request
            base_id = publisher.get_base_page_id()

            # check expected page id returned
            self.assertEqual(base_id, expected_page_id)

            # check that the provided page id is set in the request
            fetch_req = daemon.pop_get_request()
            self.assertIsNotNone(fetch_req)
            req_path, _ = fetch_req

            expected_opt = f'title={expected_page_name}'
            self.assertTrue(req_path.startswith('/rest/api/content'))
            self.assertTrue(expected_opt in expected_opt)

            # verify that no other request was made
            daemon.check_unhandled_requests()

    def test_publisher_page_base_id_parent_none(self):
        """validate publisher will search for parent page by name"""
        #
        # Verify that a publisher will find a base (pages) identifier, based
        # off a configured parent page name.

        with mock_confluence_instance(self.config) as daemon, \
                autocleanup_publisher(ConfluencePublisher) as publisher:
            daemon.register_get_rsp(200, self.std_space_connect_rsp)

            publisher.init(self.config)
            publisher.connect()

            # consume connect request
            self.assertIsNotNone(daemon.pop_get_request())

            # prepare response for a page fetch
            expected_page_id = '416'

            page_fetch_rsp = {
                'size': 1,
                'results': [{
                    'id': expected_page_id,
                    'title': 'mock page',
                    'type': 'page',
                }],
            }
            daemon.register_get_rsp(200, page_fetch_rsp)

            # request base id which should return nothing, with no request
            base_id = publisher.get_base_page_id()
            self.assertIsNone(base_id)

            # verify that no other request was made
            daemon.check_unhandled_requests()
