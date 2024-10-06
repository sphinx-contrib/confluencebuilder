# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.errors import SphinxWarning
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder


class ConfluenceDummyTestDirective(Directive):
    has_content = False

    def run(self):
        node = ConfluenceDummyTestNode()
        return [node]


class ConfluenceDummyTestNode(nodes.Element):
    pass


class TestConfluenceUnknownNode(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = cls.datasets / 'unknown'

    @setup_builder('confluence')
    def test_unknown_node_default_completion(self):
        """validate handling unknown nodes to completion"""
        #
        # Ensures we can run this builder with Sphinx using an unknown
        # node to completion. A document should be built with the missing
        # component, and no errors should result from this attempt.

        with self.prepare(self.dataset, relax=True) as app:
            self._setup_app(app)
            app.build()

    @setup_builder('confluence')
    def test_unknown_node_default_warning(self):
        """validate handling unknown nodes generate a warning"""
        #
        # Ensure that a user is properly informed when running Sphinx with
        # this extension that an unknown node has been detected.
        with self.prepare(self.dataset) as app:
            self._setup_app(app)

            with self.assertRaises(SphinxWarning):
                app.build()

    @setup_builder('confluence')
    def test_unknown_node_ignored(self):
        """validate overrides to ignore unknown nodes"""

        config = dict(self.config)
        config['confluence_adv_ignore_nodes'] = [
            'ConfluenceDummyTestNode',
        ]

        with self.prepare(self.dataset, config=config) as app:
            self._setup_app(app)

            app.build()
            self.assertEqual(app.statuscode, 0)

    def _setup_app(self, app):
        app.add_node(ConfluenceDummyTestNode)
        app.add_directive('confluence_test_dir', ConfluenceDummyTestDirective)
