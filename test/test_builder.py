# -*- coding: utf-8 -*-
"""
    sphinxcontrib.confluencebuilder.test.test_builder
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2016-2017 by the contributors (see AUTHORS file).
    :license: BSD, see LICENSE.txt for details.
"""

from sphinx.application import Sphinx
from sphinxcontrib.confluencebuilder.builder import ConfluenceBuilder
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceConfigurationError
import difflib
import io
import os
import sys
import unittest

class TestConfluenceBuilder(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        basedir = os.path.dirname(os.path.realpath(__file__))
        srcdir = os.path.join(basedir, 'testproj')
        self.expected = os.path.join(srcdir, 'expected')
        builddir = os.path.join(srcdir, 'build')
        self.outdir = os.path.join(builddir, 'out')
        doctreedir = os.path.join(builddir, 'doctree')

        self.config = {}
        self.config['extensions'] = ['sphinxcontrib.confluencebuilder']
        self.config['confluence_parent_page'] = 'Documentation'
        self.config['confluence_publish'] = False
        self.config['confluence_space_name'] = 'TEST'

        self.app = Sphinx(
            srcdir, None, self.outdir, doctreedir, 'confluence', self.config)
        self.app.build(force_all=True)

    def _assertExpectedWithOutput(self, name):
        filename = name + '.conf'
        expected_path = os.path.join(self.expected, filename)
        test_path = os.path.join(self.outdir, filename)
        self.assertTrue(os.path.exists(expected_path))
        self.assertTrue(os.path.exists(test_path))

        with io.open(expected_path, encoding='utf8') as expected_file:
            with io.open(test_path, encoding='utf8') as test_file:
                expected_data = expected_file.readlines()
                test_data = test_file.readlines()
                diff = difflib.unified_diff(
                    expected_data, test_data, lineterm='')
                diff_data = ''.join(list(diff))
                self.assertTrue(diff_data == '', msg=diff_data)

    def test_registry(self):
        if hasattr(self.app, 'extensions'):
            self.assertTrue('sphinxcontrib.confluencebuilder' in
                            self.app.extensions.keys())
        else:
            self.assertTrue('sphinxcontrib.confluencebuilder' in
                            self.app._extensions.keys())

    def test_heading(self):
        test_path = os.path.join(self.outdir, 'heading.conf')
        self.assertTrue(os.path.exists(test_path))

        with io.open(test_path, encoding='utf8') as test_file:
            lines = test_file.readlines()

            self.assertEqual(lines[0], "h1. HEADING_TEST\n")
            self.assertEqual(lines[1], '\n')
            self.assertEqual(lines[2], 'h2. SUBHEADER_TEST\n')

    def test_list(self):
        test_path = os.path.join(self.outdir, 'list.conf')
        self.assertTrue(os.path.exists(test_path))

        with io.open(test_path, encoding='utf8') as test_file:
            lines = test_file.readlines()
            self.assertEqual(lines[0], 'h1. list test\n')
            self.assertEqual(lines[1], '\n')
            self.assertEqual(lines[2], "* BULLET_1\n")
            self.assertEqual(lines[3], '* BULLET_2\n')
            self.assertEqual(lines[4], '\n')
            self.assertEqual(lines[5], "# ENUMERATED_1\n")
            self.assertEqual(lines[6], '# ENUMERATED_2\n')

    def test_formatting(self):
        test_path = os.path.join(self.outdir, 'text.conf')
        self.assertTrue(os.path.exists(test_path))

        with io.open(test_path, encoding='utf8') as test_file:
            lines = test_file.readlines()
            self.assertEqual(lines[0], 'h1. this is a text test\n')
            self.assertEqual(lines[2], '_emphasis_\n')
            self.assertEqual(lines[4], '*strong emphasis*\n')
            self.assertEqual(lines[6], '[http://website.com/]\n')
            self.assertEqual(lines[10], '----\n')
            self.assertEqual(lines[12], 'End of transition test\n');

    def test_admonitions(self):
        test_path = os.path.join(self.outdir, 'admonitions.conf')
        self.assertTrue(os.path.exists(test_path))

        with io.open(test_path, encoding='utf8') as test_file:
            lines = test_file.readlines()
            self.assertEqual(lines[0], 'h1. Admonition Test\n')
            self.assertEqual(lines[2], '{note}attention-message{note}\n')
            self.assertEqual(lines[4], '{warning}caution-message{warning}\n')
            self.assertEqual(lines[6], '{warning}danger-message{warning}\n')
            self.assertEqual(lines[8], '{warning}error-message{warning}\n')
            self.assertEqual(lines[10], '{tip}hint-message{tip}\n')
            self.assertEqual(lines[12], '{warning}important-message{warning}\n')
            self.assertEqual(lines[14], '{info}note-message{info}\n')
            self.assertEqual(lines[16], '{tip}tip-message{tip}\n')
            self.assertEqual(lines[18], '{warning}warning-message{warning}\n')

    def test_code(self):
        test_path = os.path.join(self.outdir, 'code.conf')
        self.assertTrue(os.path.exists(test_path))

        with io.open(test_path, encoding='utf8') as test_file:
            lines = test_file.readlines()
            self.assertEqual(lines[0], 'h1. Code Test\n')
            self.assertEqual(lines[2], '{code:linenumbers=false|language=python}\n')
            self.assertEqual(lines[3], 'import antigravity\n')
            self.assertEqual(lines[4], 'antigravity.space()\n')
            self.assertEqual(lines[5], '{code}\n')

    def test_references(self):
        self._assertExpectedWithOutput('ref')

    def test_toctree(self):
        test_path = os.path.join(self.outdir, 'toctree.conf')
        self.assertTrue(os.path.exists(test_path))

        with io.open(test_path, encoding='utf8') as test_file:
            lines = test_file.readlines()
            self.assertEqual(lines[0], 'h1. TOCTREE\n')
            self.assertEqual(lines[2], '* [Code Test]\n')
            self.assertEqual(lines[3], '* [HEADING_TEST]\n')
            self.assertEqual(lines[4], '** [SUBHEADER_TEST|HEADING_TEST#SUBHEADER_TEST]\n')

    def test_table(self):
        test_path = os.path.join(self.outdir, 'tables.conf')
        self.assertTrue(os.path.exists(test_path))

        with io.open(test_path, encoding='utf8') as test_file:
            lines = test_file.readlines()
            self.assertEqual(len(lines), 6)
            self.assertEqual(lines[0], 'h1. Table Test\n')
            self.assertEqual(lines[2], '||A||B||A or B||\n')
            self.assertEqual(lines[3], '|False|False|False|\n')
            self.assertEqual(lines[4], '|True|False|True|\n')

    def test_publish(self):
        builder = ConfluenceBuilder(self.app)
        builder.config.confluence_publish = True
        with self.assertRaises(ConfluenceConfigurationError):
            builder.init()

    def test_bad_values(self):
        test_path = os.path.join(self.outdir, 'badvalues.conf')
        self.assertTrue(os.path.exists(test_path))

        with open(test_path, 'r') as test_file:
            lines = test_file.readlines()
            self.assertEqual(len(lines), 3)
            self.assertEqual(lines[0], 'This is a page with &lcub;bad&rcub; things\n')
            self.assertEqual(lines[2], '* Like a bad value in a &lt;list&gt;\n')

if __name__ == '__main__':
    sys.exit(unittest.main())
