# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from sphinx.builders import Builder

from sphinxcontrib.confluencebuilder.config.checks import validate_configuration


class ConfluenceReportBuilder(Builder):
    name = "internal-confluence-report"

    def __init__(self, app):
        super(ConfluenceReportBuilder, self).__init__(app)

    def init(self):
        validate_configuration(self)
        self.config.sphinx_verbosity = self.app.verbosity
