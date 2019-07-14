# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2017-2019 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from sphinxcontrib.confluencebuilder.state import ConfluenceState
from sphinxcontrib_confluencebuilder_util import ConfluenceTestUtil as testutil
import os
import unittest
import sys


class TestBase(unittest.TestCase):
    test_dir = os.path.dirname(os.path.realpath(__file__))
    dataset_base = os.path.join(test_dir, 'dataset-')

    @classmethod
    def setUpClass(self):
        self.classname = ''
        self.specific_configs = {}

    def expected_dir(self):
        return os.path.join(self.test_dir, 'expected-' + self.classname)

    def prepare_and_build(self):
        config = testutil.prepareConfiguration()
        for key, value in self.specific_configs.items():
            if isinstance(value, list) and isinstance(config[key], list):
                config[key].extend(value)
                continue
            config[key] = value

        doc_dir, doctree_dir = testutil.prepareDirectories(self.classname)

        dataset_dir = self.dataset_base + self.classname
        testutil.buildSphinx(dataset_dir, doc_dir, doctree_dir, config)

        return doc_dir


class TestVisitDescSignatureLine(TestBase):
    ''' called by doxygen directive '''
    @classmethod
    def setUpClass(self):
        self.classname = 'visit-desc-signature-line'
        self.specific_configs = {}
        self.specific_configs['breathe_default_project'] = 'nutshell'
        self.specific_configs['breathe_projects.nutshell'] = \
            os.path.join(self.dataset_base + self.classname, 'xml')
        self.specific_configs['extensions'] = ['breathe']

    @testutil.minimum_python_version('3.6')
    @testutil.minimum_sphinx_version('2.0')
    def test_visit_desc_signature_line(self):
        doc_dir = self.prepare_and_build()
        testutil.assertExpectedWithOutput(
            self, 'index', self.expected_dir(), doc_dir)


class TestVisitToctree(TestBase):
    ''' visited when an included file in a toctree
    defines another toctree
    '''
    @classmethod
    def setUpClass(self):
        self.classname = 'visit-toctree'
        self.specific_configs = {}

    def test_toctree(self):
        doc_dir = self.prepare_and_build()
        check_files = ['index', 'page']
        for check_file in check_files:
            testutil.assertExpectedWithOutput(
                self, check_file, self.expected_dir(), doc_dir)
