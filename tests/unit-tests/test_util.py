# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2018-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

import unittest

from sphinxcontrib.confluencebuilder.util import ConfluenceUtil as UTIL


class TestConfluenceUtil(unittest.TestCase):
    def test_util_normalize_baseurl(self):
        data = {
            "https://example.atlassian.net/wiki": "https://example.atlassian.net/wiki/",
            "https://example.atlassian.net/wiki/": "https://example.atlassian.net/wiki/",
            "https://example.atlassian.net/wiki/rest/api": "https://example.atlassian.net/wiki/",
            "https://example.atlassian.net/wiki/rest/api/": "https://example.atlassian.net/wiki/",
            "https://intranet-wiki.example.com": "https://intranet-wiki.example.com/",
            "https://intranet-wiki.example.com/": "https://intranet-wiki.example.com/",
            "https://intranet-wiki.example.com/rest/api": "https://intranet-wiki.example.com/",
            "https://intranet-wiki.example.com/rest/api/": "https://intranet-wiki.example.com/",
            "http://example.atlassian.net/wiki": "http://example.atlassian.net/wiki/",
        }
        for key in data:
            self.assertEqual(UTIL.normalizeBaseUrl(key), data[key])
