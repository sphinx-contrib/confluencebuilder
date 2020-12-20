# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2019-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from __future__ import unicode_literals
from tests.lib import prepare_conf
from tests.lib import prepare_sphinx
import io
import os
import unittest

class TestConfluencePrevNext(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        test_dir = os.path.dirname(os.path.realpath(__file__))

        self.config = prepare_conf()
        self.dataset = os.path.join(test_dir, 'dataset-prevnext')
        self.expected = os.path.join(test_dir, 'expected')

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

    def test_legacy_prevnext_bottom(self):
        config = dict(self.config)
        config['confluence_prev_next_buttons_location'] = 'bottom'

        with prepare_sphinx(self.dataset, config=config) as app:
            app.build(force_all=True)
            self._character_check('index',  app.outdir, {'←': 0, '→': 1})
            self._character_check('middle', app.outdir, {'←': 1, '→': 1})
            self._character_check('final',  app.outdir, {'←': 1, '→': 0})

    def test_legacy_prevnext_both(self):
        config = dict(self.config)
        config['confluence_prev_next_buttons_location'] = 'both'

        with prepare_sphinx(self.dataset, config=config) as app:
            app.build(force_all=True)
            self._character_check('index',  app.outdir, {'←': 0, '→': 2})
            self._character_check('middle', app.outdir, {'←': 2, '→': 2})
            self._character_check('final',  app.outdir, {'←': 2, '→': 0})

    def test_legacy_prevnext_none(self):
        config = dict(self.config)
        config['confluence_prev_next_buttons_location'] = None

        with prepare_sphinx(self.dataset, config=config) as app:
            app.build(force_all=True)
            self._character_check('index',  app.outdir, {'←': 0, '→': 0})
            self._character_check('middle', app.outdir, {'←': 0, '→': 0})
            self._character_check('final',  app.outdir, {'←': 0, '→': 0})

    def test_legacy_prevnext_top(self):
        config = dict(self.config)
        config['confluence_prev_next_buttons_location'] = 'top'

        with prepare_sphinx(self.dataset, config=config) as app:
            app.build(force_all=True)
            self._character_check('index',  app.outdir, {'←': 0, '→': 1})
            self._character_check('middle', app.outdir, {'←': 1, '→': 1})
            self._character_check('final',  app.outdir, {'←': 1, '→': 0})
