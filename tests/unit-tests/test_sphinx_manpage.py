# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2022 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os


class TestConfluenceSphinxManpage(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestConfluenceSphinxManpage, cls).setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'common')
        cls.filenames = [
            'manpage',
        ]

    @setup_builder('confluence')
    def test_storage_sphinx_manpage_config(self):
        config = dict(self.config)
        config['manpages_url'] = 'https://manpages.example.com/{path}'

        out_dir = self.build(self.dataset, config=config,
            filenames=self.filenames)

        with parse('manpage', out_dir) as data:
            em = data.find('em')
            self.assertIsNotNone(em)

            link = em.find('a', recursive=False)
            self.assertIsNotNone(link)
            self.assertTrue(link.has_attr('href'))
            self.assertEqual(link['href'], 'https://manpages.example.com/ls(1)')
            self.assertEqual(link.text, 'ls(1)')

    @setup_builder('confluence')
    def test_storage_sphinx_manpage_noconfig(self):
        out_dir = self.build(self.dataset, filenames=self.filenames)

        with parse('manpage', out_dir) as data:
            em = data.find('em')
            self.assertIsNotNone(em)
            self.assertEqual(em.text, 'ls(1)')

            link = data.find('a')
            self.assertIsNone(link)
