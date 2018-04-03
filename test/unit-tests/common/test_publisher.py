# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2016-2018 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

import ssl
import unittest
from http.client import HTTPConnection, HTTPSConnection

from sphinxcontrib.confluencebuilder.publisher import ConfluenceTransport


class TestConfluenceTransport(unittest.TestCase):
    def setUp(self):
        self.http_url = 'http://somehost'
        self.https_url = 'https://somehost'

    def test_make_connection_already_exists(self):
        transport = ConfluenceTransport(self.http_url, client_cert=None)
        connection = transport.make_connection('host')
        self.assertEqual(connection, transport.make_connection('host'))

    def test_make_http_connection(self):
        transport = ConfluenceTransport(self.http_url, client_cert=None)
        connection = transport.make_connection('host')
        self.assertIsInstance(connection, HTTPConnection)

    def test_make_https_connection_no_client_cert(self):
        transport = ConfluenceTransport(self.https_url, client_cert=None)
        connection = transport.make_connection('host')
        self.assertIsInstance(connection, HTTPSConnection)
        context = connection._context
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)

    def test_make_https_connection_disable_validation(self):
        transport = ConfluenceTransport(self.https_url)
        transport.disable_ssl_verification()
        connection = transport.make_connection('host')
        self.assertIsInstance(connection, HTTPSConnection)
        context = connection._context
        self.assertEqual(context.verify_mode, ssl.CERT_NONE)

    def test_make_http_connection_with_client_cert(self):
        transport = ConfluenceTransport(self.http_url,
                                        client_cert=("file1", None))
        connection = transport.make_connection('host')
        self.assertIsInstance(connection, HTTPConnection)