# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

import os
import unittest

from tests.lib import build_sphinx, parse, prepare_conf


class TestConfluenceRstFootnotes(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset = os.path.join(test_dir, 'datasets', 'common')
        self.filenames = [
            'footnotes',
        ]

    def test_storage_rst_footnotes(self):
        out_dir = build_sphinx(self.dataset, config=self.config,
            filenames=self.filenames)

        with parse('footnotes', out_dir) as data:
            # ##########################################################
            # footnotes
            # ##########################################################

            footnote_link_containers = data.find_all('sup')
            self.assertEqual(len(footnote_link_containers), 3)

            # footnote a
            container = footnote_link_containers.pop(0)
            ac_link = container.find('ac:link')
            self.assertIsNotNone(ac_link)

            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'id5')

            link_body = ac_link.find('ac:plain-text-link-body')
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, '[1]')

            # leader anchor back to this footnote a
            anchor_tag = container.find_previous_sibling()
            self.assertIsNotNone(anchor_tag)
            self.assertEqual(anchor_tag.name, 'ac:structured-macro')
            self.assertTrue(anchor_tag.has_attr('ac:name'))
            self.assertEqual(anchor_tag['ac:name'], 'anchor')

            anchor_param = anchor_tag.find('ac:parameter', recursive=False)
            self.assertIsNotNone(anchor_param)
            self.assertEqual(anchor_param.text, 'id1')

            # footnote b
            container = footnote_link_containers.pop(0)
            ac_link = container.find('ac:link')
            self.assertIsNotNone(ac_link)

            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'note')

            link_body = ac_link.find('ac:plain-text-link-body')
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, '[3]') # 3 since 2 was pre-reserved

            # leader anchor back to this footnote b
            anchor_tag = container.find_previous_sibling()
            self.assertIsNotNone(anchor_tag)
            self.assertEqual(anchor_tag.name, 'ac:structured-macro')
            self.assertTrue(anchor_tag.has_attr('ac:name'))
            self.assertEqual(anchor_tag['ac:name'], 'anchor')

            anchor_param = anchor_tag.find('ac:parameter', recursive=False)
            self.assertIsNotNone(anchor_param)
            self.assertEqual(anchor_param.text, 'id2')

            # footnote c
            container = footnote_link_containers.pop(0)
            ac_link = container.find('ac:link')
            self.assertIsNotNone(ac_link)

            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'id4')

            link_body = ac_link.find('ac:plain-text-link-body')
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, '[2]')

            # leader anchor back to this footnote 3
            anchor_tag = container.find_previous_sibling()
            self.assertIsNotNone(anchor_tag)
            self.assertEqual(anchor_tag.name, 'ac:structured-macro')
            self.assertTrue(anchor_tag.has_attr('ac:name'))
            self.assertEqual(anchor_tag['ac:name'], 'anchor')

            anchor_param = anchor_tag.find('ac:parameter', recursive=False)
            self.assertIsNotNone(anchor_param)
            self.assertEqual(anchor_param.text, 'id3')

            # ##########################################################
            # footnote table
            # ##########################################################

            footnote_table = data.find('table')
            self.assertIsNotNone(footnote_table)

            footnote_rows = footnote_table.find_all('tr')
            self.assertEqual(len(footnote_rows), 3)

            # footnote a
            tds = footnote_rows[0].find_all('td', recursive=False)
            self.assertEqual(len(tds), 2)

            anchor_tag = tds[0].find('ac:structured-macro',
                {'ac:name': 'anchor'})
            self.assertIsNotNone(anchor_tag)
            anchor_param = anchor_tag.find('ac:parameter')
            self.assertIsNotNone(anchor_param)
            self.assertEqual(anchor_param.text, 'id4')

            ac_link = tds[0].find('ac:link')
            self.assertIsNotNone(ac_link)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'id3')
            link_body = ac_link.find('ac:plain-text-link-body')
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, '2')

            self.assertEqual(tds[1].text.strip(), 'footnote 2')

            # footnote b
            tds = footnote_rows[1].find_all('td', recursive=False)
            self.assertEqual(len(tds), 2)

            anchor_tag = tds[0].find('ac:structured-macro',
                {'ac:name': 'anchor'})
            self.assertIsNotNone(anchor_tag)
            anchor_param = anchor_tag.find('ac:parameter')
            self.assertIsNotNone(anchor_param)
            self.assertEqual(anchor_param.text, 'id5')

            ac_link = tds[0].find('ac:link')
            self.assertIsNotNone(ac_link)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'id1')
            link_body = ac_link.find('ac:plain-text-link-body')
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, '1')

            self.assertEqual(tds[1].text.strip(), 'footnote num')

            # footnote c
            tds = footnote_rows[2].find_all('td', recursive=False)
            self.assertEqual(len(tds), 2)

            anchor_tag = tds[0].find('ac:structured-macro',
                {'ac:name': 'anchor'})
            self.assertIsNotNone(anchor_tag)
            anchor_param = anchor_tag.find('ac:parameter')
            self.assertIsNotNone(anchor_param)
            self.assertEqual(anchor_param.text, 'note')

            ac_link = tds[0].find('ac:link')
            self.assertIsNotNone(ac_link)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'id2')
            link_body = ac_link.find('ac:plain-text-link-body')
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, '3')

            self.assertEqual(tds[1].text.strip(), 'footnote note')
