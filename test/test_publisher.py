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
from subprocess import check_output
import io
import os
import sys
import unittest

DEFAULT_TEST_URL = 'https://jdknight.atlassian.net/wiki'
DEFAULT_TEST_USER = 'sphinxcontrib-confluencebuilder'
DEFAULT_TEST_SPACE = 'confluencebuilder'
DEFAULT_TEST_PARENT = 'test-holder'
DEFAULT_PUBLISH_KEY_FILE = '.test_publish_key'

class TestConfluencePublisher(unittest.TestCase):
    is_automated = True
    single_docname = None

    @classmethod
    def _conf(self, key, env, default=None):
        self.config[key] = os.getenv(env, default)

    @classmethod
    def setUpClass(self):
        base_dir = os.path.dirname(os.path.realpath(__file__))
        val_dir = os.path.join(base_dir, 'validation-set')
        build_dir = os.path.join(base_dir, 'build')
        doctree_dir = os.path.join(build_dir, 'validation-doctree')
        self.out = os.path.join(build_dir, 'validation-out')

        self.config = {}
        self.config['extensions'] = ['sphinxcontrib.confluencebuilder']
        self.config['confluence_publish'] = False
        self.config['confluence_purge'] = not self.single_docname

        self._conf('confluence_parent_page',    'CB_PAR', DEFAULT_TEST_PARENT)
        self._conf('confluence_publish_prefix', 'CB_PFX')
        self._conf('confluence_server_pass',    'CB_PWD')
        self._conf('confluence_server_url',     'CB_URL', DEFAULT_TEST_URL)
        self._conf('confluence_server_user',    'CB_USR', DEFAULT_TEST_USER)
        self._conf('confluence_space_name',     'CB_SPC', DEFAULT_TEST_SPACE)

        if not self.is_automated:
            parent = self.config['confluence_parent_page']
            prefix = self.config['confluence_publish_prefix']

            parentValue = ""
            if parent:
                parentValue = " [%s]" % parent

            prefixValue = ""
            if prefix:
                prefixValue = " [%s]" % prefix

            print('')
            parent = input('Parent page to publish to' + parentValue + ': ')
            prefix = input('Page prefix value' + prefixValue + ': ')
            print('')

            if not parent:
                parent = self.config['confluence_parent_page']
            if not prefix:
                prefix = self.config['confluence_publish_prefix']

            print('Publish target]')
            print('            url:', self.config['confluence_server_url'])
            print('          space:', self.config['confluence_space_name'])
            print('    parent page:', parent)
            print('    page prefix:', prefix)
            print('')

            choice = input('Start publishing? [y/N] ').lower()
            if not choice == "y" and not choice == "yes":
                print('User has decided not to publish; exiting...')
                sys.exit(0)

            self.config['confluence_parent_page'] = parent
            self.config['confluence_publish_prefix'] = prefix

        if self.config['confluence_publish_prefix']:
            self.config['confluence_remove_title'] = False

        if not self.config['confluence_server_pass']:
            key_filename = os.path.realpath(__file__)
            key_filename = os.path.dirname(key_filename)
            key_filename = os.path.join(key_filename, '..')
            key_filename = os.path.abspath(key_filename)
            key_filename = os.path.join(key_filename, DEFAULT_PUBLISH_KEY_FILE)
            if os.path.isfile(key_filename):
                with io.open(key_filename, encoding='utf8') as key_file:
                    self.config['confluence_server_pass'] = \
                        key_file.read().replace('\n', '')

            if not self.config['confluence_server_pass']:
                assert False, "No password provided to publish to instance."

        try:
            source_revision = check_output(['git', 'rev-parse', 'HEAD'])
            source_revision = source_revision.decode('utf-8').splitlines()[0]
        except:
            source_revision = 'unknown'

        gencontents_file = os.path.join(val_dir, 'contents.rst')
        try:
            with io.open(gencontents_file, 'w', encoding='utf-8') as file:
                file.write(u'revision\n')
                file.write(u'========\n')
                file.write(u'\n')
                file.write(u'Revision: %s\n' % source_revision)
        except (IOError, OSError) as err:
            ConfluenceLogger.err("error generating file "
                "%s: %s" % (gencontents_file, err))

        self.app = Sphinx(
            val_dir, None, self.out, doctree_dir, 'confluence', self.config)
        self.app.build(force_all=True)
        self.docnames = self.app.builder.env.found_docs

    def test_manual_publish(self):
        self.app.config['confluence_publish'] = True

        builder = ConfluenceBuilder(self.app)
        builder.init()
        for docname in self.docnames:
            if self.single_docname and self.single_docname != docname:
                continue
            ConfluenceLogger.info("\033[01mpublishing '%s'...\033[0m" % docname)
            output_filename = os.path.join(self.out, docname + '.conf')
            with io.open(output_filename, encoding='utf8') as output_file:
                output = output_file.read()
                builder.publish_doc(docname, output)
        builder.finish()

if __name__ == '__main__':
    if '--doc' in sys.argv:
        idx = sys.argv.index('--doc')
        del sys.argv[idx]
        if idx < len(sys.argv):
            TestConfluencePublisher.single_docname = sys.argv[idx]
            del sys.argv[idx]
    if '--input' in sys.argv:
        TestConfluencePublisher.is_automated = False
        sys.argv.remove('--input')
    sys.exit(unittest.main())
