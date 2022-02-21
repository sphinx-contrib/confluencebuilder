# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2021-2022 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from sphinxcontrib.confluencebuilder.publisher import ConfluencePublisher
from tests.lib import mock_confluence_instance
from tests.lib import prepare_conf
import unittest


class TestConfluencePublisherPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = prepare_conf()
        cls.config.confluence_publish_debug = True
        cls.config.confluence_timeout = 5

        cls.std_space_connect_rsp = {
            'size': 1,
            'results': [{
                'name': 'Mock Space',
                'type': 'global',
            }],
        }

    def test_publisher_page_store_page_id_allow_watch(self):
        """validate publisher will store a page by id (watch)"""
        #
        # Verify that a publisher can update an existing page by an
        # identifier value. Instance will be configured to watch content,
        # so any page updates should not trigger an watch event.

        config = self.config.clone()
        config.confluence_watch = True

        with mock_confluence_instance(config) as daemon:
            daemon.register_get_rsp(200, self.std_space_connect_rsp)

            publisher = ConfluencePublisher()
            publisher.init(config)
            publisher.connect()

            # consume connect request
            self.assertIsNotNone(daemon.pop_get_request())

            # prepare response for a page id fetch
            expected_page_id = 7456
            mocked_version = 28

            page_fetch_rsp = {
                'id': str(expected_page_id),
                'title': 'mock page',
                'type': 'page',
                'version': {
                    'number': str(mocked_version),
                },
            }
            daemon.register_get_rsp(200, page_fetch_rsp)

            # prepare response for update event
            daemon.register_put_rsp(200, dict(page_fetch_rsp))

            # perform page update request
            data = {
                'content': 'dummy page data',
                'labels': [],
            }
            page_id = publisher.store_page_by_id(
                'dummy-name', expected_page_id, data)

            # check expected page id returned
            self.assertEqual(page_id, expected_page_id)

            # check that the provided page id is set in the request
            fetch_req = daemon.pop_get_request()
            self.assertIsNotNone(fetch_req)
            req_path, _ = fetch_req

            expected_request = '/rest/api/content/{}?'.format(expected_page_id)
            self.assertTrue(req_path.startswith(expected_request))

            # check that an update request is processed
            update_req = daemon.pop_put_request()
            self.assertIsNotNone(update_req)

            # verify that no other request was made
            self.assertFalse(daemon.check_unhandled_requests())

    def test_publisher_page_store_page_id_default(self):
        """validate publisher will store a page by id (default)"""
        #
        # Verify that a publisher can update an existing page by an
        # identifier value. By default, the update request will ensure
        # the user configures to not watch the page.

        with mock_confluence_instance(self.config) as daemon:
            daemon.register_get_rsp(200, self.std_space_connect_rsp)

            publisher = ConfluencePublisher()
            publisher.init(self.config)
            publisher.connect()

            # consume connect request
            self.assertIsNotNone(daemon.pop_get_request())

            # prepare response for a page id fetch
            expected_page_id = 4568
            mocked_version = 45

            page_fetch_rsp = {
                'id': str(expected_page_id),
                'title': 'mock page',
                'type': 'page',
                'version': {
                    'number': str(mocked_version),
                },
            }
            daemon.register_get_rsp(200, page_fetch_rsp)

            # prepare response for update event
            daemon.register_put_rsp(200, dict(page_fetch_rsp))

            # prepare response for unwatch event
            daemon.register_delete_rsp(200)

            # perform page update request
            data = {
                'content': 'dummy page data',
                'labels': [],
            }
            page_id = publisher.store_page_by_id(
                'dummy-name', expected_page_id, data)

            # check expected page id returned
            self.assertEqual(page_id, expected_page_id)

            # check that the provided page id is set in the request
            fetch_req = daemon.pop_get_request()
            self.assertIsNotNone(fetch_req)
            req_path, _ = fetch_req

            expected_request = '/rest/api/content/{}?'.format(expected_page_id)
            self.assertTrue(req_path.startswith(expected_request))

            # check that an update request is processed
            update_req = daemon.pop_put_request()
            self.assertIsNotNone(update_req)

            # check that the page is unwatched
            unwatch_req = daemon.pop_delete_request()
            self.assertIsNotNone(unwatch_req)
            req_path, _ = unwatch_req
            ereq = '/rest/api/user/watch/content/{}'.format(expected_page_id)
            self.assertEqual(req_path, ereq)

            # verify that no other request was made
            self.assertFalse(daemon.check_unhandled_requests())

    def test_publisher_page_store_page_id_dryrun(self):
        """validate publisher suppress store a page by id with dryrun"""
        #
        # Verify that a publisher will handle a id-page update request
        # properly when the dryrun flag is set.

        config = self.config.clone()
        config.confluence_publish_dryrun = True

        with mock_confluence_instance(config) as daemon:
            daemon.register_get_rsp(200, self.std_space_connect_rsp)

            publisher = ConfluencePublisher()
            publisher.init(config)
            publisher.connect()

            # consume connect request
            self.assertIsNotNone(daemon.pop_get_request())

            # prepare response for a page id fetch
            expected_page_id = 2

            page_rsp = {
                'id': expected_page_id,
                'title': 'mock page',
                'type': 'page',
            }
            daemon.register_get_rsp(200, page_rsp)

            page_id = publisher.store_page_by_id(
                'dummy-name', expected_page_id, {})

            # check expected page id returned
            self.assertEqual(page_id, expected_page_id)

            # check that the provided page id is set in the request
            fetch_req = daemon.pop_get_request()
            self.assertIsNotNone(fetch_req)
            req_path, _ = fetch_req

            expected_request = '/rest/api/content/{}?'.format(expected_page_id)
            self.assertTrue(req_path.startswith(expected_request))

            # verify that no update request was made
            self.assertFalse(daemon.check_unhandled_requests())
