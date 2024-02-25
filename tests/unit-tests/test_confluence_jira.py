# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from sphinx.errors import SphinxWarning


class TestConfluenceJira(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.container = cls.datasets / 'jira'

    def test_confluence_jira_directive_bad_sid(self):
        dataset = self.container / 'bad-sid'

        with self.assertRaises(SphinxWarning):
            self.build(dataset)

    def test_confluence_jira_directive_conflicting_server_id(self):
        dataset = self.container / 'conflicting-server-id'

        with self.assertRaises(SphinxWarning):
            self.build(dataset)

    def test_confluence_jira_directive_conflicting_server_name(self):
        dataset = self.container / 'conflicting-server-name'

        with self.assertRaises(SphinxWarning):
            self.build(dataset)

    def test_confluence_jira_directive_missing_server_entry(self):
        dataset = self.container / 'missing-server-entry'

        with self.assertRaises(SphinxWarning):
            self.build(dataset)

    def test_confluence_jira_directive_missing_server_id(self):
        dataset = self.container / 'missing-server-id'

        with self.assertRaises(SphinxWarning):
            self.build(dataset)

    def test_confluence_jira_directive_missing_server_name(self):
        dataset = self.container / 'missing-server-name'

        with self.assertRaises(SphinxWarning):
            self.build(dataset)

    @setup_builder('html')
    def test_html_confluence_jira_directive_ignore(self):
        dataset = self.container / 'valid'

        # build attempt should not throw an exception/error
        self.build(dataset, relax=True)

    @setup_builder('confluence')
    def test_storage_confluence_jira_directive_expected(self):
        dataset = self.container / 'valid'

        config = dict(self.config)
        config['confluence_jira_servers'] = {
            'test-jira-server': {
                'name': 'test-server-name',
                'id': '00000000-1234-0000-5678-000000000009',
            },
        }

        out_dir = self.build(dataset, config=config)

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

            max_issues = jira_macro.find(
                'ac:parameter', {'ac:name': 'maximumIssues'})
            self.assertIsNotNone(max_issues)
            self.assertEqual(max_issues.text, '5')

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

    @setup_builder('confluence')
    def test_storage_confluence_jira_role_default_expected(self):
        dataset = self.container / 'valid-role'

        out_dir = self.build(dataset)

        with parse('index', out_dir) as data:
            p_tag = data.find('p')
            self.assertIsNotNone(p_tag)

            macro = p_tag.find('ac:structured-macro', {'ac:name': 'jira'})
            self.assertIsNotNone(macro)

            key = macro.find('ac:parameter', {'ac:name': 'key'})
            self.assertIsNotNone(key)
            self.assertEqual(key.text, 'TEST-456')

            summary = macro.find('ac:parameter', {'ac:name': 'showSummary'})
            self.assertIsNotNone(summary)
            self.assertEqual(summary.text, 'false')

    @setup_builder('confluence')
    def test_storage_confluence_jira_substitution_expected(self):
        dataset = self.container / 'valid-substitution'

        out_dir = self.build(dataset)

        with parse('index', out_dir) as data:
            jira_macros = data.find_all('ac:structured-macro',
                {'ac:name': 'jira'})
            self.assertIsNotNone(jira_macros)
            self.assertEqual(len(jira_macros), 3)

            # jira_issue substitution
            jira_macro = jira_macros.pop(0)

            key = jira_macro.find('ac:parameter', {'ac:name': 'key'})
            self.assertIsNotNone(key)
            self.assertEqual(key.text, 'TEST-1')

            # jira substitution
            jira_macro = jira_macros.pop(0)

            cols = jira_macro.find('ac:parameter', {'ac:name': 'columns'})
            self.assertIsNotNone(cols)
            self.assertEqual(cols.text, 'key,summary,status,resolution')

            count = jira_macro.find('ac:parameter', {'ac:name': 'count'})
            self.assertIsNotNone(count)
            self.assertEqual(count.text, 'false')

            jql = jira_macro.find('ac:parameter', {'ac:name': 'jqlQuery'})
            self.assertIsNotNone(jql)
            self.assertEqual(jql.text, 'project = "TESTPRJ"')

            max_issues = jira_macro.find(
                'ac:parameter', {'ac:name': 'maximumIssues'})
            self.assertIsNotNone(max_issues)
            self.assertEqual(max_issues.text, '8')

            # jira (role) substitution
            jira_macro = jira_macros.pop(0)

            key = jira_macro.find('ac:parameter', {'ac:name': 'key'})
            self.assertIsNotNone(key)
            self.assertEqual(key.text, 'TEST-2')
