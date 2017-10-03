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
from sphinxcontrib.confluencebuilder.common import ConfluenceDocMap
import difflib
import io
import os
import sys
import unittest

def create_default_test_config():
    config = {}
    config['extensions'] = ['sphinxcontrib.confluencebuilder']
    config['confluence_parent_page'] = 'Documentation'
    config['confluence_publish'] = False
    config['confluence_remove_title'] = False
    config['confluence_space_name'] = 'TEST'
    return config

class TestConfluenceBuilder(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        base_dir = os.path.dirname(os.path.realpath(__file__))
        src_dir = os.path.join(base_dir, 'builder-set')
        self.expected = os.path.join(src_dir, 'expected-wiki')
        build_dir = os.path.join(base_dir, 'build')
        self.out_dir = os.path.join(build_dir, 'builder-out')
        doctree_dir = os.path.join(build_dir, 'builder-doctree')

        self.config = create_default_test_config()

        self.app = Sphinx(
            src_dir, None, self.out_dir, doctree_dir, 'confluence', self.config)
        self.app.build(force_all=True)

    def _assertExpectedWithOutput(self, name):
        filename = name + '.conf'
        expected_path = os.path.join(self.expected, filename)
        test_path = os.path.join(self.out_dir, filename)
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
        self._assertExpectedWithOutput('heading')

    def test_list(self):
        self._assertExpectedWithOutput('list')

    def test_formatting(self):
        self._assertExpectedWithOutput('formatting')

    def test_admonitions(self):
        self._assertExpectedWithOutput('admonitions')

    def test_code(self):
        self._assertExpectedWithOutput('code')

    def test_references(self):
        self._assertExpectedWithOutput('ref')

    def test_toctree(self):
        self._assertExpectedWithOutput('toctree')

    def test_table(self):
        self._assertExpectedWithOutput('tables')

    def test_no_parent(self):
        self.assertEqual(ConfluenceDocMap.parent('toctree'), None)
        self.assertEqual(ConfluenceDocMap.parent('code'), None)

    def test_publish(self):
        builder = ConfluenceBuilder(self.app)
        builder.config.confluence_publish = True
        with self.assertRaises(ConfluenceConfigurationError):
            builder.init()

    def test_bad_values(self):
        self._assertExpectedWithOutput('badvalues')

class TestConfluenceBuilderExperimentalParent(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        basedir = os.path.dirname(os.path.realpath(__file__))
        srcdir = os.path.join(basedir, 'testproj')
        self.expected = os.path.join(srcdir, 'expected')
        builddir = os.path.join(srcdir, 'build')
        self.outdir = os.path.join(builddir, 'experimental-parent-out')
        doctreedir = os.path.join(builddir, 'experimental-parent-doctree')

        self.config = create_default_test_config()
        self.config['master_doc'] = 'toctree'
        self.config['confluence_experimental_page_hierarchy'] = True

        self.app = Sphinx(
            srcdir, None, self.outdir, doctreedir, 'confluence', self.config)
        self.app.build(force_all=True)

    def test_parent(self):
        self.assertEqual(ConfluenceDocMap.parent('toctree'), None)
        self.assertEqual(ConfluenceDocMap.parent('code'), 'toctree')

class TestConfluenceBuilderExperimentalDepth(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        basedir = os.path.dirname(os.path.realpath(__file__))
        srcdir = os.path.join(basedir, 'testproj')
        self.expected = os.path.join(srcdir, 'expected')
        builddir = os.path.join(srcdir, 'build')
        self.outdir = os.path.join(builddir, 'experimental-depth-out')
        doctreedir = os.path.join(builddir, 'experimental-depth-doctree')

        self.config = create_default_test_config()
        self.config['master_doc'] = 'toctree'
        self.config['confluence_experimental_max_depth'] = 0

        self.app = Sphinx(
            srcdir, None, self.outdir, doctreedir, 'confluence', self.config)
        self.app.build(force_all=True)

    def test_parent(self):
        self.assertEqual(ConfluenceDocMap.depth('toctree'), 0)
        self.assertEqual(ConfluenceDocMap.depth('code'), 1)


if __name__ == '__main__':
    sys.exit(unittest.main())
