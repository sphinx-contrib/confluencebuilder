# -*- coding: utf-8 -*-
"""
    sphinxcontrib.confluencebuilder.test.test_publisher
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2017 by the contributors (see AUTHORS file).
    :license: BSD, see LICENSE.txt for details.
"""

from sphinx.application import Sphinx
from sphinxcontrib.confluencebuilder.builder import ConfluenceBuilder
from sphinxcontrib.confluencebuilder.common import ConfluenceLogger
import os
import sys
import unittest

DEFAULT_TEST_URL = 'https://jdknight.atlassian.net/wiki'
DEFAULT_TEST_USER = 'sphinxcontrib-confluencebuilder'
DEFAULT_TEST_SPACE = 'confluencebuilder'
DEFAULT_TEST_PARENT = 'test-holder'
DEFAULT_PUBLISH_KEY_FILE = '.test_publish_key'


class TestConfluencePublisher(unittest.TestCase):
    @classmethod
    def _conf(self, key, env, default=None):
        self.config[key] = os.getenv(env, default)

    @classmethod
    def setUpClass(self):
        basedir = os.path.dirname(os.path.realpath(__file__))
        val_dir = os.path.join(basedir, 'validation-set')
        build_dir = os.path.join(os.getcwd(), 'build')
        doctree_dir = os.path.join(build_dir, 'doctree')
        self.out = os.path.join(build_dir, 'out')

        self.config = {}
        self.config['extensions'] = ['sphinxcontrib.confluencebuilder']
        self.config['confluence_publish'] = False
        self.config['confluence_purge'] = True

        self._conf('confluence_parent_page',    'CB_PAR', DEFAULT_TEST_PARENT)
        self._conf('confluence_publish_prefix', 'CB_PFX')
        self._conf('confluence_server_pass',    'CB_PWD')
        self._conf('confluence_server_url',     'CB_URL', DEFAULT_TEST_URL)
        self._conf('confluence_server_user',    'CB_USR', DEFAULT_TEST_USER)
        self._conf('confluence_space_name',     'CB_SPC', DEFAULT_TEST_SPACE)

        if not self.config['confluence_server_pass']:
            key_filename = os.path.realpath(__file__)
            key_filename = os.path.dirname(key_filename)
            key_filename = os.path.join(key_filename, '..')
            key_filename = os.path.abspath(key_filename)
            key_filename = os.path.join(key_filename, DEFAULT_PUBLISH_KEY_FILE)
            if os.path.isfile(key_filename):
                with open(key_filename, 'r') as key_file:
                    self.config['confluence_server_pass'] = \
                        key_file.read().replace('\n', '')

            if not self.config['confluence_server_pass']:
                assert False, "No password provided to publish to instance."

        self.app = Sphinx(
            val_dir, None, self.out, doctree_dir, 'confluence', self.config)
        self.app.build(force_all=True)
        self.docnames = self.app.builder.env.found_docs

    def test_manual_publish(self):
        self.app.config['confluence_publish'] = True

        builder = ConfluenceBuilder(self.app)
        builder.init()
        for docname in self.docnames:
            ConfluenceLogger.info("\033[01mpublishing '%s'...\033[0m" % docname)
            output_filename = os.path.join(self.out, docname + '.conf')
            with open(output_filename, 'r') as output_file:
                output = output_file.read()
                builder.publish_doc(docname, output)
        builder.finish()

if __name__ == '__main__':
    sys.exit(unittest.main())
