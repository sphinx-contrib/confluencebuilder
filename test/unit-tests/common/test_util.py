# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2018 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from sphinxcontrib.confluencebuilder.util import ConfluenceUtil as UTIL
import unittest

class TestConfluenceUtil(unittest.TestCase):
    def test_normalize_baseurl(self):
        data = {
'https://example.atlassian.net/wiki':             'https://example.atlassian.net/wiki/',
'https://example.atlassian.net/wiki/':            'https://example.atlassian.net/wiki/',
'https://example.atlassian.net/wiki/rest/api':    'https://example.atlassian.net/wiki/',
'https://example.atlassian.net/wiki/rest/api/':   'https://example.atlassian.net/wiki/',
'https://example.atlassian.net/wiki/rpc/xmlrpc':  'https://example.atlassian.net/wiki/',
'https://example.atlassian.net/wiki/rpc/xmlrpc/': 'https://example.atlassian.net/wiki/',
'https://intranet-wiki.example.com':              'https://intranet-wiki.example.com/',
'https://intranet-wiki.example.com/':             'https://intranet-wiki.example.com/',
'https://intranet-wiki.example.com/rest/api':     'https://intranet-wiki.example.com/',
'https://intranet-wiki.example.com/rest/api/':    'https://intranet-wiki.example.com/',
'https://intranet-wiki.example.com/rpc/xmlrpc':   'https://intranet-wiki.example.com/',
'https://intranet-wiki.example.com/rpc/xmlrpc/':  'https://intranet-wiki.example.com/',
'http://example.atlassian.net/wiki':              'http://example.atlassian.net/wiki/',
            }
        for key in data:
            self.assertEqual(UTIL.normalizeBaseUrl(key), data[key])
