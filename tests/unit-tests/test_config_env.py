# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from pathlib import Path
from tests.lib import prepare_conf
from tests.lib import prepare_sphinx
import os
import unittest


class TestConfluenceConfigEnvironment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_dir = Path(__file__).parent.resolve()
        cls.dataset = test_dir / 'datasets' / 'common'

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
            self.assertIsNone(app.config.confluence_publish_force)

        # configure option from environment
        os.environ['CONFLUENCE_PUBLISH_FORCE'] = '0'
        with prepare_sphinx(self.dataset, config=self.config) as app:
            self.assertFalse(app.config.confluence_publish_force)

        os.environ['CONFLUENCE_PUBLISH_FORCE'] = '1'
        with prepare_sphinx(self.dataset, config=self.config) as app:
            self.assertTrue(app.config.confluence_publish_force)

        # override the option (taking precedence over environment)
        self.config['confluence_publish_force'] = False
        with prepare_sphinx(self.dataset, config=self.config) as app:
            self.assertFalse(app.config.confluence_publish_force)
        self.assertTrue('CONFLUENCE_PUBLISH_FORCE' in os.environ)
        self.assertEqual(os.environ['CONFLUENCE_PUBLISH_FORCE'], '1')

    def test_config_env_disabled(self):
        # default unset
        with prepare_sphinx(self.dataset, config=self.config) as app:
            self.assertIsNone(app.config.confluence_publish_force)

        # configure option from environment
        os.environ['CONFLUENCE_PUBLISH_FORCE'] = '1'
        with prepare_sphinx(self.dataset, config=self.config) as app:
            self.assertTrue(app.config.confluence_publish_force)

        # disable environment options
        self.config['confluence_disable_env_conf'] = True
        with prepare_sphinx(self.dataset, config=self.config) as app:
            self.assertFalse(app.config.confluence_publish_force)
        self.assertTrue('CONFLUENCE_PUBLISH_FORCE' in os.environ)
        self.assertEqual(os.environ['CONFLUENCE_PUBLISH_FORCE'], '1')

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
