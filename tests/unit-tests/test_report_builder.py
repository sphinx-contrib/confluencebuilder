# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from sphinxcontrib.confluencebuilder.reportbuilder import ConfluenceReportBuilder
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder


class TestReportBuilder(ConfluenceTestCase):
    @setup_builder(ConfluenceReportBuilder.name)
    def test_report_builder(self):
        # sanity check that this builder can be prepared
        with self.prepare(self.datasets / 'minimal') as app:
            self.assertIsInstance(app.builder, ConfluenceReportBuilder)
