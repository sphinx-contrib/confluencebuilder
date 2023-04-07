# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from sphinx.builders import Builder
from sphinxcontrib.confluencebuilder.config.checks import validate_configuration


class ConfluenceReportBuilder(Builder):
    name = 'internal-confluence-report'

    def init(self):
        validate_configuration(self)
        self.config.sphinx_verbosity = self.app.verbosity
