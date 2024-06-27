# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from sphinxcontrib.confluencebuilder.util import detect_cloud
import unittest


class TestConfluenceUtilDetectCloud(unittest.TestCase):
    def test_util_detect_cloud(self):
        self.assertTrue(detect_cloud('https://ex.atlassian.net/wiki/'))
        self.assertTrue(detect_cloud('https://ex.atlassian.net:443/wiki/'))
        self.assertFalse(detect_cloud('https://www.example.org/wiki/'))
        self.assertFalse(detect_cloud('https://www.example.org:443/wiki/'))
