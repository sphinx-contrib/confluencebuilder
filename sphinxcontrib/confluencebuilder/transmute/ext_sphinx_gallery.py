# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from docutils import nodes

# ##############################################################################
# disable import/except warnings for third-party modules
# pylint: disable=E

# load sphinx-gallery extension if available
try:
    from sphinx_gallery.directives import imgsgnode as sphinx_gallery_imgsgnode
    sphinx_gallery = True
except:  # noqa: E722
    sphinx_gallery = False

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

    if not sphinx_gallery:
        return

    for node in doctree.traverse(sphinx_gallery_imgsgnode):
        new_node = nodes.image(candidates={'?'}, **node.attributes)
        if 'align' in node:
            new_node['align'] = node['align']
        node.replace_self(new_node)
