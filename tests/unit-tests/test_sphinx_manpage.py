# SPDX-License-Identifier: BSD-2-Clause
# Copyright 2016-2023 Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os


class TestConfluenceSphinxManpage(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestConfluenceSphinxManpage, cls).setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'manpage')

    @setup_builder('confluence')
    def test_storage_sphinx_manpage_config(self):
        config = dict(self.config)
        config['manpages_url'] = 'https://manpages.example.com/{path}'

        out_dir = self.build(self.dataset, config=config)

        with parse('index', out_dir) as data:
            em = data.find('em')
            self.assertIsNotNone(em)

            link = em.find('a', recursive=False)
            self.assertIsNotNone(link)
            self.assertTrue(link.has_attr('href'))
            self.assertEqual(link['href'], 'https://manpages.example.com/ls(1)')
            self.assertEqual(link.text, 'ls(1)')

    @setup_builder('confluence')
    def test_storage_sphinx_manpage_noconfig(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            em = data.find('em')
            self.assertIsNotNone(em)
            self.assertEqual(em.text, 'ls(1)')

            link = data.find('a')
            self.assertIsNone(link)
