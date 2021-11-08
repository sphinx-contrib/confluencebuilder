# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from sphinxcontrib.confluencebuilder.util import convert_px_length
import unittest

class TestConfluenceUtilConvertPxLength(unittest.TestCase):
    def test_util_convertpxlen_invalid(self):
        self.assertIsNone(convert_px_length(None, None))

    def test_util_convertpxlen_unitless(self):
        self.assertEqual(convert_px_length(123, None), 123)
        self.assertEqual(convert_px_length(456.2, None), 456)
        self.assertEqual(convert_px_length('789.7', None), 790)

    def test_util_convertpxlen_units(self):
        self.assertEqual(convert_px_length(321, 'px'), 321)
        self.assertEqual(convert_px_length('654', 'px'), 654)
        self.assertEqual(convert_px_length('987.6', 'px'), 988)
        self.assertEqual(convert_px_length('987.3', 'px'), 987)
        self.assertEqual(convert_px_length(1, 'in'), 96)
        self.assertEqual(convert_px_length(1, 'pc'), 16)
        self.assertGreater(convert_px_length(100, 'em'), 100)
        self.assertGreater(convert_px_length(100, 'ex'), 100)
        self.assertGreater(convert_px_length(100, 'mm'), 100)
        self.assertGreater(convert_px_length(100, 'cm'), 100)
        self.assertGreater(convert_px_length(100, 'pt'), 100)
