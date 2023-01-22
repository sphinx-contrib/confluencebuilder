# SPDX-License-Identifier: BSD-2-Clause
# Copyright 2018-2023 Sphinx Confluence Builder Contributors (AUTHORS)

from sphinxcontrib.confluencebuilder.util import ConfluenceUtil
import unittest


class TestConfluenceUtil(unittest.TestCase):
    def test_util_normalize_baseurl(self):
        data = {
'https://example.atlassian.net/wiki':             'https://example.atlassian.net/wiki/',
'https://example.atlassian.net/wiki/':            'https://example.atlassian.net/wiki/',
'https://example.atlassian.net/wiki/rest/api':    'https://example.atlassian.net/wiki/',
'https://example.atlassian.net/wiki/rest/api/':   'https://example.atlassian.net/wiki/',
'https://intranet-wiki.example.com':              'https://intranet-wiki.example.com/',
'https://intranet-wiki.example.com/':             'https://intranet-wiki.example.com/',
'https://intranet-wiki.example.com/rest/api':     'https://intranet-wiki.example.com/',
'https://intranet-wiki.example.com/rest/api/':    'https://intranet-wiki.example.com/',
'http://example.atlassian.net/wiki':              'http://example.atlassian.net/wiki/',
        }
        for key in data:
            self.assertEqual(ConfluenceUtil.normalize_base_url(key), data[key])
