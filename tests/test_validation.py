# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2018-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from sphinxcontrib.confluencebuilder.exceptions import ConfluenceBadApiError
from tests.lib import buildSphinx
from tests.lib import enableSphinxStatus
from tests.lib import prepareConfiguration
from tests.lib import prepareDirectories
import os
import sys
import unittest

DEFAULT_TEST_DESC = 'test state'
DEFAULT_TEST_KEY = 'test-holder'
DEFAULT_TEST_SPACE = 'DEVELOP'
DEFAULT_TEST_URL = 'https://sphinxcontrib-confluencebuilder.atlassian.net/wiki/'
DEFAULT_TEST_USER = 'sphinxcontrib-confluencebuilder@jdknight.me'
AUTH_ENV_KEY = 'CONFLUENCE_AUTH'

class TestConfluenceValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        enableSphinxStatus()

        # build configuration
        cls.config = prepareConfiguration()
        cls.config['confluence_disable_notifications'] = True
        cls.config['confluence_page_hierarchy'] = True
        cls.config['confluence_parent_page'] = None
        cls.config['confluence_publish'] = True
        cls.config['confluence_space_name'] = DEFAULT_TEST_SPACE
        cls.config['confluence_server_url'] = DEFAULT_TEST_URL
        cls.config['confluence_server_user'] = DEFAULT_TEST_USER
        cls.config['confluence_timeout'] = 1
        cls.test_desc = DEFAULT_TEST_DESC
        cls.test_key = DEFAULT_TEST_KEY

        # configure ci authentication key (if set)
        cls.config['confluence_server_pass'] = os.getenv(AUTH_ENV_KEY)

        # overrides from user
        try:
            from validation_test_overrides import config_overrides
            cls.config.update(config_overrides)
        except ImportError:
            pass
        try:
            from validation_test_overrides import config_test_desc
            cls.test_desc = config_test_desc
        except ImportError:
            pass
        try:
            from validation_test_overrides import config_test_key
            cls.test_key = config_test_key
        except ImportError:
            pass

        # finalize
        cls.config['confluence_master_homepage'] = True
        cls.config['confluence_publish_prefix'] = ''
        cls.config['confluence_publish_postfix'] = ''
        cls.config['confluence_purge'] = False
        cls.config['rst_epilog'] = """
.. |test_key| replace:: {}
.. |test_desc| replace:: {}
""".format(cls.test_key, cls.test_desc)

        # find validate-sets base folder
        test_dir = os.path.dirname(os.path.realpath(__file__))
        cls.datasets = os.path.join(test_dir, 'validation-sets')

        # setup base structure
        dataset = os.path.join(cls.datasets, 'base')
        doc_dir, doctree_dir = prepareDirectories('validation-set-base')

        # build/publish test base page
        buildSphinx(dataset, doc_dir, doctree_dir, cls.config)

        # finalize configuration for tests
        cls.config['confluence_master_homepage'] = False
        cls.config['confluence_parent_page'] = cls.test_key
        cls.config['confluence_prev_next_buttons_location'] = 'both'
        cls.config['confluence_purge'] = True
        cls.config['confluence_purge_from_master'] = True

    def test_extensions(self):
        config = dict(self.config)
        config['extensions'].append('sphinx.ext.autodoc')
        config['extensions'].append('sphinx.ext.autosummary')
        config['extensions'].append('sphinx.ext.graphviz')
        config['extensions'].append('sphinx.ext.ifconfig')
        config['extensions'].append('sphinx.ext.inheritance_diagram')
        config['extensions'].append('sphinx.ext.todo')
        config['graphviz_output_format'] = 'svg'
        config['todo_include_todos'] = True
        config['todo_link_only'] = True

        dataset = os.path.join(self.datasets, 'extensions')
        doc_dir, doctree_dir = prepareDirectories('validation-set-extensions')
        sys.path.insert(0, os.path.join(dataset, 'src'))

        buildSphinx(dataset, doc_dir, doctree_dir, config)

        sys.path.pop(0)

    def test_header_footer(self):
        config = dict(self.config)

        dataset = os.path.join(self.datasets, 'header-footer')
        doc_dir, doctree_dir = prepareDirectories('validation-set-hf')

        config['confluence_header_file'] = os.path.join(dataset, 'header.tpl')
        config['confluence_footer_file'] = os.path.join(dataset, 'footer.tpl')

        buildSphinx(dataset, doc_dir, doctree_dir, config)

    def test_hierarchy(self):
        config = dict(self.config)
        config['confluence_max_doc_depth'] = 2
        config['confluence_page_hierarchy'] = True

        dataset = os.path.join(self.datasets, 'hierarchy')
        doc_dir, doctree_dir = prepareDirectories('validation-set-hierarchy')

        buildSphinx(dataset, doc_dir, doctree_dir, config)

    def test_nonjsonresponse(self):
        config = dict(self.config)
        config['confluence_server_url'] = 'https://example.com/'
        dataset = os.path.join(self.datasets, 'base')
        doc_dir, doctree_dir = prepareDirectories('validation-set-nonjsonresponse')

        with self.assertRaises(ConfluenceBadApiError):
            buildSphinx(dataset, doc_dir, doctree_dir, config)

    def test_standard_default(self):
        dataset = os.path.join(self.datasets, 'standard')
        doc_dir, doctree_dir = prepareDirectories('validation-set-standard')

        buildSphinx(dataset, doc_dir, doctree_dir, self.config)

    def test_standard_macro_restricted(self):
        config = dict(self.config)

        dataset = os.path.join(self.datasets, 'standard')
        doc_dir, doctree_dir = prepareDirectories('validation-set-standard-nm')

        config['confluence_adv_restricted'] = [
            'anchor',
            'children',
            'code',
            'info',
            'viewfile',
            'jira'
        ]
        config['confluence_header_file'] = os.path.join(dataset, 'no-macro.tpl')
        config['confluence_publish_postfix'] = ' (nomacro)'

        buildSphinx(dataset, doc_dir, doctree_dir, config)

if __name__ == '__main__':
    sys.exit(unittest.main(verbosity=0))
