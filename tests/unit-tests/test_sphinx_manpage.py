# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib import build_sphinx
from tests.lib import parse
from tests.lib import prepare_conf
import os
import unittest


class TestConfluenceSphinxManpage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        cls.dataset = os.path.join(test_dir, 'datasets', 'common')
        cls.filenames = [
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
