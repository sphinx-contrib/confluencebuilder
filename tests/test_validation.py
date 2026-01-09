# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from pathlib import Path
from tests.lib import build_sphinx
from tests.lib import enable_sphinx_info
from tests.lib import prepare_conf
from tests.lib import prepare_dirs
from tests.lib import prepare_sphinx
import argparse
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
        cls.point_url = None

        # build configuration
        space_key = os.getenv(SPACE_ENV_KEY, DEFAULT_TEST_SPACE)
        cls.config = prepare_conf()
        cls.config['extensions'].append('sphinx.ext.ifconfig')
        cls.config['confluence_api_token'] = os.getenv(AUTH_ENV_KEY)
        cls.config['confluence_full_width'] = False
        cls.config['confluence_page_generation_notice'] = True
        cls.config['confluence_prev_next_buttons_location'] = 'both'
        cls.config['confluence_publish'] = True
        cls.config['confluence_publish_debug'] = 'deprecated'
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
        cls.test_version = os.getenv(TESTKEY_ENV_VERSION, DEFAULT_TEST_VERSION)

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
                '_entry_next',
            ]
            builder.state.register_title('_entry_next',
                'reStructuredText', None)
            return docnames
        config['confluence_navdocs_transform'] = navdocs_transform

        # track the initial publish point
        def capture_base_publish_point(app, point_url):
            cls.point_url = point_url

        # build/publish test base page
        with prepare_sphinx(dataset, config=config, out_dir=doc_dir) as app:
            app.connect('confluence-publish-point', capture_base_publish_point)
            app.build()

        # finalize configuration for tests
        cls.config['confluence_cleanup_purge'] = True
        cls.config['confluence_cleanup_from_root'] = True
        cls.config['confluence_root_homepage'] = False

    @classmethod
    def tearDownClass(cls):
        if cls.point_url:
            print()
            print()
            print('Validation publish point:', cls.point_url)
            print()
            print()

    def test_110_restructuredtext(self):
        self._test_restructuredtext()

    def test_120_sphinx(self):
        self._test_sphinx()

    def test_130_markdown(self):
        self._test_markdown()

    def test_140_extensions(self):
        self._test_extensions()

    def test_310_singleconfluence(self):
        config = self.config.clone()
        config['confluence_sourcelink'] = None
        config['confluence_title_overrides'] = {
            'index': 'Single Confluence',
        }

        dataset = self.datasets / 'restructuredtext'
        doc_dir = prepare_dirs('validation-set-rst-singleconfluence')

        build_sphinx(dataset, config=config, out_dir=doc_dir,
            builder='singleconfluence')

    def _test_restructuredtext(self):
        config = self.config.clone()
        config['confluence_sourcelink']['container'] += 'restructuredtext/'

        dataset = self.datasets / 'restructuredtext'
        doc_dir = prepare_dirs('validation-set-restructuredtext')

        # inject a navdoc to the header/footer start page
        def navdocs_transform(builder, docnames):
            builder.state.register_title(
                '_validation_prev', self.test_key, None)
            docnames.insert(0, '_validation_prev')
            builder.state.register_title(
                '_validation_next', 'Sphinx', None)
            docnames.append('_validation_next')
            return docnames
        config['confluence_navdocs_transform'] = navdocs_transform

        build_sphinx(dataset, config=config, out_dir=doc_dir)

    def _test_sphinx(self):
        config = self.config.clone()
        config['confluence_sourcelink']['container'] += 'sphinx/'

        dataset = self.datasets / 'sphinx'
        doc_dir = prepare_dirs('validation-set-sphinx')

        # inject a navdoc to the header/footer start page
        def navdocs_transform(builder, docnames):
            builder.state.register_title(
                '_validation_prev', 'Transition', None)
            docnames.insert(0, '_validation_prev')
            builder.state.register_title(
                '_validation_next', 'Markdown', None)
            docnames.append('_validation_next')
            return docnames
        config['confluence_navdocs_transform'] = navdocs_transform

        build_sphinx(dataset, config=config, out_dir=doc_dir)

    def _test_markdown(self):
        config = self.config.clone()
        config['confluence_sourcelink']['container'] += 'markdown/'
        config['extensions'].append('myst_parser')

        dataset = self.datasets / 'markdown'
        doc_dir = prepare_dirs('validation-set-markdown')

        # inject a navdoc to the header/footer start page
        def navdocs_transform(builder, docnames):
            builder.state.register_title(
                '_validation_prev', 'Version changed', None)
            docnames.insert(0, '_validation_prev')
            builder.state.register_title(
                '_validation_next', 'Extensions', None)
            docnames.append('_validation_next')
            return docnames
        config['confluence_navdocs_transform'] = navdocs_transform

        build_sphinx(dataset, config=config, out_dir=doc_dir)

    def _test_extensions(self):
        config = self.config.clone()
        config['confluence_sourcelink']['container'] += 'extensions/'
        config['extensions'].append('sphinx.ext.autodoc')
        config['extensions'].append('sphinx.ext.autosummary')
        config['extensions'].append('sphinx.ext.graphviz')
        config['extensions'].append('sphinx.ext.ifconfig')
        config['extensions'].append('sphinx.ext.inheritance_diagram')
        config['extensions'].append('sphinx.ext.linkcode')
        config['extensions'].append('sphinx.ext.todo')
        config['todo_include_todos'] = True
        config['todo_link_only'] = True

        def linkcode_resolve(domain, info):
            module = info.get('module', None)
            if module != 'linkcode_example':
                return None
            name = info.get('fullname', None)
            if not name:
                return None
            return f'https://example.org/src/{name}'
        config['linkcode_resolve'] = linkcode_resolve

        dataset = self.datasets / 'extensions'
        doc_dir = prepare_dirs('validation-set-extensions')

        # inject a navdoc to the header/footer start page
        def navdocs_transform(builder, docnames):
            builder.state.register_title(
                '_validation_prev', 'Markdown Table', None)
            docnames.insert(0, '_validation_prev')
            builder.state.register_title(
                '_validation_next', 'Single Confluence', None)
            docnames.append('_validation_next')
            return docnames
        config['confluence_navdocs_transform'] = navdocs_transform

        dataset = self.datasets / 'extensions'
        doc_dir = prepare_dirs('validation-set-extensions')
        sys.path.insert(0, str(dataset / 'src'))

        build_sphinx(dataset, config=config, out_dir=doc_dir)

        sys.path.pop(0)


def main():
    enable_sphinx_info()

    parser = argparse.ArgumentParser(prog=__name__,
        description='Atlassian Confluence Sphinx Extension Validation')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--verbose', '-v', action='store_true')

    # parse local argument and rebuild sys.argv with other arguments
    # which will be handled in `unittest.main`
    args, unknown_args = parser.parse_known_args(sys.argv[1:])
    sys.argv = sys.argv[:1] + unknown_args

    if args.debug or args.verbose:
        if 'SPHINX_VERBOSITY' not in os.environ:
            os.environ['SPHINX_VERBOSITY'] = '2'

    return unittest.main(failfast=True, verbosity=0)


if __name__ == '__main__':
    sys.exit(main())
