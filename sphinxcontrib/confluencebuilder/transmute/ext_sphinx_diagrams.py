# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from docutils import nodes
from sphinxcontrib.confluencebuilder.compat import docutils_findall as findall
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger

# ##############################################################################
# disable import/except warnings for third-party modules
# pylint: disable=E

# load sphinx-diagrams extension if available
try:
    from sphinx_diagrams import DiagramsError
    from sphinx_diagrams import diagrams as sphinx_diagrams_diagrams
    from sphinx_diagrams import render_diagrams as sphinx_diagrams_render
    has_sphinx_diagrams = True
except:  # noqa: E722
    has_sphinx_diagrams = False

# re-enable pylint warnings from above
# pylint: enable=E
# ##############################################################################


def replace_sphinx_diagrams_nodes(builder, doctree):
    """
    replace sphinx-diagrams nodes with images

    sphinx-diagrams nodes are pre-processed and replaced with respective images
    in the processed documentation set.

    Args:
        builder: the builder
        doctree: the doctree to replace blocks on
    """

    # allow users to disabled third-party implemented extension changes
    restricted = builder.config.confluence_adv_restricted
    if 'ext-sphinx_diagrams' in restricted:
        return

    if not has_sphinx_diagrams:
        return

    # sphinx-diagrams's render call expects a translator to be passed in;
    # mock a translator tied to our builder
    class MockTranslator:
        def __init__(self, builder):
            self.builder = builder
    mock_translator = MockTranslator(builder)

    for node in findall(doctree, sphinx_diagrams_diagrams):
        try:
            fname, _ = sphinx_diagrams_render(mock_translator,
                node['code'], node['options'], 'diagrams')
            if not fname:
                node.parent.remove(node)
                continue

            new_node = nodes.image(candidates={'?'}, uri=fname)
            if 'align' in node:
                new_node['align'] = node['align']

            new_container = nodes.paragraph()
            new_container.append(new_node)

            node.replace_self(new_container)
        except DiagramsError as exc:
            ConfluenceLogger.warn('diagrams code %r: %s', node['code'], exc)
            node.parent.remove(node)
