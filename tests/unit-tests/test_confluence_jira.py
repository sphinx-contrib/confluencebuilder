# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2019-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from sphinx.errors import SphinxWarning
from tests.lib import build_sphinx
from tests.lib import parse
from tests.lib import prepare_conf
import os
import unittest

class TestConfluenceJira(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.container = os.path.join(test_dir, 'datasets', 'jira')

    def test_confluence_jira_directive_bad_sid(self):
        dataset = os.path.join(self.container, 'bad-sid')

        with self.assertRaises(SphinxWarning):
            build_sphinx(dataset, config=self.config)

    def test_confluence_jira_directive_conflicting_server_id(self):
        dataset = os.path.join(self.container, 'conflicting-server-id')

        with self.assertRaises(SphinxWarning):
            build_sphinx(dataset, config=self.config)

    def test_confluence_jira_directive_conflicting_server_name(self):
        dataset = os.path.join(self.container, 'conflicting-server-name')

        with self.assertRaises(SphinxWarning):
            build_sphinx(dataset, config=self.config)

    def test_confluence_jira_directive_missing_server_entry(self):
        dataset = os.path.join(self.container, 'missing-server-entry')

        with self.assertRaises(SphinxWarning):
            build_sphinx(dataset, config=self.config)

    def test_confluence_jira_directive_missing_server_id(self):
        dataset = os.path.join(self.container, 'missing-server-id')

        with self.assertRaises(SphinxWarning):
            build_sphinx(dataset, config=self.config)

    def test_confluence_jira_directive_missing_server_name(self):
        dataset = os.path.join(self.container, 'missing-server-name')

        with self.assertRaises(SphinxWarning):
            build_sphinx(dataset, config=self.config)

    def test_storage_confluence_jira_directive_expected(self):
        dataset = os.path.join(self.container, 'valid')

        config = dict(self.config)
        config['confluence_jira_servers'] = {
            'test-jira-server': {
                'name': 'test-server-name',
                'id': '00000000-1234-0000-5678-000000000009',
            }
        }

        out_dir = build_sphinx(dataset, config=config)

        with parse('index', out_dir) as data:
            jira_macros = data.find_all('ac:structured-macro',
                {'ac:name': 'jira'})
            self.assertIsNotNone(jira_macros)
            self.assertEqual(len(jira_macros), 3)

            # jira_issue
            jira_macro = jira_macros.pop(0)

            key = jira_macro.find('ac:parameter', {'ac:name': 'key'})
            self.assertIsNotNone(key)
            self.assertEqual(key.text, 'TEST-123')

            # jira
            jira_macro = jira_macros.pop(0)

            cols = jira_macro.find('ac:parameter', {'ac:name': 'columns'})
            self.assertIsNotNone(cols)
            self.assertEqual(cols.text, 'key,summary,updated,status,resolution')

            count = jira_macro.find('ac:parameter', {'ac:name': 'count'})
            self.assertIsNotNone(count)
            self.assertEqual(count.text, 'false')

            jql = jira_macro.find('ac:parameter', {'ac:name': 'jqlQuery'})
            self.assertIsNotNone(jql)
            self.assertEqual(jql.text, 'project = "TEST"')

            max = jira_macro.find('ac:parameter', {'ac:name': 'maximumIssues'})
            self.assertIsNotNone(max)
            self.assertEqual(max.text, '5')

            sname = jira_macro.find('ac:parameter', {'ac:name': 'server'})
            self.assertIsNotNone(sname)
            self.assertEqual(sname.text, 'test-server-name')

            sid = jira_macro.find('ac:parameter', {'ac:name': 'serverId'})
            self.assertIsNotNone(sid)
            self.assertEqual(sid.text, '00000000-1234-0000-5678-000000000009')

            # jira_issue (server override)
            jira_macro = jira_macros.pop(0)

            key = jira_macro.find('ac:parameter', {'ac:name': 'key'})
            self.assertIsNotNone(key)
            self.assertEqual(key.text, 'TEST-1')

            sname = jira_macro.find('ac:parameter', {'ac:name': 'server'})
            self.assertIsNotNone(sname)
            self.assertEqual(sname.text, 'overwritten-server-name')

            sid = jira_macro.find('ac:parameter', {'ac:name': 'serverId'})
            self.assertIsNotNone(sid)
            self.assertEqual(sid.text, '00000000-0000-9876-0000-000000000000')

    def test_storage_confluence_jira_directive_ignore(self):
        dataset = os.path.join(self.container, 'valid')
        opts = {
            'builder': 'html',
            'config': self.config,
            'relax': True,
        }

        # build attempt should not throw an exception/error
        build_sphinx(dataset, **opts)
