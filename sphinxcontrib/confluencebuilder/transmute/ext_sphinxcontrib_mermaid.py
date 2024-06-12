# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from docutils import nodes
from sphinxcontrib.confluencebuilder.compat import docutils_findall as findall
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger

# ##############################################################################
# disable import/except warnings for third-party modules
# pylint: disable=E

# load sphinxcontrib-mermaid extension if available
try:
    from sphinxcontrib.mermaid import MermaidError
    from sphinxcontrib.mermaid import mermaid
    from sphinxcontrib.mermaid import render_mm as mermaid_render
    sphinxcontrib_mermaid = True
except:  # noqa: E722
    sphinxcontrib_mermaid = False

# re-enable pylint warnings from above
# pylint: enable=E
# ##############################################################################


def replace_sphinxcontrib_mermaid_nodes(builder, doctree):
    """
    replace mermaid nodes with images

    mermaid nodes are pre-processed and replaced with respective images in the
    processed documentation set.

    Args:
        builder: the builder
        doctree: the doctree to replace blocks on
    """

    # allow users to disabled third-party implemented extension changes
    restricted = builder.config.confluence_adv_restricted
    if 'ext-sphinxcontrib.mermaid' in restricted:
        return

    if not sphinxcontrib_mermaid:
        return

    # mermaid's mermaid_render call expects a translator to be passed in; mock a
    # translator tied to our builder
    class MockTranslator:
        def __init__(self, builder):
            self.builder = builder
    mock_translator = MockTranslator(builder)

    for node in findall(doctree, mermaid):
        try:
            format_ = builder.config.mermaid_output_format
            if format_ == 'raw':
                format_ = 'png'

            fname, _ = mermaid_render(mock_translator,
                node['code'], node['options'], format_, 'mermaid')
            if not fname:
                node.parent.remove(node)
                continue

            new_node = nodes.image(candidates={'?'}, uri=fname)
            if 'align' in node:
                new_node['align'] = node['align']
            node.replace_self(new_node)
        except MermaidError as exc:
            ConfluenceLogger.warn('mermaid code %r: %s', node['code'], exc)
            node.parent.remove(node)
