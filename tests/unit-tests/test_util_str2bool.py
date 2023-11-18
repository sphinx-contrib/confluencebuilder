# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from sphinxcontrib.confluencebuilder.util import str2bool
import unittest


class TestConfluenceUtilStr2Bool(unittest.TestCase):
    def test_util_str2bool_invalid(self):
        with self.assertRaises(ValueError):
            str2bool(None)

        with self.assertRaises(ValueError):
            str2bool(2)

        with self.assertRaises(ValueError):
            str2bool({})

    def test_util_str2bool_true(self):
        self.assertTrue(str2bool('on'))
        self.assertTrue(str2bool('ON'))
        self.assertTrue(str2bool('true'))
        self.assertTrue(str2bool('TRUE'))
        self.assertTrue(str2bool('yes'))
        self.assertTrue(str2bool('YES'))
        self.assertTrue(str2bool('1'))
        self.assertTrue(str2bool(1))

    def test_util_str2bool_false(self):
        self.assertFalse(str2bool('false'))
        self.assertFalse(str2bool('FALSE'))
        self.assertFalse(str2bool('no'))
        self.assertFalse(str2bool('NO'))
        self.assertFalse(str2bool('off'))
        self.assertFalse(str2bool('OFF'))
        self.assertFalse(str2bool('0'))
        self.assertFalse(str2bool(0))
