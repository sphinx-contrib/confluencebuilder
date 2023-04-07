# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib import prepare_conf
from tests.lib import prepare_sphinx
import os
import unittest


class TestConfluenceConfigEnvironment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_dir = os.path.dirname(os.path.realpath(__file__))
        cls.dataset = os.path.join(test_dir, 'datasets', 'common')

    def run(self, result=None):
        # unique configuration each run to avoid copying it in each test
        self.config = prepare_conf()

        # ensure environment overrides do not leak between tests
        old_env = dict(os.environ)
        try:
            super().run(result)
        finally:
            os.environ.clear()
            os.environ.update(old_env)

    def test_config_env_bool(self):
        # default unset
        with prepare_sphinx(self.dataset, config=self.config) as app:
            self.assertIsNone(app.config.confluence_publish_debug)

        # configure option from environment
        os.environ['CONFLUENCE_PUBLISH_DEBUG'] = '0'
        with prepare_sphinx(self.dataset, config=self.config) as app:
            self.assertFalse(app.config.confluence_publish_debug)

        os.environ['CONFLUENCE_PUBLISH_DEBUG'] = '1'
        with prepare_sphinx(self.dataset, config=self.config) as app:
            self.assertTrue(app.config.confluence_publish_debug)

        # override the option (taking precedence over environment)
        self.config['confluence_publish_debug'] = False
        with prepare_sphinx(self.dataset, config=self.config) as app:
            self.assertFalse(app.config.confluence_publish_debug)
        self.assertTrue('CONFLUENCE_PUBLISH_DEBUG' in os.environ)
        self.assertEqual(os.environ['CONFLUENCE_PUBLISH_DEBUG'], '1')

    def test_config_env_int(self):
        # default unset
        with prepare_sphinx(self.dataset, config=self.config) as app:
            self.assertIsNone(app.config.confluence_timeout)

        # configure option from environment
        os.environ['CONFLUENCE_TIMEOUT'] = '5'
        with prepare_sphinx(self.dataset, config=self.config) as app:
            self.assertEqual(app.config.confluence_timeout, 5)

        # override the option (taking precedence over environment)
        self.config['confluence_timeout'] = 10
        with prepare_sphinx(self.dataset, config=self.config) as app:
            self.assertEqual(app.config.confluence_timeout, 10)
        self.assertTrue('CONFLUENCE_TIMEOUT' in os.environ)
        self.assertEqual(os.environ['CONFLUENCE_TIMEOUT'], '5')

    def test_config_env_str(self):
        # default unset
        with prepare_sphinx(self.dataset, config=self.config) as app:
            self.assertIsNone(app.config.confluence_space_key)

        # configure option from environment
        os.environ['CONFLUENCE_SPACE_KEY'] = 'FIRSTSPACE'
        with prepare_sphinx(self.dataset, config=self.config) as app:
            self.assertEqual(app.config.confluence_space_key, 'FIRSTSPACE')

        # override the option (taking precedence over environment)
        self.config['confluence_space_key'] = 'SECONDSPACE'
        with prepare_sphinx(self.dataset, config=self.config) as app:
            self.assertEqual(app.config.confluence_space_key, 'SECONDSPACE')
        self.assertTrue('CONFLUENCE_SPACE_KEY' in os.environ)
        self.assertEqual(os.environ['CONFLUENCE_SPACE_KEY'], 'FIRSTSPACE')
