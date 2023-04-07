# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from docutils import nodes
from sphinxcontrib.confluencebuilder.compat import docutils_findall as findall
import itertools

# ##############################################################################
# disable import/except warnings for third-party modules
# pylint: disable=E

# load nbsphinx extension if available
try:
    from nbsphinx import CodeAreaNode as nbsphinx_codeareanode
    from nbsphinx import FancyOutputNode as nbsphinx_fancyoutputnode
    nbsphinx = True
except:  # noqa: E722
    nbsphinx = False

# re-enable pylint warnings from above
# pylint: enable=E
# ##############################################################################


def replace_nbsphinx_nodes(builder, doctree):
    """
    replace nbsphinx nodes

    nbsphinx nodes are pre-processed and replaced with compatible nodes
    in the processed documentation set.

    Args:
        builder: the builder
        doctree: the doctree to replace blocks on
    """

    # allow users to disabled third-party implemented extension changes
    restricted = builder.config.confluence_adv_restricted
    if 'ext-nbsphinx' in restricted:
        return

    if not nbsphinx:
        return

    for node in itertools.chain(findall(doctree, nbsphinx_codeareanode),
            findall(doctree, nbsphinx_fancyoutputnode)):

        for raw_node in node.findall(nodes.raw):
            if 'text' in raw_node.get('format', '').split():
                new_node = nodes.literal_block(
                    raw_node.astext(), raw_node.astext(), language='none')
                raw_node.replace_self(new_node)
