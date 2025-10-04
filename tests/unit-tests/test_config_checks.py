# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from pathlib import Path
from requests.auth import AuthBase
from requests.auth import HTTPDigestAuth
from sphinx.environment import BuildEnvironment
from sphinx.errors import SphinxWarning
from sphinxcontrib.confluencebuilder.builder import ConfluenceBuilder
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluenceConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluenceDefaultTableWidthError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluencePageGenerationNoticeConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluencePermitRawHtmlConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluencePublishCleanupConflictConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluenceSourcelinkTypeConfigError
from tests.lib import EXT_NAME
from tests.lib import mock_getpass
from tests.lib import mock_input
from tests.lib import prepare_conf
from tests.lib import prepare_sphinx
import unittest


class TestConfluenceConfigChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = Path(__file__).parent.resolve()
        cls.dataset = cls.test_dir / 'datasets' / 'common'
        cls.dummy_exists = cls.test_dir / 'assets' / 'dummy'
        cls.dummy_missing = cls.test_dir / 'assets' / 'missing'

        cls.minimal_config = {'extensions': EXT_NAME}

    def run(self, result=None):
        # unique configuration each run to avoid copying it in each test
        self.config = prepare_conf()

        super().run(result)

    def _prepare_valid_publish(self):
        self.config['confluence_publish'] = True
        self.config['confluence_server_url'] = \
            'https://intranet-wiki.example.com/'
        self.config['confluence_space_key'] = 'DUMMY'

    def _try_config(self, config=None, edefs=None, relax=None, dataset=None):
        config = config if config else self.minimal_config
        dataset = dataset if dataset else self.dataset

        with prepare_sphinx(dataset,
                config=config, extra_config=edefs, relax=relax) as app:
            env = BuildEnvironment(app)
            builder = ConfluenceBuilder(app, env)

            class MockedPublisher:
                def init(self, config, cloud=None):
                    pass

                def connect(self):
                    pass

                def disconnect(self):
                    pass
            builder.publisher = MockedPublisher()

            for k, v in self.config.items():
                setattr(builder.config, k, v)

            builder.init()

    def test_config_check_api_token(self):
        self.config['confluence_api_token'] = 'dummy'  # noqa: S105
        self._try_config()

        # enable publishing enabled checks
        self._prepare_valid_publish()

        # without `confluence_api_token` should throw an error
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_server_user'] = 'dummy'
        self._try_config()

    def test_config_check_ask_password(self):
        print()  # space out ask output if an unbuffered run

        self.config['confluence_ask_password'] = True
        self._try_config()

        # enable publishing enabled checks
        self._prepare_valid_publish()

        with mock_getpass('password'):
            with self.assertRaises(ConfluenceConfigError):
                self._try_config()

        self.config['confluence_ask_user'] = True

        with mock_input('username'), mock_getpass('password'):
            self._try_config()

        self.config['confluence_ask_user'] = False
        self.config['confluence_server_user'] = 'username'

        with mock_getpass('password'):
            self._try_config()

        with mock_getpass(''):
            with self.assertRaises(ConfluenceConfigError):
                self._try_config()

        del self.config['confluence_ask_password']
        del self.config['confluence_ask_user']
        self.config['confluence_server_user'] = 'username'

        defines = {
            'confluence_ask_password': '1',
        }
        with mock_getpass(''):
            with self.assertRaises(ConfluenceConfigError):
                self._try_config(edefs=defines)

        defines = {
            'confluence_ask_password': '1',
        }
        with mock_getpass('password'):
            self._try_config(edefs=defines)

        defines = {
            'confluence_ask_password': '0',
        }
        with mock_getpass(''):
            self._try_config(edefs=defines)

        defines = {
            'confluence_ask_password': '',  # empty to "unset"
        }
        with mock_getpass(''):
            self._try_config(edefs=defines)

    def test_config_check_ask_user(self):
        print()  # space out ask output if an unbuffered run

        self.config['confluence_ask_user'] = True
        self._try_config()

        # enable publishing enabled checks
        self._prepare_valid_publish()

        with mock_input('username'):
            self._try_config()

        with mock_input(''):
            with self.assertRaises(ConfluenceConfigError):
                self._try_config()

        # accepting default username
        self.config['confluence_server_user'] = 'username'
        with mock_input(''):
            self._try_config()

        del self.config['confluence_ask_user']
        del self.config['confluence_server_user']

        defines = {
            'confluence_ask_user': '1',
        }
        with mock_input(''):
            with self.assertRaises(ConfluenceConfigError):
                self._try_config(edefs=defines)

        defines = {
            'confluence_ask_user': '1',
        }
        with mock_input('username'):
            self._try_config(edefs=defines)

        defines = {
            'confluence_ask_user': '0',
        }
        with mock_input(''):
            self._try_config(edefs=defines)

        defines = {
            'confluence_ask_user': '',  # empty to "unset"
        }
        with mock_input(''):
            self._try_config(edefs=defines)

    def test_config_check_additional_mime_types(self):
        self.config['confluence_additional_mime_types'] = [
            'image/ief',
            'image/tiff',
        ]
        self._try_config()

        self.config['confluence_additional_mime_types'] = 'image/tiff'
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_additional_mime_types'] = ['image tiff']
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_additional_mime_types'] = ['image/unknown-type']
        with self.assertRaises(SphinxWarning):
            self._try_config()

    def test_config_check_ca_cert(self):
        valid_cert_dir = self.test_dir
        valid_cert_file = self.dummy_exists
        missing_cert = self.dummy_missing

        self.config['confluence_ca_cert'] = valid_cert_dir
        self._try_config()

        self.config['confluence_ca_cert'] = str(valid_cert_dir)
        self._try_config()

        self.config['confluence_ca_cert'] = valid_cert_file
        self._try_config()

        self.config['confluence_ca_cert'] = str(valid_cert_file)
        self._try_config()

        self.config['confluence_ca_cert'] = missing_cert
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_ca_cert'] = str(missing_cert)
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

    def test_config_check_cleanup_conflict(self):
        # enable publishing enabled checks
        self._prepare_valid_publish()

        self.config['confluence_cleanup_archive'] = True
        self.config['confluence_cleanup_purge'] = True
        with self.assertRaises(ConfluencePublishCleanupConflictConfigError):
            self._try_config()

    def test_config_check_client_cert(self):
        valid_cert = self.dummy_exists
        missing_cert = self.dummy_missing

        self.config['confluence_client_cert'] = valid_cert
        self._try_config()

        self.config['confluence_client_cert'] = str(valid_cert)
        self._try_config()

        self.config['confluence_client_cert'] = (valid_cert, valid_cert)
        self._try_config()

        self.config['confluence_client_cert'] = missing_cert
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_client_cert'] = str(missing_cert)
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_client_cert'] = (valid_cert, missing_cert)
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_client_cert'] = (missing_cert, valid_cert)
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        # too many
        self.config['confluence_client_cert'] = \
            (valid_cert, valid_cert, valid_cert)
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

    def test_config_check_cert_pass(self):
        self.config['confluence_client_cert_pass'] = 'dummy'  # noqa: S105
        self._try_config()

    def test_config_check_cleanup_purge_mode(self):
        self.config['confluence_cleanup_search_mode'] = 'direct'
        self._try_config()

        self.config['confluence_cleanup_search_mode'] = 'direct-aggressive'
        self._try_config()

        self.config['confluence_cleanup_search_mode'] = 'search'
        self._try_config()

        self.config['confluence_cleanup_search_mode'] = 'search-aggressive'
        self._try_config()

        self.config['confluence_cleanup_search_mode'] = 'invalid'
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

    def test_config_check_code_block_theme(self):
        self.config['confluence_code_block_theme'] = True
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_code_block_theme'] = 'invalid'
        with self.assertRaises(SphinxWarning):
            self._try_config()

    def test_config_check_default_alignment(self):
        self.config['confluence_default_alignment'] = 'left'
        self._try_config()

        self.config['confluence_default_alignment'] = 'center'
        self._try_config()

        self.config['confluence_default_alignment'] = 'right'
        self._try_config()

        self.config['confluence_default_alignment'] = 'invalid'
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

    def test_config_check_disable_ssl_validation(self):
        self.config['confluence_disable_ssl_validation'] = True
        with self.assertRaises(SphinxWarning):
            self._try_config()

    def test_config_check_domain_indices(self):
        self.config['confluence_domain_indices'] = True
        self._try_config()

        self.config['confluence_domain_indices'] = []
        self._try_config()

        self.config['confluence_domain_indices'] = [
            'js-modindex',
            'py-modindex',
        ]
        self._try_config()

        self.config['confluence_domain_indices'] = 'py-modindex'
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_domain_indices'] = [
            None,
        ]
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

    def test_config_check_editor(self):
        self.config['confluence_editor'] = None
        self._try_config()

        self.config['confluence_editor'] = 'v1'
        self._try_config()

        self.config['confluence_editor'] = 'v2'
        self._try_config()

        self.config['confluence_editor'] = 2
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_editor'] = 'some-value'
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_adv_permit_editor'] = True
        with self.assertRaises(SphinxWarning):
            self._try_config()

    def test_config_check_emptyconfig(self):
        # default state of this extension with a builder should be a valid
        # configuration state; documentation should be generated (with no
        # attempt at publishing)
        self._try_config()

    def test_config_check_file_suffix(self):
        self.config['confluence_file_suffix'] = '.conf'
        self._try_config()

        self.config['confluence_file_suffix'] = '.'
        with self.assertRaises(SphinxWarning):
            self._try_config()

    def test_config_check_footer_file(self):
        valid_footer = self.dummy_exists
        missing_footer = self.dummy_missing

        self.config['confluence_footer_file'] = valid_footer
        self._try_config()

        self.config['confluence_footer_file'] = str(valid_footer)
        self._try_config()

        self.config['confluence_footer_file'] = missing_footer
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_footer_file'] = str(missing_footer)
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        relbase = '../../templates/'
        self.config['confluence_footer_file'] = relbase + 'sample-footer.tpl'
        self._try_config()

    def test_config_check_global_labels(self):
        self.config['confluence_global_labels'] = ['label-a', 'label-b']
        self._try_config()

        self.config['confluence_global_labels'] = 'label-a label-b'
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

    def test_config_check_header_file(self):
        valid_header = self.dummy_exists
        missing_header = self.dummy_missing

        self.config['confluence_header_file'] = valid_header
        self._try_config()

        self.config['confluence_header_file'] = str(valid_header)
        self._try_config()

        self.config['confluence_header_file'] = missing_header
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_header_file'] = str(missing_header)
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        relbase = '../../templates/'
        self.config['confluence_header_file'] = relbase + 'sample-header.tpl'
        self._try_config()

    def test_config_check_confluence_default_table_width(self):
        self.config['confluence_default_table_width'] = 123456
        self._try_config()

        self.config['confluence_default_table_width'] = '123456'
        self._try_config()

        self.config['confluence_default_table_width'] = '123456 em'
        self._try_config()

        self.config['confluence_default_table_width'] = '123456mm'
        self._try_config()

        self.config['confluence_default_table_width'] = '123456 px'
        self._try_config()

        self.config['confluence_default_table_width'] = 'MyPage'
        self._try_config()

        self.config['confluence_default_table_width'] = '123456%'
        with self.assertRaises(ConfluenceDefaultTableWidthError):
            self._try_config()

        self.config['confluence_default_table_width'] = 0
        with self.assertRaises(ConfluenceDefaultTableWidthError):
            self._try_config()

        self.config['confluence_default_table_width'] = -123456
        with self.assertRaises(ConfluenceDefaultTableWidthError):
            self._try_config()

    def test_config_check_confluence_html_macro(self):
        self.config['confluence_html_macro'] = ''
        self._try_config()

        self.config['confluence_html_macro'] = 'dummy'
        self._try_config()

        self.config['confluence_html_macro'] = 1
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

    def test_config_check_jira_servers(self):
        self.config['confluence_jira_servers'] = {}
        self._try_config()

        self.config['confluence_jira_servers'] = {
            'server-1': {
                'id': '92d94d0e-ac8b-4f2e-92a5-2217ad88e5f2',
                'name': 'MyAwesomeServer',
            },
        }
        self._try_config()

        self.config['confluence_jira_servers'] = []
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_jira_servers'] = {
            None: {
                'id': '92d94d0e-ac8b-4f2e-92a5-2217ad88e5f2',
                'name': 'MyAwesomeServer',
            },
        }
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_jira_servers'] = {
            'server-1': None,
        }
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_jira_servers'] = {
            'server-1': {},
        }
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_jira_servers'] = {
            'server-1': {
                'id': '92d94d0e-ac8b-4f2e-92a5-2217ad88e5f2',
            },
        }
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_jira_servers'] = {
            'server-1': {
                'name': 'MyAwesomeServer',
            },
        }
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

    def test_config_check_lang_transform(self):
        self.config['confluence_lang_overrides'] = {
            'key': 'value',
        }
        self._try_config()

        def mock_transform(lang):
            return 'default'

        self.config['confluence_lang_overrides'] = mock_transform
        self._try_config(relax=True)
        # relax: since using transform is deprecated and will generate a warning

        self.config['confluence_lang_overrides'] = 'invalid'
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

    def test_config_check_latex_macro(self):
        self.config['confluence_latex_macro'] = 'macro-name'
        self._try_config()

        self.config['confluence_latex_macro'] = {
            'block-macro': 'block-macro-name',
            'inline-macro': 'inline-macro-name',
        }
        self._try_config()

        self.config['confluence_latex_macro'] = {
            'block-macro': 'block-macro-name',
            'inline-macro': 'inline-macro-name',
            'inline-macro-param': 'inline-macro-parameter',
        }
        self._try_config()

        self.config['confluence_latex_macro'] = {
            'block-macro': 'block-macro-name',
        }
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_latex_macro'] = {
            'inline-macro': 'inline-macro-name',
        }
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_latex_macro'] = {
            'block-macro': 'block-macro-name',
            'inline-macro': None,
        }
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_latex_macro'] = {
            'block-macro': None,
            'inline-macro': 'inline-macro-name',
        }
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

    def test_config_check_link_suffix(self):
        self.config['confluence_link_suffix'] = '.conf'
        self._try_config()

    def test_config_check_mentions(self):
        self.config['confluence_mentions'] = {}
        self._try_config()

        self.config['confluence_mentions'] = {
            'key1': 'myuser',
            'key2': 'b9aaf35e80441f415c3a3d3c53695d0e',
            'key3': '3c5369:fa8b5c24-17f8-4340-b73e-50d383307c59',
        }
        self._try_config()

        self.config['confluence_mentions'] = 'some-value'
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_mentions'] = {
            'key': None,
        }
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_mentions'] = {
            'key': 123,
        }
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

    def test_config_check_page_generation_notice(self):
        self.config['confluence_page_generation_notice'] = True
        self._try_config()

        self.config['confluence_page_generation_notice'] = False
        self._try_config()

        self.config['confluence_page_generation_notice'] = ''
        self._try_config()

        self.config['confluence_page_generation_notice'] = 'message'
        self._try_config()

        self.config['confluence_page_generation_notice'] = [1, 2, 3]
        with self.assertRaises(ConfluencePageGenerationNoticeConfigError):
            self._try_config()

    def test_config_check_parent_page(self):
        self.config['confluence_parent_page'] = 'dummy'
        self._try_config()

        self.config['confluence_parent_page'] = '123456'
        self._try_config()

        self.config['confluence_parent_page'] = 456789
        self._try_config()

        self.config['confluence_parent_page'] = 0
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_parent_page'] = -123456
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

    def test_config_check_parent_page_id_check(self):
        # enable publishing enabled checks
        self._prepare_valid_publish()

        # without `confluence_parent_page` should throw a error
        self.config['confluence_parent_page_id_check'] = 123456
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_parent_page'] = 'dummy'
        with self.assertRaises(SphinxWarning):
            self._try_config()

        self.config['confluence_parent_page_id_check'] = '123456'
        with self.assertRaises(SphinxWarning):
            self._try_config()

        self.config['confluence_parent_page_id_check'] = 0
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_parent_page_id_check'] = -123456
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

    def test_config_check_page_search_mode(self):
        self.config['confluence_page_search_mode'] = ''
        self._try_config()

        self.config['confluence_page_search_mode'] = 'default'
        self._try_config()

        self.config['confluence_page_search_mode'] = 'content'
        self._try_config()

        self.config['confluence_page_search_mode'] = 'search'
        self._try_config()

        self.config['confluence_page_search_mode'] = 'invalid'
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

    def test_config_check_permit_raw_html(self):
        self.config['confluence_permit_raw_html'] = True
        self._try_config()

        self.config['confluence_permit_raw_html'] = False
        self._try_config()

        self.config['confluence_permit_raw_html'] = ''
        self._try_config()

        self.config['confluence_permit_raw_html'] = 'sample-macro'
        self._try_config()

        self.config['confluence_permit_raw_html'] = [1, 2, 3]
        with self.assertRaises(ConfluencePermitRawHtmlConfigError):
            self._try_config()

    def test_config_check_prev_next_buttons_location(self):
        self.config['confluence_prev_next_buttons_location'] = 'bottom'
        self._try_config()

        self.config['confluence_prev_next_buttons_location'] = 'both'
        self._try_config()

        self.config['confluence_prev_next_buttons_location'] = 'top'
        self._try_config()

        self.config['confluence_prev_next_buttons_location'] = 'invalid'
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

    def test_config_check_publish(self):
        # stock configuration should need more than just the publish flag
        self.config['confluence_publish'] = True
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

    def test_config_check_publish_debug(self):
        self.config['confluence_publish_debug'] = ''
        self._try_config()

        self.config['confluence_publish_debug'] = 'urllib3'
        self._try_config()

        self.config['confluence_publish_debug'] = 'unknown-entry'
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_publish_debug'] = [1, 2, 3]
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_publish_debug'] = True
        with self.assertRaises(SphinxWarning):
            self._try_config()

    def test_config_check_publish_delay(self):
        self.config['confluence_publish_delay'] = 0.3
        self._try_config()

        self.config['confluence_publish_delay'] = 1
        self._try_config()

        self.config['confluence_publish_delay'] = '0.7'
        self._try_config()

        self.config['confluence_publish_delay'] = -1
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_publish_delay'] = 'one-hour'
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

    def test_config_check_publish_headers(self):
        self.config['confluence_publish_headers'] = {}
        self._try_config()

        self.config['confluence_publish_headers'] = {
            'CUSTOM_HEADER': 'some-value',
            'another-header': 'another-value',
        }
        self._try_config()

        self.config['confluence_publish_headers'] = {
            'good-key-bad-value': None,
        }
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_publish_headers'] = {
            123: 'bad-key-good-value',
        }
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

    def test_config_check_publish_list(self):
        dataset = self.test_dir / 'datasets' / 'publish-set'
        assets_dir = self.test_dir / 'assets'
        invalid_list = assets_dir / 'sample-invalid-publish-list'
        missing_list = self.dummy_missing
        valid_list = assets_dir / 'sample-valid-publish-list'

        options = [
            'confluence_publish_allowlist',
            'confluence_publish_denylist',
        ]

        for option in options:
            # empty value (None; ignore state)
            self.config[option] = None
            self._try_config(dataset=dataset)

            # empty value (list; no publish or no denied state)
            self.config[option] = []
            self._try_config(dataset=dataset)

            # document list with valid entry
            self.config[option] = ['doc-a']
            self._try_config(dataset=dataset)

            # document list with valid entry (in folder)
            self.config[option] = ['sub/doc-b']
            self._try_config(dataset=dataset)

            # explicitly force unicode strings to help verify python 2.x series
            # dealing with unicode strings inside the document subset
            self.config[option] = ['doc-c']
            self._try_config(dataset=dataset)

            # file with a valid document list
            self.assertTrue(valid_list.is_file())
            self.config[option] = valid_list
            self._try_config(dataset=dataset)

            self.config[option] = str(valid_list)
            self._try_config(dataset=dataset)

            # list with invalid content
            self.config[option] = [True, False]
            with self.assertRaises(ConfluenceConfigError):
                self._try_config(dataset=dataset)

            # missing document
            self.config[option] = ['missing']
            with self.assertRaises(ConfluenceConfigError):
                self._try_config(dataset=dataset)

            # use of file extension
            self.config[option] = ['index.rst']
            with self.assertRaises(ConfluenceConfigError):
                self._try_config(dataset=dataset)

            # file with invalid document list
            self.assertTrue(invalid_list.is_file())
            self.config[option] = invalid_list
            with self.assertRaises(ConfluenceConfigError):
                self._try_config(dataset=dataset)

            self.config[option] = str(invalid_list)
            with self.assertRaises(ConfluenceConfigError):
                self._try_config(dataset=dataset)

            # missing file
            self.assertFalse(missing_list.is_file())
            self.config[option] = missing_list
            with self.assertRaises(ConfluenceConfigError):
                self._try_config(dataset=dataset)

            self.config[option] = str(missing_list)
            with self.assertRaises(ConfluenceConfigError):
                self._try_config(dataset=dataset)

            # cleanup
            self.config[option] = None

            # enumalate command line empty string to unset (valid)
            config = dict(self.minimal_config)
            config[option] = ''
            self._try_config(config=config, dataset=dataset)

            # enumalate command line csv string to list (valid)
            config = dict(self.minimal_config)
            config[option] = 'doc-a,doc-c'
            self._try_config(config=config, dataset=dataset)

            # enumalate command line csv string to list (invalid)
            config = dict(self.minimal_config)
            config[option] = 'doc-a2,doc-c'
            with self.assertRaises(ConfluenceConfigError):
                self._try_config(config=config, dataset=dataset)

    def test_config_check_publish_orphan_container(self):
        # enable publishing enabled checks
        self._prepare_valid_publish()

        self.config['confluence_publish_orphan_container'] = 0
        self._try_config()

        self.config['confluence_publish_orphan_container'] = 123456
        self._try_config()

        self.config['confluence_publish_orphan_container'] = '123456'
        self._try_config()

        self.config['confluence_publish_orphan_container'] = -123456
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

    def test_config_check_publish_override_api_prefix(self):
        self.config['confluence_publish_override_api_prefix'] = {}
        self._try_config()

        self.config['confluence_publish_override_api_prefix'] = {
            'v1': 'override1/',
            'v2': 'override2/',
        }
        self._try_config()

        self.config['confluence_publish_override_api_prefix'] = {
            'v2': None,
        }
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

    def test_config_check_publish_postfix(self):
        self.config['confluence_publish_postfix'] = ''
        self._try_config()

        self.config['confluence_publish_postfix'] = 'dummy'
        self._try_config()

    def test_config_check_publish_prefix(self):
        self.config['confluence_publish_prefix'] = ''
        self._try_config()

        self.config['confluence_publish_prefix'] = 'dummy'
        self._try_config()

    def test_config_check_publish_retry_attempts(self):
        self.config['confluence_publish_retry_attempts'] = 10
        self._try_config()

        self.config['confluence_publish_retry_attempts'] = '999'
        self._try_config()

        self.config['confluence_publish_retry_attempts'] = -1
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

    def test_config_check_publish_retry_duration(self):
        self.config['confluence_publish_retry_duration'] = 2
        self._try_config()

        self.config['confluence_publish_retry_duration'] = '2'
        self._try_config()

        self.config['confluence_publish_retry_duration'] = -1
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

    def test_config_check_publish_root(self):
        # enable publishing enabled checks
        self._prepare_valid_publish()

        self.config['confluence_publish_root'] = 123456
        self._try_config()

        self.config['confluence_publish_root'] = '123456'
        self._try_config()

        self.config['confluence_publish_root'] = 0
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_publish_root'] = -123456
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_publish_root'] = 'MyPage'
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

    def test_config_check_publish_target_conflicts(self):
        # enable publishing enabled checks
        self._prepare_valid_publish()

        # confluence_parent_page and confluence_publish_root conflict
        self.config['confluence_parent_page'] = 'dummy'
        self.config['confluence_publish_root'] = 123456
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

    def test_config_check_publish_token(self):
        self.config['confluence_publish_token'] = ''
        self._try_config()

        self.config['confluence_publish_token'] = 'dummy'  # noqa: S105
        self._try_config()

    def test_config_check_quote_wrapped_auth(self):
        self.config['confluence_api_token'] = '"test"'  # noqa: S105
        with self.assertRaises(SphinxWarning):
            self._try_config()

        self.config['confluence_publish_token'] = '"test"'  # noqa: S105
        with self.assertRaises(SphinxWarning):
            self._try_config()

        self.config['confluence_server_pass'] = "'test'"  # noqa: S105
        with self.assertRaises(SphinxWarning):
            self._try_config()

    def test_config_check_secnumber_suffix(self):
        self.config['confluence_secnumber_suffix'] = ''
        self._try_config()

        self.config['confluence_secnumber_suffix'] = 'dummy'
        self._try_config()

    def test_config_check_server_auth(self):
        self.config['confluence_server_auth'] = HTTPDigestAuth('user', 'pass')
        self._try_config()

        class ValidAuth(AuthBase):
            def __call__(self, r):
                return r

        self.config['confluence_server_auth'] = ValidAuth()
        self._try_config()

        class InvalidAuth:
            pass

        self.config['confluence_server_auth'] = InvalidAuth()
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

    def test_config_check_server_cookies(self):
        self.config['confluence_server_cookies'] = {}
        self._try_config()

        self.config['confluence_server_cookies'] = {
            'SESSION_ID': 'b8e536f5-895a-4054-b370-e0c579cb8d6b',
            'U_ID': 'myusername',
        }
        self._try_config()

        self.config['confluence_server_cookies'] = {
            'SID': None,
        }
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

    def test_config_check_server_pass(self):
        self.config['confluence_server_pass'] = 'dummy'  # noqa: S105
        self._try_config()

        # enable publishing enabled checks
        self._prepare_valid_publish()

        # without `confluence_server_user` should throw an error
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_server_user'] = 'dummy'
        self._try_config()

    def test_config_check_server_url(self):
        self.config['confluence_server_url'] = \
            'https://example.atlassian.net/wiki/'
        self._try_config()

        self.config['confluence_server_url'] = \
            'https://example.atlassian.net/wiki'
        with self.assertRaises(SphinxWarning):
            self._try_config()

        self.config['confluence_server_url'] = \
            'https://intranet-wiki.example.com/'
        self._try_config()

        self.config['confluence_server_url'] = \
            'https://intranet-wiki.example.com'
        with self.assertRaises(SphinxWarning):
            self._try_config()

        self.config['confluence_server_url'] = \
            'https://intranet-wiki.example.com/rest/api/'
        with self.assertRaises(SphinxWarning):
            self._try_config()

        # enable publishing enabled checks
        self._prepare_valid_publish()

        # without `confluence_server_url` with publishing should throw an error
        self.config['confluence_server_url'] = None
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_server_url'] = \
            'https://intranet-wiki.example.org/'
        self._try_config()

    def test_config_check_server_user(self):
        self.config['confluence_server_user'] = 'dummy'
        self._try_config()

    def test_config_check_space_name(self):
        self.config['confluence_space_key'] = 'DUMMY'
        self._try_config()

        # enable publishing enabled checks
        self._prepare_valid_publish()

        # without `confluence_space_key` with publishing should throw an error
        self.config['confluence_space_key'] = None
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_space_key'] = 'DUMMY2'
        self._try_config()

    def test_config_check_sourcelink(self):
        self.config['confluence_sourcelink'] = {}
        self._try_config()

        self.config['confluence_sourcelink'] = {
            'url': 'https://example.com',
        }
        self._try_config()

        self.config['confluence_sourcelink'] = {
            'dummy': 'value',
        }
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_sourcelink'] = {
            'url': None,
        }
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        # reserved check
        self.config['confluence_sourcelink'] = {
            'url': 'https://example.com',
            'page': 'test',
        }
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_sourcelink'] = {
            'url': 'https://example.com',
            'suffix': 'test',
        }
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        # templates
        supported_templates = [
            'bitbucket',
            'codeberg',
            'github',
            'gitlab',
        ]

        for template in supported_templates:
            valid_template = {
                'type': template,
                'owner': 'test',
                'repo': 'test',
                'version': 'test',
            }
            self.config['confluence_sourcelink'] = dict(valid_template)
            self._try_config()

            sourcelink = dict(valid_template)
            del sourcelink['owner']
            self.config['confluence_sourcelink'] = sourcelink
            with self.assertRaises(ConfluenceConfigError):
                self._try_config()

            sourcelink = dict(valid_template)
            del sourcelink['repo']
            self.config['confluence_sourcelink'] = sourcelink
            with self.assertRaises(ConfluenceConfigError):
                self._try_config()

            sourcelink = dict(valid_template)
            del sourcelink['version']
            self.config['confluence_sourcelink'] = sourcelink
            with self.assertRaises(ConfluenceConfigError):
                self._try_config()

        invalid_template = {
            'type': 'invalid',
            'owner': 'test',
            'repo': 'test',
            'version': 'test',
        }
        self.config['confluence_sourcelink'] = dict(invalid_template)
        with self.assertRaises(ConfluenceSourcelinkTypeConfigError):
            self._try_config()

    def test_config_check_tab_macro(self):
        self.config['confluence_tab_macro'] = {
            'macro-name': 'macro-name',
        }
        self._try_config()

        self.config['confluence_tab_macro'] = {
            'macro-name': None,
        }
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

        self.config['confluence_tab_macro'] = 1
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

    def test_config_check_title_overrides(self):
        self.config['confluence_title_overrides'] = {}
        self._try_config()

        self.config['confluence_title_overrides'] = {
            'index': 'Index Override',
        }
        self._try_config()

        self.config['confluence_title_overrides'] = {
            'index': None,
        }
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

    def test_config_check_timeout(self):
        self.config['confluence_timeout'] = 2
        self._try_config()

        self.config['confluence_timeout'] = '2'
        self._try_config()

        self.config['confluence_timeout'] = -1
        with self.assertRaises(ConfluenceConfigError):
            self._try_config()

    def test_config_check_confluence_version_comment(self):
        self.config['confluence_version_comment'] = ''
        self._try_config()

        self.config['confluence_version_comment'] = 'dummy'
        self._try_config()
