# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020-2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from __future__ import unicode_literals
from tests.lib import build_sphinx
from tests.lib import prepare_conf
import io
import os
import unittest


class TestConfluenceConfigPrevNext(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset = os.path.join(test_dir, 'datasets', 'prevnext')

    def test_config_prevnext_bottom(self):
        config = dict(self.config)
        config['confluence_prev_next_buttons_location'] = 'bottom'

        out_dir = build_sphinx(self.dataset, config=config)

        self._character_check('index',  out_dir, {'←': 0, '→': 1})
        self._character_check('middle', out_dir, {'←': 1, '→': 1})
        self._character_check('final',  out_dir, {'←': 1, '→': 0})

    def test_config_prevnext_both(self):
        config = dict(self.config)
        config['confluence_prev_next_buttons_location'] = 'both'

        out_dir = build_sphinx(self.dataset, config=config)

        self._character_check('index',  out_dir, {'←': 0, '→': 2})
        self._character_check('middle', out_dir, {'←': 2, '→': 2})
        self._character_check('final',  out_dir, {'←': 2, '→': 0})

    def test_config_prevnext_none(self):
        config = dict(self.config)
        config['confluence_prev_next_buttons_location'] = None

        out_dir = build_sphinx(self.dataset, config=config)

        self._character_check('index',  out_dir, {'←': 0, '→': 0})
        self._character_check('middle', out_dir, {'←': 0, '→': 0})
        self._character_check('final',  out_dir, {'←': 0, '→': 0})

    def test_config_prevnext_top(self):
        config = dict(self.config)
        config['confluence_prev_next_buttons_location'] = 'top'

        out_dir = build_sphinx(self.dataset, config=config)

        self._character_check('index',  out_dir, {'←': 0, '→': 1})
        self._character_check('middle', out_dir, {'←': 1, '→': 1})
        self._character_check('final',  out_dir, {'←': 1, '→': 0})

    def _character_check(self, name, output, expected):
        test_path = os.path.join(output, name + '.conf')
        self.assertTrue(os.path.exists(test_path),
            'missing output file: {}'.format(test_path))

        with io.open(test_path, encoding='utf8') as test_file:
            data = ''.join([o.strip() + '\n' for o in test_file.readlines()])
            for char, count in expected.items():
                found = data.count(char)
                self.assertTrue(data.count(char) == count,
                    'unexpected character ({}) count (expected: {}, found: {}) '
                    'in file: {}'.format(
                        hex(ord(char)), count, found, test_path))
