# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from pathlib import Path
from sphinxcontrib.confluencebuilder.state import ConfluenceState
from tests.lib import build_sphinx
from tests.lib import enable_sphinx_info
from tests.lib import prepare_conf
from tests.lib import prepare_dirs
import os
import sys
import unittest

DEFAULT_TEST_DESC = 'test state'
DEFAULT_TEST_KEY = 'test-holder'
DEFAULT_TEST_SPACE = 'DEVELOP'
DEFAULT_TEST_URL = 'https://sphinxcontrib-confluencebuilder.atlassian.net/wiki/'
DEFAULT_TEST_USER = 'sphinxcontrib-confluencebuilder@jdknight.me'
DEFAULT_TEST_VERSION = 'main'
AUTH_ENV_KEY = 'CONFLUENCE_AUTH'
SPACE_ENV_KEY = 'CONFLUENCE_SPACE'
TESTDESC_ENV_KEY = 'CONFLUENCE_TEST_DESC'
TESTKEY_ENV_KEY = 'CONFLUENCE_TEST_KEY'
TESTKEY_ENV_VERSION = 'CONFLUENCE_TEST_VERSION'


class TestConfluenceValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        enable_sphinx_info()

        # build configuration
        space_key = os.getenv(SPACE_ENV_KEY, DEFAULT_TEST_SPACE)
        cls.config = prepare_conf()
        cls.config['extensions'].append('sphinx.ext.ifconfig')
        cls.config['confluence_disable_notifications'] = True
        cls.config['confluence_full_width'] = False
        cls.config['confluence_page_hierarchy'] = True
        cls.config['confluence_page_generation_notice'] = True
        cls.config['confluence_parent_page'] = None
        cls.config['confluence_prev_next_buttons_location'] = 'both'
        cls.config['confluence_publish'] = True
        cls.config['confluence_publish_debug'] = 'deprecated'
        cls.config['confluence_server_pass'] = os.getenv(AUTH_ENV_KEY)
        cls.config['confluence_server_url'] = DEFAULT_TEST_URL
        cls.config['confluence_server_user'] = DEFAULT_TEST_USER
        cls.config['confluence_sourcelink'] = {
            'type': 'github',
            'owner': 'sphinx-contrib',
            'repo': 'confluencebuilder',
            'container': 'tests/validation-sets/',
        }
        cls.config['confluence_space_key'] = space_key
        cls.config['confluence_timeout'] = 30
        cls.config['imgmath_font_size'] = 14
        cls.config['imgmath_image_format'] = 'svg'
        cls.config['imgmath_use_preview'] = True
        cls.config['manpages_url'] = 'https://example.org/{path}'
        cls.test_desc = os.getenv(TESTDESC_ENV_KEY, DEFAULT_TEST_DESC)
        cls.test_key = os.getenv(TESTKEY_ENV_KEY, DEFAULT_TEST_KEY)
        cls.test_version = os.getenv(TESTKEY_ENV_KEY, DEFAULT_TEST_VERSION)

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
        try:
            from validation_test_overrides import config_test_version
            cls.test_version = config_test_version
        except ImportError:
            pass

        # finalize
        if cls.config['confluence_space_key'].startswith('~'):
            cls.config['confluence_root_homepage'] = False
        cls.config['confluence_publish_prefix'] = ''
        cls.config['confluence_publish_postfix'] = ''
        cls.config['confluence_cleanup_archive'] = False
        cls.config['confluence_sourcelink']['version'] = cls.test_version
        cls.config['rst_epilog'] = f'''
.. |test_key| replace:: {cls.test_key}
.. |test_desc| replace:: {cls.test_desc}
'''

        # find validate-sets base folder
        test_dir = Path(__file__).parent.resolve()
        cls.datasets = test_dir / 'validation-sets'

        # setup base structure
        dataset = cls.datasets / 'base'
        doc_dir = prepare_dirs('validation-set-base')

        config = cls.config.clone()
        config['confluence_sourcelink']['container'] += 'base/'

        # inject a navdoc from the "standard" start page
        def navdocs_transform(builder, docnames):
            docnames = [
                'index',
                'editor_v1',
                '_entry_v1_next',
                '_entry_v2_prev',
                'editor_v2',
                '_entry_v2_next',
            ]
            builder.state.register_title('_entry_v1_next',
                'reStructuredText', None)
            builder.state.register_title('_entry_v2_prev',
                'sphinx.ext.todo', None)
            builder.state.register_title('_entry_v2_next',
                'reStructuredText (Fabric)', None)
            return docnames
        config['confluence_navdocs_transform'] = navdocs_transform

        # build/publish test base page
        build_sphinx(dataset, config=config, out_dir=doc_dir)

        # track root pages for editors to publish content into
        cls.editor_root = {
            'v1': ConfluenceState.upload_id('editor_v1'),
            'v2': ConfluenceState.upload_id('editor_v2'),
        }

        # finalize configuration for tests
        cls.config['confluence_cleanup_purge'] = True
        cls.config['confluence_cleanup_from_root'] = True
        cls.config['confluence_root_homepage'] = False

    def _prepare_editor(self, editor):
        display_name = ' (Fabric)' if editor == 'v2' else None

        config = self.config.clone()
        config['confluence_editor'] = editor
        config['confluence_parent_page'] = self.editor_root[editor]
        config['confluence_publish_postfix'] = display_name

        # always force png since svgs do not look nice in v2
        if editor == 'v2':
            config['imgmath_image_format'] = 'png'

        return config

    def test_110_restructuredtext_v1(self):
        self._test_restructuredtext('v1')

    def test_120_sphinx_v1(self):
        self._test_sphinx('v1')

    def test_130_markdown(self):
        self._test_markdown('v1')

    def test_140_extensions(self):
        self._test_extensions('v1')

    def test_210_restructuredtext_v2(self):
        self._test_restructuredtext('v2')

    def test_220_sphinx_v2(self):
        self._test_sphinx('v2')

    def test_230_markdown(self):
        self._test_markdown('v2')

    def test_240_extensions(self):
        self._test_extensions('v2')

    def _test_restructuredtext(self, editor):
        config = self._prepare_editor(editor)
        config['confluence_sourcelink']['container'] += 'restructuredtext/'

        dataset = self.datasets / 'restructuredtext'
        doc_dir = prepare_dirs('validation-set-restructuredtext-' + editor)

        # inject a navdoc to the header/footer start page
        def navdocs_transform(builder, docnames):
            if editor == 'v2':
                builder.state.register_title(
                    '_validation_prev', 'Fabric editor', None)
                docnames.insert(0, '_validation_prev')
                builder.state.register_title(
                    '_validation_next', 'Sphinx (Fabric)', None)
                docnames.append('_validation_next')
            else:
                builder.state.register_title(
                    '_validation_prev', 'Default editor', None)
                docnames.insert(0, '_validation_prev')
                builder.state.register_title(
                    '_validation_next', 'Sphinx', None)
                docnames.append('_validation_next')
            return docnames
        config['confluence_navdocs_transform'] = navdocs_transform

        build_sphinx(dataset, config=config, out_dir=doc_dir)

    def _test_sphinx(self, editor):
        config = self._prepare_editor(editor)
        config['confluence_sourcelink']['container'] += 'sphinx/'

        dataset = self.datasets / 'sphinx'
        doc_dir = prepare_dirs('validation-set-sphinx-' + editor)

        # inject a navdoc to the header/footer start page
        def navdocs_transform(builder, docnames):
            if editor == 'v2':
                builder.state.register_title(
                    '_validation_prev', 'Transition (Fabric)', None)
                docnames.insert(0, '_validation_prev')
                builder.state.register_title(
                    '_validation_next', 'Markdown (Fabric)', None)
                docnames.append('_validation_next')
            else:
                builder.state.register_title(
                    '_validation_prev', 'Transition', None)
                docnames.insert(0, '_validation_prev')
                builder.state.register_title(
                    '_validation_next', 'Markdown', None)
                docnames.append('_validation_next')
            return docnames
        config['confluence_navdocs_transform'] = navdocs_transform

        build_sphinx(dataset, config=config, out_dir=doc_dir)

    def _test_markdown(self, editor):
        config = self._prepare_editor(editor)
        config['confluence_sourcelink']['container'] += 'markdown/'
        config['extensions'].append('myst_parser')

        dataset = self.datasets / 'markdown'
        doc_dir = prepare_dirs('validation-set-markdown-' + editor)

        # inject a navdoc to the header/footer start page
        def navdocs_transform(builder, docnames):
            if editor == 'v2':
                builder.state.register_title(
                    '_validation_prev', 'Version changed (Fabric)', None)
                docnames.insert(0, '_validation_prev')
                builder.state.register_title(
                    '_validation_next', 'Extensions (Fabric)', None)
                docnames.append('_validation_next')
            else:
                builder.state.register_title(
                    '_validation_prev', 'Version changed', None)
                docnames.insert(0, '_validation_prev')
                builder.state.register_title(
                    '_validation_next', 'Extensions', None)
                docnames.append('_validation_next')
            return docnames
        config['confluence_navdocs_transform'] = navdocs_transform

        build_sphinx(dataset, config=config, out_dir=doc_dir)

    def _test_extensions(self, editor):
        config = self._prepare_editor(editor)
        config['confluence_sourcelink']['container'] += 'extensions/'
        config['extensions'].append('sphinx.ext.autodoc')
        config['extensions'].append('sphinx.ext.autosummary')
        config['extensions'].append('sphinx.ext.graphviz')
        config['extensions'].append('sphinx.ext.ifconfig')
        config['extensions'].append('sphinx.ext.inheritance_diagram')
        config['extensions'].append('sphinx.ext.todo')
        config['todo_include_todos'] = True
        config['todo_link_only'] = True

        # always force png since svgs do not look nice in v2
        if editor == 'v2':
            config['imgmath_image_format'] = 'png'
        else:
            config['graphviz_output_format'] = 'svg'

        dataset = self.datasets / 'extensions'
        doc_dir = prepare_dirs('validation-set-extensions-' + editor)

        # inject a navdoc to the header/footer start page
        def navdocs_transform(builder, docnames):
            if editor == 'v2':
                builder.state.register_title(
                    '_validation_prev', 'Markdown Table (Fabric)', None)
                docnames.insert(0, '_validation_prev')
            else:
                builder.state.register_title(
                    '_validation_prev', 'Markdown Table', None)
                docnames.insert(0, '_validation_prev')
                builder.state.register_title(
                    '_validation_next', 'Fabric editor', None)
                docnames.append('_validation_next')
            return docnames
        config['confluence_navdocs_transform'] = navdocs_transform

        dataset = self.datasets / 'extensions'
        doc_dir = prepare_dirs('validation-set-extensions')
        sys.path.insert(0, str(dataset / 'src'))

        build_sphinx(dataset, config=config, out_dir=doc_dir)

        sys.path.pop(0)


if __name__ == '__main__':
    sys.exit(unittest.main(failfast=True, verbosity=0))
