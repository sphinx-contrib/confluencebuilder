# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from sphinxcontrib.confluencebuilder.util import extract_length
import unittest


class TestConfluenceUtilExtractLength(unittest.TestCase):
    def test_util_extractlen_invalid(self):
        self.assertEqual(extract_length(None), (None, None))
        self.assertEqual(extract_length(' '), (None, None))
        self.assertEqual(extract_length('px'), (None, None))
        self.assertEqual(extract_length(str(None)), (None, None))

    def test_util_extractlen_unitless(self):
        self.assertEqual(extract_length('123'), ('123', None))
        self.assertEqual(extract_length(' 123'), ('123', None))
        self.assertEqual(extract_length('123 '), ('123', None))

    def test_util_extractlen_units(self):
        self.assertEqual(extract_length('321px'), ('321', 'px'))
        self.assertEqual(extract_length('2em'), ('2', 'em'))
        self.assertEqual(extract_length('52 pt'), ('52', 'pt'))
        self.assertEqual(extract_length(' 3 ex '), ('3', 'ex'))
