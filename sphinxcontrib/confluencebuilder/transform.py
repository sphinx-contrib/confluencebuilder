# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)
# Copyright 2024 by the Sphinx team (sphinx-doc/sphinx#AUTHORS)

from __future__ import annotations
from sphinx.builders.linkcheck import CheckExternalLinksBuilder
from sphinx.builders.linkcheck import Hyperlink
from sphinx.builders.linkcheck import HyperlinkCollector
from sphinx.util.nodes import get_node_line
from sphinxcontrib.confluencebuilder.nodes import confluence_doc_card
from sphinxcontrib.confluencebuilder.nodes import confluence_link_card
from sphinxcontrib.confluencebuilder.nodes import confluence_link_card_inline
from typing import TYPE_CHECKING
from typing import cast

if TYPE_CHECKING:
    from typing import Any


# The Confluence-specific hyperlink collector is based on Sphinx's
# implementation (sphinx/builders/linkcheck.py). We use the same transform
# definition, and override the `run` implementation to inject
# Confluence-specific links into the transform (which in turn adds them into
# the check-link builder).
class ConfluenceHyperlinkCollector(HyperlinkCollector):
    default_priority = HyperlinkCollector.default_priority + 1

    def run(self, **kwargs: Any) -> None:
        app = self.app
        builder = cast(CheckExternalLinksBuilder, app.builder)
        hyperlinks = builder.hyperlinks
        docname = self.env.docname

        def is_confluence_href_node(node):
            return isinstance(node, (
                confluence_doc_card,
                confluence_link_card,
                confluence_link_card_inline,
            ))

        for refnode in self.document.findall(is_confluence_href_node):
            uri = refnode['confluence-params']['href']

            if newuri := app.emit_firstresult('linkcheck-process-uri', uri):
                uri = newuri

            try:
                lineno = get_node_line(refnode)
            except ValueError:
                lineno = -1

            if uri not in hyperlinks:
                hyperlinks[uri] = Hyperlink(
                    uri, docname, self.env.doc2path(docname), lineno)
