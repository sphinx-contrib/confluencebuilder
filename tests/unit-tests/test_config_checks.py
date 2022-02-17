# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from requests.auth import AuthBase
from requests.auth import HTTPDigestAuth
from sphinx.errors import SphinxWarning
from sphinxcontrib.confluencebuilder.builder import ConfluenceBuilder
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceConfigurationError
from tests.lib import EXT_NAME
from tests.lib import mock_getpass
from tests.lib import mock_input
from tests.lib import prepare_conf
from tests.lib import prepare_sphinx
import os
import unittest


class TestConfluenceConfigChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = os.path.dirname(os.path.realpath(__file__))
        cls.dataset = os.path.join(cls.test_dir, 'datasets', 'common')
        cls.dummy_exists = os.path.join(cls.test_dir, 'assets', 'dummy')
        cls.dummy_missing = os.path.join(cls.test_dir, 'assets', 'missing')

        cls.minimal_config = {'extensions': EXT_NAME}

    def run(self, result=None):
        # unique configuration each run to avoid copying it in each test
        self.config = prepare_conf()

        super(TestConfluenceConfigChecks, self).run(result)

    def _prepare_valid_publish(self):
        self.config['confluence_publish'] = True
        self.config['confluence_server_url'] = \
            'https://intranet-wiki.example.com/'
        self.config['confluence_space_key'] = 'DUMMY'

    def _try_config(self, config=None, edefs=None, dataset=None):
        config = config if config else self.minimal_config
        dataset = dataset if dataset else self.dataset

        with prepare_sphinx(dataset, config=config, extra_config=edefs) as app:
            builder = ConfluenceBuilder(app)

            class MockedPublisher:
                def init(self, config):
                    pass

                def connect(self):
                    pass

                def disconnect(self):
                    pass
            builder.publisher = MockedPublisher()

            for k, v in self.config.items():
                setattr(builder.config, k, v)

            builder.init()

    def test_config_check_ask_password(self):
        print('')  # space out ask output if an unbuffered run

        self.config['confluence_ask_password'] = True
        self._try_config()

        # enable publishing enabled checks
        self._prepare_valid_publish()

        with mock_getpass('password'):
            with self.assertRaises(ConfluenceConfigurationError):
                self._try_config()

        self.config['confluence_ask_user'] = True

        with mock_input('username'), mock_getpass('password'):
            self._try_config()

        self.config['confluence_ask_user'] = False
        self.config['confluence_server_user'] = 'username'

        with mock_getpass('password'):
            self._try_config()

        with mock_getpass(''):
            with self.assertRaises(ConfluenceConfigurationError):
                self._try_config()

        del self.config['confluence_ask_password']
        del self.config['confluence_ask_user']
        self.config['confluence_server_user'] = 'username'

        defines = {
            'confluence_ask_password': '1',
        }
        with mock_getpass(''):
            with self.assertRaises(ConfluenceConfigurationError):
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
        print('')  # space out ask output if an unbuffered run

        self.config['confluence_ask_user'] = True
        self._try_config()

        # enable publishing enabled checks
        self._prepare_valid_publish()

        with mock_input('username'):
            self._try_config()

        with mock_input(''):
            with self.assertRaises(ConfluenceConfigurationError):
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
            with self.assertRaises(ConfluenceConfigurationError):
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
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

        self.config['confluence_additional_mime_types'] = ['image tiff']
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

        self.config['confluence_additional_mime_types'] = ['image/unknown-type']
        with self.assertRaises(SphinxWarning):
            self._try_config()

    def test_config_check_ca_cert(self):
        valid_cert = self.dummy_exists
        missing_cert = self.dummy_missing

        self.config['confluence_ca_cert'] = valid_cert
        self._try_config()

        self.config['confluence_ca_cert'] = missing_cert
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

    def test_config_check_client_cert(self):
        valid_cert = self.dummy_exists
        missing_cert = self.dummy_missing

        self.config['confluence_client_cert'] = valid_cert
        self._try_config()

        self.config['confluence_client_cert'] = (valid_cert, valid_cert)
        self._try_config()

        self.config['confluence_client_cert'] = missing_cert
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

        self.config['confluence_client_cert'] = (valid_cert, missing_cert)
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

        self.config['confluence_client_cert'] = (missing_cert, valid_cert)
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

        # too many
        self.config['confluence_client_cert'] = \
            (valid_cert, valid_cert, valid_cert)
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

    def test_config_check_cert_pass(self):
        self.config['confluence_client_cert_pass'] = 'dummy'
        self._try_config()

    def test_config_check_default_alignment(self):
        self.config['confluence_default_alignment'] = 'left'
        self._try_config()

        self.config['confluence_default_alignment'] = 'center'
        self._try_config()

        self.config['confluence_default_alignment'] = 'right'
        self._try_config()

        self.config['confluence_default_alignment'] = 'invalid'
        with self.assertRaises(ConfluenceConfigurationError):
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
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

        self.config['confluence_domain_indices'] = [
            None,
        ]
        with self.assertRaises(ConfluenceConfigurationError):
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

    def test_config_check_file_transform(self):
        def mock_transform(docname):
            return docname + '.conf'

        self.config['confluence_file_transform'] = mock_transform
        self._try_config()

        self.config['confluence_file_transform'] = 'invalid'
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

    def test_config_check_footer_file(self):
        valid_footer = self.dummy_exists
        missing_footer = self.dummy_missing

        self.config['confluence_footer_file'] = valid_footer
        self._try_config()

        self.config['confluence_footer_file'] = missing_footer
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

        relbase = '../../templates/'
        self.config['confluence_footer_file'] = relbase + 'sample-footer.tpl'
        self._try_config()

    def test_config_check_global_labels(self):
        self.config['confluence_global_labels'] = ['label-a', 'label-b']
        self._try_config()

        self.config['confluence_global_labels'] = 'label-a label-b'
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

    def test_config_check_header_file(self):
        valid_header = self.dummy_exists
        missing_header = self.dummy_missing

        self.config['confluence_header_file'] = valid_header
        self._try_config()

        self.config['confluence_header_file'] = missing_header
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

        relbase = '../../templates/'
        self.config['confluence_header_file'] = relbase + 'sample-header.tpl'
        self._try_config()

    def test_config_check_jira_servers(self):
        self.config['confluence_jira_servers'] = {}
        self._try_config()

        self.config['confluence_jira_servers'] = {
            'server-1': {
                'id': '92d94d0e-ac8b-4f2e-92a5-2217ad88e5f2',
                'name': 'MyAwesomeServer'
            }
        }
        self._try_config()

        self.config['confluence_jira_servers'] = []
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

        self.config['confluence_jira_servers'] = {
            None: {
                'id': '92d94d0e-ac8b-4f2e-92a5-2217ad88e5f2',
                'name': 'MyAwesomeServer'
            }
        }
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

        self.config['confluence_jira_servers'] = {
            'server-1': None
        }
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

        self.config['confluence_jira_servers'] = {
            'server-1': {}
        }
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

        self.config['confluence_jira_servers'] = {
            'server-1': {
                'id': '92d94d0e-ac8b-4f2e-92a5-2217ad88e5f2',
            }
        }
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

        self.config['confluence_jira_servers'] = {
            'server-1': {
                'name': 'MyAwesomeServer'
            }
        }
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

    def test_config_check_lang_transform(self):
        def mock_transform(lang):
            return 'default'

        self.config['confluence_lang_transform'] = mock_transform
        self._try_config()

        self.config['confluence_lang_transform'] = 'invalid'
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

    def test_config_check_link_suffix(self):
        self.config['confluence_link_suffix'] = '.conf'
        self._try_config()

    def test_config_check_link_transform(self):
        def mock_transform(docname):
            return docname + '.conf'

        self.config['confluence_link_transform'] = mock_transform
        self._try_config()

        self.config['confluence_link_transform'] = 'invalid'
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

    def test_config_check_max_doc_depth(self):
        self.config['confluence_max_doc_depth'] = 2
        with self.assertRaises(SphinxWarning):
            self._try_config()

        self.config['confluence_max_doc_depth'] = '2'
        with self.assertRaises(SphinxWarning):
            self._try_config()

        self.config['confluence_max_doc_depth'] = -1
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

        self.config['confluence_max_doc_depth'] = 0
        with self.assertRaises(SphinxWarning):
            self._try_config()

        del self.config['confluence_max_doc_depth']

        defines = {
            'confluence_max_doc_depth': '1',
        }
        with self.assertRaises(SphinxWarning):
            self._try_config(edefs=defines)

    def test_config_check_parent_page(self):
        self.config['confluence_parent_page'] = 'dummy'
        self._try_config()

    def test_config_check_parent_page_id_check(self):
        # enable publishing enabled checks
        self._prepare_valid_publish()

        # without `confluence_parent_page` should throw a error
        self.config['confluence_parent_page_id_check'] = 123456
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

        self.config['confluence_parent_page'] = 'dummy'
        self._try_config()

        self.config['confluence_parent_page_id_check'] = '123456'
        self._try_config()

        self.config['confluence_parent_page_id_check'] = 0
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

        self.config['confluence_parent_page_id_check'] = -123456
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

    def test_config_check_prev_next_buttons_location(self):
        self.config['confluence_prev_next_buttons_location'] = 'bottom'
        self._try_config()

        self.config['confluence_prev_next_buttons_location'] = 'both'
        self._try_config()

        self.config['confluence_prev_next_buttons_location'] = 'top'
        self._try_config()

        self.config['confluence_prev_next_buttons_location'] = 'invalid'
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

    def test_config_check_publish(self):
        # stock configuration should need more than just the publish flag
        self.config['confluence_publish'] = True
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

    def test_config_check_publish_delay(self):
        self.config['confluence_publish_delay'] = 0.3
        self._try_config()

        self.config['confluence_publish_delay'] = 1
        self._try_config()

        self.config['confluence_publish_delay'] = '0.7'
        self._try_config()

        self.config['confluence_publish_delay'] = -1
        with self.assertRaises(ConfluenceConfigurationError):
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
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

        self.config['confluence_publish_headers'] = {
            123: 'bad-key-good-value',
        }
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

    def test_config_check_publish_list(self):
        dataset = os.path.join(self.test_dir, 'datasets', 'publish-set')
        assets_dir = os.path.join(self.test_dir, 'assets')
        invalid_list = os.path.join(assets_dir, 'sample-invalid-publish-list')
        missing_list = self.dummy_missing
        valid_list = os.path.join(assets_dir, 'sample-valid-publish-list')

        options = [
            'confluence_publish_allowlist',
            'confluence_publish_denylist',
        ]

        for option in options:
            # empty value (list; ignore state)
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
            self.config[option] = [u'doc-c']
            self._try_config(dataset=dataset)

            # file with a valid document list
            self.assertTrue(os.path.isfile(valid_list))
            self.config[option] = valid_list
            self._try_config(dataset=dataset)

            # list with invalid content
            self.config[option] = [True, False]
            with self.assertRaises(ConfluenceConfigurationError):
                self._try_config(dataset=dataset)

            # missing document
            self.config[option] = ['missing']
            with self.assertRaises(ConfluenceConfigurationError):
                self._try_config(dataset=dataset)

            # use of file extension
            self.config[option] = ['index.rst']
            with self.assertRaises(ConfluenceConfigurationError):
                self._try_config(dataset=dataset)

            # file with invalid document list
            self.assertTrue(os.path.isfile(invalid_list))
            self.config[option] = invalid_list
            with self.assertRaises(ConfluenceConfigurationError):
                self._try_config(dataset=dataset)

            # missing file
            self.assertFalse(os.path.isfile(missing_list))
            self.config[option] = missing_list
            with self.assertRaises(ConfluenceConfigurationError):
                self._try_config(dataset=dataset)

            # cleanup
            self.config[option] = None

            # enumalate command line csv string to list (valid)
            config = dict(self.minimal_config)
            config[option] = 'doc-a,doc-c'
            self._try_config(config=config, dataset=dataset)

            # enumalate command line csv string to list (invalid)
            config = dict(self.minimal_config)
            config[option] = 'doc-a2,doc-c'
            with self.assertRaises(ConfluenceConfigurationError):
                self._try_config(config=config, dataset=dataset)

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

    def test_config_check_publish_root(self):
        # enable publishing enabled checks
        self._prepare_valid_publish()

        self.config['confluence_publish_root'] = 123456
        self._try_config()

        self.config['confluence_publish_root'] = '123456'
        self._try_config()

        self.config['confluence_publish_root'] = 0
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

        self.config['confluence_publish_root'] = -123456
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

    def test_config_check_publish_target_conflicts(self):
        # enable publishing enabled checks
        self._prepare_valid_publish()

        # confluence_parent_page and confluence_publish_root conflict
        self.config['confluence_parent_page'] = 'dummy'
        self.config['confluence_publish_root'] = 123456
        with self.assertRaises(ConfluenceConfigurationError):
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
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

    def test_config_check_server_cookies(self):
        self.config['confluence_server_cookies'] = {}
        self._try_config()

        self.config['confluence_server_cookies'] = {
            'SESSION_ID': 'b8e536f5-895a-4054-b370-e0c579cb8d6b',
            'U_ID': 'myusername'
        }
        self._try_config()

        self.config['confluence_server_cookies'] = {
            'SID': None,
        }
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

    def test_config_check_server_pass(self):
        self.config['confluence_server_pass'] = 'dummy'
        self._try_config()

        # enable publishing enabled checks
        self._prepare_valid_publish()

        # without `confluence_server_user` should throw an error
        with self.assertRaises(ConfluenceConfigurationError):
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
        with self.assertRaises(ConfluenceConfigurationError):
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
        with self.assertRaises(ConfluenceConfigurationError):
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
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

        self.config['confluence_sourcelink'] = {
            'url': None,
        }
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

        # reserved check
        self.config['confluence_sourcelink'] = {
            'url': 'https://example.com',
            'page': 'test',
        }
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

        self.config['confluence_sourcelink'] = {
            'url': 'https://example.com',
            'suffix': 'test',
        }
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

        # templates
        supported_templates = [
            'bitbucket',
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
            with self.assertRaises(ConfluenceConfigurationError):
                self._try_config()

            sourcelink = dict(valid_template)
            del sourcelink['repo']
            self.config['confluence_sourcelink'] = sourcelink
            with self.assertRaises(ConfluenceConfigurationError):
                self._try_config()

            sourcelink = dict(valid_template)
            del sourcelink['version']
            self.config['confluence_sourcelink'] = sourcelink
            with self.assertRaises(ConfluenceConfigurationError):
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
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()

    def test_config_check_timeout(self):
        self.config['confluence_timeout'] = 2
        self._try_config()

        self.config['confluence_timeout'] = '2'
        self._try_config()

        self.config['confluence_timeout'] = -1
        with self.assertRaises(ConfluenceConfigurationError):
            self._try_config()
