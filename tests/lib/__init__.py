# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from bs4 import BeautifulSoup
from contextlib import contextmanager
from pkg_resources import parse_version
from sphinx.__init__ import __version__ as sphinx_version
from sphinx.application import Sphinx
from sphinx.util.console import color_terminal
from sphinx.util.console import nocolor
from sphinx.util.docutils import docutils_namespace
from sphinxcontrib.confluencebuilder import compat
from sphinxcontrib.confluencebuilder import util
import inspect
import os
import shutil
import sys

# full extension name
EXT_NAME = 'sphinxcontrib.confluencebuilder'

def enable_sphinx_info(verbosity=None):
    """
    enable verbosity for features handled by this utility class

    When invoked, this utility class will attempt to prepare or invoke
    requests in a verbose manner.

    Args:
        verbosity (optional): configure verbosity on the sphinx application
    """
    os.environ['SPHINX_STATUS'] = '1'
    if verbosity:
        os.environ['SPHINX_VERBOSITY'] = str(verbosity)

@contextmanager
def mock_getpass(mock):
    def _(prompt='Password: ', stream=sys.stdout):
        stream.write(prompt)
        stream.write('(mocked input> ')
        stream.write(mock)
        stream.write('\n')
        return mock

    try:
        original = util.getpass2
        util.getpass2 = _
        yield
    finally:
        util.getpass2 = original

@contextmanager
def mock_input(mock):
    def _(prompt=''):
        print(prompt + '(mocked input> ' + mock)
        return mock

    try:
        original = compat.input
        compat.input = _
        yield
    finally:
        compat.input = original

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

def prepare_conf():
    """
    prepare minimal sphinx configuration for sphinx application

    Prepares a minimum number of required configuration values into a
    dictionary for unit tests to extend. This dictionary can be passed into
    a Sphinx application instance.
    """
    config = {}
    config['extensions'] = [
        EXT_NAME,
        # include any forced-injected extensions (config support)
        'sphinx.ext.imgmath',
    ]
    config['confluence_publish'] = False

    # support pre-Sphinx v2.0 installations which default to 'contents'
    if parse_version(sphinx_version) < parse_version('2.0'):
        config['master_doc'] = 'index'

    return config

def prepare_dirs(container=None, f_back_count=1, postfix=None):
    """
    return the output directory base for all unit tests

    This utility method is used to provide other tests the location to store
    output files. This method will ensure the output directory is removed
    before returning.

    Args:
        container (optional): the output container name to use
        f_back_count (optional): number of frame objects to move back when
                                  attempting to auto-generate a container name

    Returns:
        the output directory
    """
    if not container:
        frame = inspect.currentframe()
        for i in range(f_back_count):
            frame = frame.f_back
        container = frame.f_code.co_name
    lib_dir = os.path.dirname(os.path.realpath(__file__))
    test_dir = os.path.join(lib_dir, os.pardir)
    base_dir = os.path.join(test_dir, os.pardir)
    output_dir = os.path.join(base_dir, 'output')
    container_dir = os.path.abspath(os.path.join(output_dir, container))
    if postfix:
        container_dir += postfix

    shutil.rmtree(container_dir, ignore_errors=True)

    return container_dir

@contextmanager
def prepare_sphinx(src_dir, config=None, out_dir=None, extra_config=None,
        builder=None, relax=False):
    """
    prepare a sphinx application instance

    Return a prepared Sphinx application instance [1] ready for execution.

    [1]: https://github.com/sphinx-doc/sphinx/blob/master/sphinx/application.py

    Args:
        src_dir: document sources
        config (optional): configuration to use
        out_dir (optional): output for generated documents
        extra_config (optional): additional configuration data to apply
        builder (optional): the builder to use
        relax (optional): do not generate warnings as errors
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

    if not out_dir:
        # 3 = prepare_dirs, this, contextmanager
        out_dir = prepare_dirs(f_back_count=3)

    doctrees_dir = os.path.join(out_dir, '.doctrees')

    # support pre-Sphinx v4.0 installations which do not have `root_doc` by
    # swapping to the obsolete configuration name
    if parse_version(sphinx_version) < parse_version('4.0'):
        if 'root_doc' in conf:
            conf['master_doc'] = conf['root_doc']
            del conf['root_doc']

    with docutils_namespace():
        app = Sphinx(
            src_dir,                # output for document sources
            conf_dir,               # configuration directory
            out_dir,                # output for generated documents
            doctrees_dir,           # output for doctree files
            builder,                # builder to execute
            confoverrides=conf,     # load provided configuration (volatile)
            status=sts,             # status output
            warning=sys.stderr,     # warnings output
            warningiserror=warnerr, # treat warnings as errors
            verbosity=verbosity)    # verbosity

        yield app

def prepare_sphinx_filenames(src_dir, filenames, configs=None):
    """
    prepare explicit filenames for a sphinx application instance

    A Sphinx engine allows accepting a list of filenames it will process;
    however, these filenames need to be set to full paths. This is not always
    convenient for testing, so this utility allows generating a filename list
    with the source directory prefixed for each entry.

    In addition, when passing a documentation set to process, Sphinx requires
    that the documentation set has an existing root document. In some testing
    datasets, they may not have one that exists. If this is detected, this
    helper will adjust the configuration to adjust the root document to a
    provided filename, which should prevent issues when the Sphinx application
    prepares an environment. This is only performed when configurations are
    provided in to this call. Multiple configuration entries can be provided,
    and only the last configuration entry (must exist and) will be updated in
    the event when a change is needed.

    Args:
        src_dir: document sources
        filenames: the documents to process relative to src_dir (no extensions)
        configs (optional): list of configurations to check for root doc issue

    Returns:
        the updated file name list
    """
    files = []
    for filename in filenames:
        files.append(os.path.join(src_dir, filename + '.rst'))

    if configs:
        root_doc = 'index'
        for config in configs:
            if config and 'root_doc' in config:
                root_doc = config['root_doc']
                break

        if root_doc not in filenames:
            configs[-1]['root_doc'] = filenames[0] # update last config

    return files

def build_sphinx(src_dir, config=None, out_dir=None, extra_config=None,
        builder=None, relax=False, filenames=None):
    """
    prepare a sphinx application instance

    Creates, invokes and cleans up a Sphinx application instance [1].

    [1]: https://github.com/sphinx-doc/sphinx/blob/master/sphinx/application.py

    Args:
        src_dir: document sources
        config (optional): configuration to use
        out_dir (optional): output for generated documents
        extra_config (optional): additional configuration data to apply
        builder (optional): the builder to use
        relax (optional): do not generate warnings as errors
        filenames (optional): specific documents to process

    Returns:
        the output directory
    """

    if not out_dir:
        # 2 = prepare_dirs, this
        out_dir = prepare_dirs(f_back_count=2)

    files = []
    force_all = True

    if filenames:
        # force-all not supported when using explicit filenames
        force_all = False

        # sphinx application requires full paths for explicit filenames
        extra_config = dict(extra_config) if extra_config else {}
        files = prepare_sphinx_filenames(src_dir, filenames,
            configs=(config, extra_config))

    with prepare_sphinx(
            src_dir, config=config, out_dir=out_dir, extra_config=extra_config,
            builder=builder, relax=relax) as app:
        app.build(force_all=force_all, filenames=files)

    return out_dir
