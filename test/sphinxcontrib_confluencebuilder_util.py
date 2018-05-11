# -*- coding: utf-8 -*-
"""
    sphinxcontrib.confluencebuilder.test.test_builder
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2016-2018 by the contributors (see AUTHORS file).
    :license: BSD, see LICENSE.txt for details.
"""

from sphinx.util.console import nocolor, color_terminal
from sphinx.application import Sphinx
from sphinxcontrib.confluencebuilder.builder import ConfluenceBuilder
import difflib
import io
import os
import shutil
import sys
import unittest

"""
full extension name
"""
EXT_NAME = 'sphinxcontrib.confluencebuilder'

class ConfluenceTestUtil:
    """
    confluence test utility class

    This class is used to hold a series of utility methods, etc. to assist
    in unit test implementation for this Sphinx extension.
    """
    default_sphinx_status = None

    @staticmethod
    def assertExpectedWithOutput(test, name, expected, output):
        """
        compare two files for a unit test that should match

        This utility method is used to provide an expected file and an output
        (generated) file. If both provided files exist, the utility will attempt
        to read each file's contents and compare to ensure they match. On
        failure, the file differences will be output.
        """
        filename = name + '.conf'
        expected_path = os.path.join(expected, filename)
        test_path = os.path.join(output, filename)
        test.assertTrue(os.path.exists(expected_path),
            'missing expected file: {}'.format(expected_path))
        test.assertTrue(os.path.exists(test_path),
            'missing output file: {}'.format(test_path))

        with io.open(expected_path, encoding='utf8') as expected_file:
            with io.open(test_path, encoding='utf8') as test_file:
                expected_data = expected_file.readlines()
                test_data = test_file.readlines()
                diff = difflib.unified_diff(
                    expected_data, test_data, lineterm='')
                diff_hdr = 'expected and generated documents mismatch\n' \
                    '  expected: ' + expected_path + '\n' \
                    ' generated: ' + test_path + '\n' \
                    '\n'
                diff_data = ''.join(list(diff))
                test.assertTrue(diff_data == '', msg=(diff_hdr + diff_data))

    @staticmethod
    def enableVerbose():
        """
        enable verbosity for features handled by this utility class

        When invoked, this utility class will attempt to prepare or invoke
        requests in a verbose manner.
        """
        ConfluenceTestUtil.default_sphinx_status = sys.stdout

    @staticmethod
    def prepareConfiguration():
        """
        prepare minimal sphinx configuration for sphinx application

        Prepares a minimum number of required configuration values into a
        dictionary for unit tests to extend. This dictionary can be passed into
        a Sphinx applicaiton instance.
        """
        config = {}
        config['extensions'] = [EXT_NAME]
        config['confluence_publish'] = False
        config['confluence_space_name'] = 'unit-test'
        return config

    @staticmethod
    def prepareDirectories(container):
        """
        return the output directory base for all unit tests

        This utility method is used to provide other tests the location to store
        output files. Two paths are provided by this call - the document
        directory and a doctree directory. This method will ensure the
        directories are removed before returning.
        """
        assert container
        base_dir = os.path.dirname(os.path.realpath(__file__))
        output_dir = os.path.join(base_dir, 'output')
        container_dir = os.path.join(output_dir, container)
        doc_dir = os.path.join(container_dir, 'build')
        doctree_dir = os.path.join(container_dir, 'doctree')

        shutil.rmtree(container_dir, ignore_errors=True)

        return doc_dir, doctree_dir

    @staticmethod
    def prepareSphinx(src_dir, out_dir, doctree_dir, config):
        """
        prepare a sphinx application instance

        Return a prepared Sphinx application instance [1] ready for execution.

        [1]: https://github.com/sphinx-doc/sphinx/blob/master/sphinx/application.py
        """
        # Enable coloring of warning and other messages.  Note that this can
        # cause sys.stderr to be mocked which is why we pass the new value
        # explicitly on the call to Sphinx() below.
        if not color_terminal():
            nocolor()

        sts = ConfluenceTestUtil.default_sphinx_status
        return Sphinx(
            src_dir,                # output for document sources
            None,                   # ignore configuration directory
            out_dir,                # output for generated documents
            doctree_dir,            # output for doctree files
            ConfluenceBuilder.name, # use this extension's builder
            confoverrides=dict(config), 
                                    # load the provided configuration (volatile)
            status=sts,             # status output
            warning=sys.stderr)     # warnings output
