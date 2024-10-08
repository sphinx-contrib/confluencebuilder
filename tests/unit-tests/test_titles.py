# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger as logger
from sphinxcontrib.confluencebuilder.state import ConfluenceState
from sphinxcontrib.confluencebuilder.std.confluence import CONFLUENCE_MAX_TITLE_LEN
from tests.lib import MockedConfig
import unittest


class TestTitles(unittest.TestCase):
    def setUp(self):
        ConfluenceState.reset()
        self.config = MockedConfig()

        # force (re-)initialize of logger to avoid logger being already
        # configured with a warning-exception filter in a previous test
        logger.initialize(preload=True)

    def _register_title(self, title):
        return ConfluenceState.register_title('mock', title, self.config)

    def test_titles_maximum_checks_default(self):
        t0 = self._register_title('S' * (CONFLUENCE_MAX_TITLE_LEN - 1))
        t1 = self._register_title('S' * CONFLUENCE_MAX_TITLE_LEN)
        t2 = self._register_title('S' * (CONFLUENCE_MAX_TITLE_LEN + 1))

        self.assertEqual(len(t0), CONFLUENCE_MAX_TITLE_LEN - 1)
        self.assertEqual(len(t1), CONFLUENCE_MAX_TITLE_LEN)
        self.assertEqual(len(t2), CONFLUENCE_MAX_TITLE_LEN)

    def test_titles_maximum_checks_duplicate_capped(self):
        t0 = self._register_title('S' * (CONFLUENCE_MAX_TITLE_LEN - 1))
        t1 = self._register_title('S' * (CONFLUENCE_MAX_TITLE_LEN - 1))

        self.assertEqual(len(t0), CONFLUENCE_MAX_TITLE_LEN - 1)
        self.assertEqual(len(t1), CONFLUENCE_MAX_TITLE_LEN)

    def test_titles_maximum_checks_postfix(self):
        self.config.confluence_publish_postfix = 'Z'

        t0 = self._register_title('S' * (CONFLUENCE_MAX_TITLE_LEN - 2))
        t1 = self._register_title('S' * (CONFLUENCE_MAX_TITLE_LEN - 1))
        t2 = self._register_title('S' * CONFLUENCE_MAX_TITLE_LEN)
        t3 = self._register_title('S' * (CONFLUENCE_MAX_TITLE_LEN + 1))

        self.assertEqual(len(t0), CONFLUENCE_MAX_TITLE_LEN - 1)
        self.assertEqual(len(t1), CONFLUENCE_MAX_TITLE_LEN)
        self.assertEqual(len(t2), CONFLUENCE_MAX_TITLE_LEN)
        self.assertEqual(len(t3), CONFLUENCE_MAX_TITLE_LEN)

    def test_titles_maximum_checks_prefix(self):
        self.config.confluence_publish_prefix = 'A'

        t0 = self._register_title('S' * (CONFLUENCE_MAX_TITLE_LEN - 2))
        t1 = self._register_title('S' * (CONFLUENCE_MAX_TITLE_LEN - 1))
        t2 = self._register_title('S' * CONFLUENCE_MAX_TITLE_LEN)
        t3 = self._register_title('S' * (CONFLUENCE_MAX_TITLE_LEN + 1))

        self.assertEqual(len(t0), CONFLUENCE_MAX_TITLE_LEN - 1)
        self.assertEqual(len(t1), CONFLUENCE_MAX_TITLE_LEN)
        self.assertEqual(len(t2), CONFLUENCE_MAX_TITLE_LEN)
        self.assertEqual(len(t3), CONFLUENCE_MAX_TITLE_LEN)

    def test_titles_maximum_checks_prefix_and_postfix(self):
        self.config.confluence_publish_postfix = 'Z'
        self.config.confluence_publish_prefix = 'A'

        t0 = self._register_title('S' * (CONFLUENCE_MAX_TITLE_LEN - 3))
        t1 = self._register_title('S' * (CONFLUENCE_MAX_TITLE_LEN - 2))
        t2 = self._register_title('S' * (CONFLUENCE_MAX_TITLE_LEN - 1))
        t3 = self._register_title('S' * CONFLUENCE_MAX_TITLE_LEN)
        t4 = self._register_title('S' * (CONFLUENCE_MAX_TITLE_LEN + 1))

        self.assertEqual(len(t0), CONFLUENCE_MAX_TITLE_LEN - 1)
        self.assertEqual(len(t1), CONFLUENCE_MAX_TITLE_LEN)
        self.assertEqual(len(t2), CONFLUENCE_MAX_TITLE_LEN)
        self.assertEqual(len(t3), CONFLUENCE_MAX_TITLE_LEN)
        self.assertEqual(len(t4), CONFLUENCE_MAX_TITLE_LEN)

    def test_titles_prefix_and_postfix_not_truncated(self):
        self.config.confluence_publish_postfix = 'Z'
        self.config.confluence_publish_prefix = 'A'

        title = self._register_title('S' * CONFLUENCE_MAX_TITLE_LEN)

        self.assertEqual(len(title), CONFLUENCE_MAX_TITLE_LEN)
        self.assertEqual(title[0], 'A')
        self.assertEqual(title[-1], 'Z')

    def tearDown(self):
        ConfluenceState.reset()
