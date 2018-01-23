# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2016-2018 by the contributors (see AUTHORS file).
    :license: BSD, see LICENSE.txt for details.
"""

from sphinxcontrib.confluencebuilder.builder import ConfluenceBuilder
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceConfigurationError
from sphinxcontrib_confluencebuilder_util import ConfluenceTestUtil as _
from sphinxcontrib_confluencebuilder_util import EXT_NAME
import os
import unittest

class TestConfluenceConfig(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # prepare a dummy application; no need to actually build
        config = { 'extensions': EXT_NAME }
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        mock_ds = os.path.join(self.test_dir, 'dataset-common')
        doc_dir, doctree_dir = _.prepareDirectories('config-dummy')
        self.app = _.prepareSphinx(mock_ds, doc_dir, doctree_dir, config)

    def test_emptyconfig(self):
        builder = ConfluenceBuilder(self.app)
        try:
            builder.init(suppress_conf_check=True)
        except ConfluenceConfigurationError:
            self.fail("configuration exception raised with valid config")

    def test_missing_templates(self):
        builder = ConfluenceBuilder(self.app)
        template_dir = os.path.join(self.test_dir, 'templates')

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

        builder.config.confluence_header_file = None

        tpl = os.path.join(template_dir, 'sample-footer-x.tpl')
        builder.config.confluence_header_file = tpl
        with self.assertRaises(ConfluenceConfigurationError):
            builder.init(suppress_conf_check=True)

        tpl = os.path.join(template_dir, 'sample-footer.tpl')
        builder.config.confluence_header_file = tpl
        try:
            builder.init(suppress_conf_check=True)
        except ConfluenceConfigurationError:
            self.fail("configuration exception raised with valid footer")

        builder.config.confluence_footer_file = None

    def test_publish_config(self):
        builder = ConfluenceBuilder(self.app)
        builder.config.confluence_publish = True
        with self.assertRaises(ConfluenceConfigurationError):
            builder.init(suppress_conf_check=True)
