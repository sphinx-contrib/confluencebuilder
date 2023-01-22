# SPDX-License-Identifier: BSD-2-Clause
# Copyright 2020-2023 Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.testcase import ConfluenceTestCase
import os


class TestConfluenceConfigPrevNext(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'prevnext')

    def test_config_prevnext_bottom(self):
        config = dict(self.config)
        config['confluence_prev_next_buttons_location'] = 'bottom'

        out_dir = self.build(self.dataset, config=config)

        self._character_check('index',  out_dir, {'←': 0, '→': 1})
        self._character_check('middle', out_dir, {'←': 1, '→': 1})
        self._character_check('final',  out_dir, {'←': 1, '→': 0})

    def test_config_prevnext_both(self):
        config = dict(self.config)
        config['confluence_prev_next_buttons_location'] = 'both'

        out_dir = self.build(self.dataset, config=config)

        self._character_check('index',  out_dir, {'←': 0, '→': 2})
        self._character_check('middle', out_dir, {'←': 2, '→': 2})
        self._character_check('final',  out_dir, {'←': 2, '→': 0})

    def test_config_prevnext_none(self):
        config = dict(self.config)
        config['confluence_prev_next_buttons_location'] = None

        out_dir = self.build(self.dataset, config=config)

        self._character_check('index',  out_dir, {'←': 0, '→': 0})
        self._character_check('middle', out_dir, {'←': 0, '→': 0})
        self._character_check('final',  out_dir, {'←': 0, '→': 0})

    def test_config_prevnext_top(self):
        config = dict(self.config)
        config['confluence_prev_next_buttons_location'] = 'top'

        out_dir = self.build(self.dataset, config=config)

        self._character_check('index',  out_dir, {'←': 0, '→': 1})
        self._character_check('middle', out_dir, {'←': 1, '→': 1})
        self._character_check('final',  out_dir, {'←': 1, '→': 0})

    def _character_check(self, name, output, expected):
        test_path = os.path.join(output, name + '.conf')
        self.assertTrue(os.path.exists(test_path),
            f'missing output file: {test_path}')

        with open(test_path, encoding='utf8') as test_file:
            data = ''.join([o.strip() + '\n' for o in test_file.readlines()])
            for char, count in expected.items():
                found = data.count(char)
                self.assertTrue(data.count(char) == count,
                    'unexpected character ({}) count (expected: {}, found: {}) '
                    'in file: {}'.format(
                        hex(ord(char)), count, found, test_path))
