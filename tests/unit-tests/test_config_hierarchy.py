# SPDX-License-Identifier: BSD-2-Clause
# Copyright 2017-2023 Sphinx Confluence Builder Contributors (AUTHORS)

from sphinxcontrib.confluencebuilder.state import ConfluenceState
from tests.lib.testcase import ConfluenceTestCase
import os


class TestConfluenceHierarchy(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'hierarchy')

    def test_config_hierarchy_parent_registration_default(self):
        ConfluenceState.reset()
        self.build(self.dataset, relax=True)

        # root toctree should not have a parent
        root_doc = ConfluenceState.parent_docname('index')
        self.assertIsNone(root_doc)

        # check various documents for expected parents
        parent_doc = ConfluenceState.parent_docname('toctree-doc1')
        self.assertEqual(parent_doc, 'index')

        parent_doc = ConfluenceState.parent_docname('toctree-doc2')
        self.assertEqual(parent_doc, 'index')

        parent_doc = ConfluenceState.parent_docname('toctree-doc3')
        self.assertEqual(parent_doc, 'index')

        parent_doc = ConfluenceState.parent_docname('toctree-doc2a')
        self.assertEqual(parent_doc, 'toctree-doc2')
