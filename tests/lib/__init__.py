# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from bs4 import BeautifulSoup
from contextlib import contextmanager
from pkg_resources import parse_version
from sphinx.__init__ import __version__ as sphinx_version
from sphinx.application import Sphinx
from sphinx.util.console import nocolor, color_terminal
from sphinx.util.docutils import docutils_namespace
import difflib
import io
import os
import shutil
import sys

"""
full extension name
"""
EXT_NAME = 'sphinxcontrib.confluencebuilder'

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

def enableSphinxStatus():
    """
    enable verbosity for features handled by this utility class

    When invoked, this utility class will attempt to prepare or invoke
    requests in a verbose manner.
    """
    os.environ['SPHINX_STATUS'] = '1'

@contextmanager
def parse(filename, dirname=None):
    """
    parse the output of a generated sphinx document

    Parses the provided filename for generated Confluence-supported markup which
    can be examined for expected content. This function will return an instance
    of BeautifulSoup which a tester can take advantage of the utility calls the
    library provides.

    Args:
        filename: the filename to parse
        dirname (optional): the directory the provided filename exists in

    Returns:
        the parsed output
    """
    if dirname:
        target = os.path.join(dirname, filename)
    else:
        target = filename

    target += '.conf'

    with open(target, 'r') as fp:
        soup = BeautifulSoup(fp, 'html.parser')
        yield soup

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
    if parse_version(sphinx_version) < parse_version('2.0'):
        config['master_doc'] = 'index'

    return config

def prepareDirectories(container):
    """
    return the output directory base for all unit tests

    This utility method is used to provide other tests the location to store
    output files. Two paths are provided by this call - the document
    directory and a doctree directory. This method will ensure the
    directories are removed before returning.
    """
    assert container
    lib_dir = os.path.dirname(os.path.realpath(__file__))
    base_dir = os.path.join(lib_dir, os.pardir)
    output_dir = os.path.join(base_dir, 'output')
    container_dir = os.path.join(output_dir, container)
    doc_dir = os.path.join(container_dir, 'build')
    doctree_dir = os.path.join(container_dir, 'doctree')

    shutil.rmtree(container_dir, ignore_errors=True)

    return doc_dir, doctree_dir

@contextmanager
def prepareSphinx(src_dir, out_dir, doctree_dir, config=None, extra_config=None,
        builder=None, relax=False):
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

    conf = dict(config) if config else {}
    if extra_config:
        conf.update(extra_config)
    conf_dir = src_dir if config is None else None
    warnerr = not relax

    sts = None
    if 'SPHINX_STATUS' in os.environ:
        sts = sys.stdout

    verbosity = 0
    if 'SPHINX_VERBOSITY' in os.environ:
        try:
            verbosity = int(os.environ['SPHINX_VERBOSITY'])
        except ValueError:
            pass

    # default to using this extension's builder
    if not builder:
        builder = 'confluence'

    with docutils_namespace():
        app = Sphinx(
            src_dir,                # output for document sources
            conf_dir,               # configuration directory
            out_dir,                # output for generated documents
            doctree_dir,            # output for doctree files
            builder,                # builder to execute
            confoverrides=conf,     # load provided configuration (volatile)
            status=sts,             # status output
            warning=sys.stderr,     # warnings output
            warningiserror=warnerr, # treat warnings as errors
            verbosity=verbosity)    # verbosity

        yield app

def buildSphinx(src_dir, out_dir, doctree_dir, config=None, extra_config=None,
        builder=None, relax=False):
    """
    prepare a sphinx application instance

    Creates, invokes and cleans up a Sphinx application instance [1].

    [1]: https://github.com/sphinx-doc/sphinx/blob/master/sphinx/application.py
    """
    with prepareSphinx(
            src_dir, out_dir, doctree_dir, config=config,
            extra_config=extra_config, builder=builder, relax=relax) as app:
        app.build(force_all=True)
