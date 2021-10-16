# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

import os
import unittest

from tests.lib import build_sphinx, parse, prepare_conf


class TestConfluenceSphinxManpage(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset = os.path.join(test_dir, 'datasets', 'common')
        self.filenames = [
            'manpage',
        ]

    def test_storage_sphinx_manpage_config(self):
        config = dict(self.config)
        config['manpages_url'] = 'https://manpages.example.com/{path}'

        out_dir = build_sphinx(self.dataset, config=config,
            filenames=self.filenames)

        with parse('manpage', out_dir) as data:
            em = data.find('em')
            self.assertIsNotNone(em)

            link = em.find('a', recursive=False)
            self.assertIsNotNone(link)
            self.assertTrue(link.has_attr('href'))
            self.assertEqual(link['href'], 'https://manpages.example.com/ls(1)')
            self.assertEqual(link.text, 'ls(1)')

    def test_storage_sphinx_manpage_noconfig(self):
        out_dir = build_sphinx(self.dataset, config=self.config,
            filenames=self.filenames)

        with parse('manpage', out_dir) as data:
            em = data.find('em')
            self.assertIsNotNone(em)
            self.assertEqual(em.text, 'ls(1)')

            link = data.find('a')
            self.assertIsNone(link)
