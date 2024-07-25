# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from docutils import nodes
from sphinxcontrib.confluencebuilder.compat import docutils_findall as findall

# ##############################################################################
# disable import/except warnings for third-party modules
# pylint: disable=E

# load sphinx-gallery extension if available
try:
    from sphinx_gallery.directives import imgsgnode as sphinx_gallery_imgsgnode
    has_sphinx_gallery = True
except:  # noqa: E722
    has_sphinx_gallery = False

# re-enable pylint warnings from above
# pylint: enable=E
# ##############################################################################


def replace_sphinx_gallery_nodes(builder, doctree):
    """
    replace sphinx-gallery nodes with images

    sphinx-gallery nodes are pre-processed and replaced with respective images
    in the processed documentation set.

    Args:
        builder: the builder
        doctree: the doctree to replace blocks on
    """

    # allow users to disabled third-party implemented extension changes
    restricted = builder.config.confluence_adv_restricted
    if 'ext-sphinx_gallery' in restricted:
        return

    if not has_sphinx_gallery:
        return

    for node in findall(doctree, sphinx_gallery_imgsgnode):
        new_node = nodes.image(candidates={'?'}, **node.attributes)
        if 'align' in node:
            new_node['align'] = node['align']
        node.replace_self(new_node)
