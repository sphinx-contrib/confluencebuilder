# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2016-2019 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from contextlib import contextmanager
from sphinx.application import Sphinx
from sphinx.util.console import nocolor, color_terminal
from sphinx.util.docutils import docutils_namespace
from sphinx import __version__ as sphinx_version
from sphinxcontrib.confluencebuilder.builder import ConfluenceBuilder
import difflib
import io
import os
import shutil
import sys
import unittest
from pkg_resources import parse_version
import platform

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
    def assertExpectedWithOutput(test, name, expected, output, tpn=None):
        """
        compare two files for a unit test that should match

        This utility method is used to provide an expected file and an output
        (generated) file. If both provided files exist, the utility will attempt
        to read each file's contents and compare to ensure they match. On
        failure, the file differences will be output.
        """
        if not tpn:
            tpn = name
        expected_path = os.path.join(expected, name + '.conf')
        test_path = os.path.join(output, tpn + '.conf')
        test.assertTrue(os.path.exists(expected_path),
            'missing expected file: {}'.format(expected_path))
        test.assertTrue(os.path.exists(test_path),
            'missing output file: {}'.format(test_path))

        def relaxed_data(f):
            return [o.strip() + '\n' for o in f.readlines()]

        with io.open(expected_path, encoding='utf8') as expected_file:
            with io.open(test_path, encoding='utf8') as test_file:
                expected_data = relaxed_data(expected_file)
                test_data = relaxed_data(test_file)
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
        a Sphinx application instance.
        """
        config = {}
        config['extensions'] = [EXT_NAME]
        config['confluence_publish'] = False
        config['confluence_space_name'] = 'unit-test'
        # support pre-Sphinx v2.0 installations which default to 'contents'
        config['master_doc'] = 'index' 
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
    @contextmanager
    def prepareSphinx(src_dir, out_dir, doctree_dir, config=None):
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
        conf = dict(config) if config else None
        conf_dir = src_dir if not conf else None

        with docutils_namespace():
            app = Sphinx(
                src_dir,                # output for document sources
                conf_dir,               # ignore configuration directory
                out_dir,                # output for generated documents
                doctree_dir,            # output for doctree files
                ConfluenceBuilder.name, # use this extension's builder
                confoverrides=conf,     # load provided configuration (volatile)
                status=sts,             # status output
                warning=sys.stderr)     # warnings output

            yield app

    @staticmethod
    def buildSphinx(src_dir, out_dir, doctree_dir, config=None):
        """
        prepare a sphinx application instance

        Creates, invokes and cleans up a Sphinx application instance [1].

        [1]: https://github.com/sphinx-doc/sphinx/blob/master/sphinx/application.py
        """
        with ConfluenceTestUtil.prepareSphinx(
                src_dir, out_dir, doctree_dir, config) as app:
            app.build(force_all=True)

    @staticmethod
    def skip_test_function_if(skip_condition):
        ''' decorator of decorator to receive the condition as argument '''
        def decorator(func):
            def wrapper(*args, **kwargs):
                if skip_condition:
                    return lambda : None  # do nothing
                return func(*args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def minimum_python_version(min_version):
        skip_condition = parse_version(platform.python_version()) < \
                         parse_version(min_version)
        return ConfluenceTestUtil.skip_test_function_if(skip_condition)

    @staticmethod
    def minimum_sphinx_version(min_version):
        skip_condition = parse_version(sphinx_version) < \
                         parse_version(min_version)
        return ConfluenceTestUtil.skip_test_function_if(skip_condition)
