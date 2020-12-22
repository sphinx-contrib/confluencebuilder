# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from contextlib import contextmanager
from sphinxcontrib.confluencebuilder.builder import ConfluenceBuilder
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceConfigurationError
from tests.lib import EXT_NAME
from tests.lib import prepare_dirs
from tests.lib import prepare_sphinx
import os
import unittest

class TestConfluenceConfig(unittest.TestCase):
    def run(self, result=None):
        # prepare a dummy application; no need to actually build
        self.config = {'extensions': EXT_NAME}
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        self.mock_ds = os.path.join(self.test_dir, 'dataset-common')
        self.doc_dir = prepare_dirs('config-dummy')

        # legacy
        with self._build_app() as app:
            self.app = app
            super(TestConfluenceConfig, self).run(result)

    @contextmanager
    def _build_app(self):
        with prepare_sphinx(self.mock_ds, config=self.config, out_dir=self.doc_dir) as app:
            yield app

    def test_legacy_emptyconfig(self):
        builder = ConfluenceBuilder(self.app)
        try:
            builder.init(suppress_conf_check=True)
        except ConfluenceConfigurationError:
            self.fail("configuration exception raised with valid config")

    def test_legacy_missing_templates(self):
        builder = ConfluenceBuilder(self.app)
        template_dir = os.path.join(self.test_dir, os.pardir, os.pardir, 'templates')

        tpl = os.path.join(template_dir, 'sample-header-x.tpl')
        builder.config.confluence_header_file = tpl
        with self.assertRaises(ConfluenceConfigurationError):
            builder.init(suppress_conf_check=True)

        tpl = os.path.join(template_dir, 'sample-header.tpl')
        builder.config.confluence_header_file = tpl
        try:
            builder.init(suppress_conf_check=True)
        except ConfluenceConfigurationError:
            self.fail("configuration exception raised with valid header")

        builder.config.confluence_header_file = '../../../templates/sample-header.tpl'
        try:
            builder.init(suppress_conf_check=True)
        except ConfluenceConfigurationError:
            self.fail("configuration exception raised with valid header")

        builder.config.confluence_header_file = None

        tpl = os.path.join(template_dir, 'sample-footer-x.tpl')
        builder.config.confluence_footer_file = tpl
        with self.assertRaises(ConfluenceConfigurationError):
            builder.init(suppress_conf_check=True)

        tpl = os.path.join(template_dir, 'sample-footer.tpl')
        builder.config.confluence_footer_file = tpl
        try:
            builder.init(suppress_conf_check=True)
        except ConfluenceConfigurationError:
            self.fail("configuration exception raised with valid footer")

        builder.config.confluence_footer_file = '../../../templates/sample-footer.tpl'
        try:
            builder.init(suppress_conf_check=True)
        except ConfluenceConfigurationError:
            self.fail("configuration exception raised with valid header")

        builder.config.confluence_footer_file = None

    def test_legacy_publish_config(self):
        builder = ConfluenceBuilder(self.app)
        builder.config.confluence_publish = True
        with self.assertRaises(ConfluenceConfigurationError):
            builder.init(suppress_conf_check=True)

    def test_legacy_publish_lists(self):
        builder = ConfluenceBuilder(self.app)
        config = builder.config
        config.source_suffix = {
            '.rst': 'restructuredtext',
        }

        assets_dir = os.path.join(self.test_dir, 'assets')
        invalid_list = os.path.join(assets_dir, 'sample-invalid-publish-list')
        missing_list = os.path.join(assets_dir, 'sample-missing-publish-list')
        valid_list = os.path.join(assets_dir, 'sample-valid-publish-list')

        options = [
            'confluence_publish_allowlist',
            'confluence_publish_denylist',
        ]

        for option in options:
            # empty value (string; ignore state)
            setattr(config, option, '')
            try:
                builder.init(suppress_conf_check=True)
            except ConfluenceConfigurationError:
                self.fail('configuration exception raised with '
                    'empty (string) list: ' + option)

            # empty value (list; ignore state)
            setattr(config, option, [])
            try:
                builder.init(suppress_conf_check=True)
            except ConfluenceConfigurationError:
                self.fail('configuration exception raised with '
                    'empty (list) list: ' + option)

            # document list with valid entries
            setattr(config, option, ['index'])
            try:
                builder.init(suppress_conf_check=True)
            except ConfluenceConfigurationError:
                self.fail('configuration exception raised with '
                    'valid document list: ' + option)

            # explicitly force unicode strings to help verify python 2.x series
            # dealing with unicode strings inside the document subset
            setattr(config, option, [u'index'])
            try:
                builder.init(suppress_conf_check=True)
            except ConfluenceConfigurationError:
                self.fail('configuration exception raised with '
                    'valid document (unicode) list: ' + option)

            # file with a valid document list
            self.assertTrue(os.path.isfile(valid_list))
            setattr(config, option, valid_list)
            try:
                builder.init(suppress_conf_check=True)
            except ConfluenceConfigurationError:
                self.fail('configuration exception raised with '
                    'valid document file list: ' + option)

            # invalid content
            setattr(config, option, True)
            with self.assertRaises(ConfluenceConfigurationError):
                builder.init(suppress_conf_check=True)

            # list with invalid content
            setattr(config, option, [True, False])
            with self.assertRaises(ConfluenceConfigurationError):
                builder.init(suppress_conf_check=True)

            # missing document
            setattr(config, option, ['missing'])
            with self.assertRaises(ConfluenceConfigurationError):
                builder.init(suppress_conf_check=True)

            # use of file extension
            setattr(config, option, ['index.rst'])
            with self.assertRaises(ConfluenceConfigurationError):
                builder.init(suppress_conf_check=True)

            # file with invalid document list
            self.assertTrue(os.path.isfile(invalid_list))
            setattr(config, option, invalid_list)
            with self.assertRaises(ConfluenceConfigurationError):
                builder.init(suppress_conf_check=True)

            # missing file
            self.assertFalse(os.path.isfile(missing_list))
            setattr(config, option, missing_list)
            with self.assertRaises(ConfluenceConfigurationError):
                builder.init(suppress_conf_check=True)

            # clear back to the default state
            setattr(config, option, None)

    def test_legacy_invalid_ca_cert(self):
        builder = ConfluenceBuilder(self.app)
        ca_cert = os.path.join(self.test_dir, 'certs', 'non_existant.crt')
        builder.config.confluence_publish = True
        builder.config.confluence_ca_cert = ca_cert
        builder.config.confluence_server_url = "some_url"
        builder.config.confluence_space_name = "some_space_name"
        with self.assertRaises(ConfluenceConfigurationError):
            builder.init(suppress_conf_check=True)

        builder.config.confluence_publish = False
        builder.config.confluence_ca_cert = None
        builder.config.confluence_server_url = None
        builder.config.confluence_space_name = None

    def test_legacy_too_many_client_certs(self):
        builder = ConfluenceBuilder(self.app)
        this_file = os.path.realpath(__file__)
        cert = (this_file, this_file, this_file)
        builder.config.confluence_publish = True
        builder.config.confluence_client_cert = cert
        builder.config.confluence_server_url = "some_url"
        builder.config.confluence_space_name = "some_space_name"
        with self.assertRaises(ConfluenceConfigurationError):
            builder.init(suppress_conf_check=True)

        builder.config.confluence_publish = False
        builder.config.confluence_client_cert = None
        builder.config.confluence_server_url = None
        builder.config.confluence_space_name = None

    def test_legacy_format_client_cert(self):
        builder = ConfluenceBuilder(self.app)
        this_file = os.path.realpath(__file__)
        builder.config.confluence_publish = True
        ca_cert = os.path.join(self.test_dir, 'certs', 'non_existant.crt')
        builder.config.confluence_client_cert = this_file
        builder.config.confluence_server_url = "http://somehost/"
        builder.config.confluence_space_name = "some_space_name"
        builder.config.confluence_ca_cert = ca_cert

        with self.assertRaises(ConfluenceConfigurationError):
            builder.init(suppress_conf_check=True)

        self.assertEqual(len(builder.config.confluence_client_cert), 2)
        self.assertEqual(builder.config.confluence_client_cert,
                         (this_file, None))

        builder.config.confluence_publish = False
        builder.config.confluence_client_cert = None
        builder.config.confluence_ca_cert = None
        builder.config.confluence_server_url = None
        builder.config.confluence_space_name = None

    def test_legacy_client_cert_does_not_exist(self):
        builder = ConfluenceBuilder(self.app)
        client_cert = os.path.join(self.test_dir, 'certs', 'non_existant.crt')
        builder.config.confluence_publish = True
        builder.config.confluence_client_cert = client_cert
        builder.config.confluence_server_url = "some_url"
        builder.config.confluence_space_name = "some_space_name"
        with self.assertRaises(ConfluenceConfigurationError):
            builder.init(suppress_conf_check=True)

        self.assertEqual(len(builder.config.confluence_client_cert), 2)

        builder.config.confluence_publish = False
        builder.config.confluence_client_cert = None
        builder.config.confluence_server_url = None
        builder.config.confluence_space_name = None
