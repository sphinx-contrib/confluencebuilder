# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from sphinxcontrib.confluencebuilder.exceptions import ConfluenceAuthenticationFailedUrlError
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceBadServerUrlError
from sphinxcontrib.confluencebuilder.exceptions import ConfluencePermissionError
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceProxyPermissionError
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceTimeoutError
from sphinxcontrib.confluencebuilder.publisher import ConfluencePublisher
from tests.lib import mock_confluence_instance
from tests.lib import prepare_conf
import os
import time
import unittest


class TestConfluencePublisherConnect(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = prepare_conf()
        cls.config.confluence_timeout = 1

    def test_publisher_connect_bad_response_code(self):
        """validate publisher can handle bad response code"""
        #
        # Verify that the initial connection event for a publisher can safely
        # handle a 500 server error on a connection.

        with mock_confluence_instance(self.config) as daemon:
            daemon.register_get_rsp(500, None)

            publisher = ConfluencePublisher()
            publisher.init(self.config)

            with self.assertRaises(ConfluenceBadServerUrlError):
                publisher.connect()

    def test_publisher_connect_handle_authentication_error(self):
        """validate publisher reports an authentication error"""
        #
        # Verify that the publisher will report a tailored error message when a
        # Confluence instance reports an authentication issue.

        with mock_confluence_instance(self.config) as daemon:
            daemon.register_get_rsp(401, None)

            publisher = ConfluencePublisher()
            publisher.init(self.config)

            with self.assertRaises(ConfluenceAuthenticationFailedUrlError):
                publisher.connect()

    def test_publisher_connect_handle_permission_error(self):
        """validate publisher reports a permission error"""
        #
        # Verify that the publisher will report a tailored error message when a
        # Confluence instance reports a Confluence-specific permission issue.

        with mock_confluence_instance(self.config) as daemon:
            daemon.register_get_rsp(403, None)

            publisher = ConfluencePublisher()
            publisher.init(self.config)

            with self.assertRaises(ConfluencePermissionError):
                publisher.connect()

    def test_publisher_connect_handle_proxy_permission_error(self):
        """validate publisher reports a proxy-permission error"""
        #
        # Verify that the publisher will report a tailored error message when a
        # configured proxy reports a permission issue.

        with mock_confluence_instance(self.config) as daemon:
            daemon.register_get_rsp(407, None)

            publisher = ConfluencePublisher()
            publisher.init(self.config)

            with self.assertRaises(ConfluenceProxyPermissionError):
                publisher.connect()

    def test_publisher_connect_invalid_json(self):
        """validate publisher can handle non-json data"""
        #
        # Verify that the initial connection event for a publisher can safely
        # handle non-JSON data returned from a configured instance (either a
        # non-Confluence instance or a proxy response).

        with mock_confluence_instance(self.config) as daemon:
            daemon.register_get_rsp(200, 'Welcome to my website.')

            publisher = ConfluencePublisher()
            publisher.init(self.config)

            with self.assertRaises(ConfluenceBadServerUrlError):
                publisher.connect()

    def test_publisher_connect_proxy(self):
        """validate publisher can find a valid space"""
        #
        # Verify that a publisher can query a Confluence instance and cache the
        # display name for a space.

        std_space_name = 'My Default Space'
        std_rsp = {
            'size': 1,
            'results': [{
                'name': std_space_name,
            }],
        }

        proxy_space_name = 'My Proxy Space'
        proxy_rsp = {
            'size': 1,
            'results': [{
                'name': proxy_space_name,
            }],
        }

        try:
            with mock_confluence_instance(self.config) as default_daemon,\
                    mock_confluence_instance() as proxy_daemon:

                proxy_host, proxy_port = proxy_daemon.server_address
                proxy_url = 'http://{}:{}/'.format(proxy_host, proxy_port)

                # check default space is accessible
                default_daemon.register_get_rsp(200, std_rsp)
                proxy_daemon.register_get_rsp(200, proxy_rsp)

                publisher = ConfluencePublisher()
                publisher.init(self.config)
                publisher.connect()

                self.assertEqual(publisher.space_display_name, std_space_name)

                # check confluence proxy option will go through proxy instance
                config = self.config.clone()
                config.confluence_proxy = proxy_url

                default_daemon.register_get_rsp(200, std_rsp)
                proxy_daemon.register_get_rsp(200, proxy_rsp)

                publisher = ConfluencePublisher()
                publisher.init(config)
                publisher.connect()

                self.assertEqual(publisher.space_display_name, proxy_space_name)

                # check system proxy option will go through proxy instance
                os.environ['http_proxy'] = proxy_url

                default_daemon.register_get_rsp(200, std_rsp)
                proxy_daemon.register_get_rsp(200, proxy_rsp)

                publisher = ConfluencePublisher()
                publisher.init(self.config)
                publisher.connect()

                self.assertEqual(publisher.space_display_name, proxy_space_name)
        finally:
            if 'http_proxy' in os.environ:
                del os.environ['http_proxy']

    def test_publisher_connect_unsupported_json(self):
        """validate publisher can handle unexpected json data"""
        #
        # Verify that the initial connection event for a publisher provides a
        # bit more strict error checking on the provided JSON data returned.
        # This is to help deal with a configuration which points to a
        # non-Confluence instance, but the server provides JSON data in its
        # response.

        with mock_confluence_instance(self.config) as daemon:
            publisher = ConfluencePublisher()
            publisher.init(self.config)

            # random json data
            rsp = {
                'some-data': 'hello',
            }
            daemon.register_get_rsp(200, rsp)
            with self.assertRaises(ConfluenceBadServerUrlError):
                publisher.connect()

            # data with a size field, but unrelated data
            rsp = {
                'size': 3,
                'data': [
                    'item-1',
                    'item-2',
                    'item-3',
                ],
            }
            daemon.register_get_rsp(200, rsp)
            with self.assertRaises(ConfluenceBadServerUrlError):
                publisher.connect()

            # result data not matching expected
            rsp = {
                'size': 1,
                'results': [{
                    'misc-option': 123,
                }],
            }
            daemon.register_get_rsp(200, rsp)
            with self.assertRaises(ConfluenceBadServerUrlError):
                publisher.connect()

    def test_publisher_connect_valid_space(self):
        """validate publisher can find a valid space"""
        #
        # Verify that a publisher can query a Confluence instance and cache the
        # display name for a space.

        space_name = 'My Space'

        val = {
            'size': 1,
            'results': [{
                'name': space_name,
            }],
        }

        with mock_confluence_instance(self.config) as daemon:
            daemon.register_get_rsp(200, val)

            publisher = ConfluencePublisher()
            publisher.init(self.config)
            publisher.connect()

            self.assertEqual(publisher.space_display_name, space_name)

    def test_publisher_connect_verify_timeout(self):
        """validate publisher timeout"""
        #
        # Verify that a non-served request from a publisher event will timeout.

        with mock_confluence_instance(self.config, ignore_requests=True):
            publisher = ConfluencePublisher()
            publisher.init(self.config)

            start = time.time()

            with self.assertRaises(ConfluenceTimeoutError):
                publisher.connect()

            end = time.time()
            diff = int(end - start)

            self.assertLessEqual(diff, self.config.confluence_timeout + 1)
