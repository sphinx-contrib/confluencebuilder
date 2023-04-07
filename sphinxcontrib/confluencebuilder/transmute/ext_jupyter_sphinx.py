# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from sphinxcontrib.confluencebuilder.compat import docutils_findall as findall

# ##############################################################################
# disable import/except warnings for third-party modules
# pylint: disable=E

# load jupyter_sphinx extension if available
try:
    from jupyter_sphinx.ast import CellOutputNode as jupyter_celloutputnode
    from jupyter_sphinx.ast import MimeBundleNode as jupyter_mimebundlenode
    jupyter_sphinx = True
except:  # noqa: E722
    jupyter_sphinx = False

# re-enable pylint warnings from above
# pylint: enable=E
# ##############################################################################


def replace_jupyter_sphinx_nodes(builder, doctree):
    """
    replace jupyter-sphinx nodes

    jupyter-sphinx nodes are pre-processed and replaced with compatible nodes
    in the processed documentation set.

    Args:
        builder: the builder
        doctree: the doctree to replace blocks on
    """

    # allow users to disabled third-party implemented extension changes
    restricted = builder.config.confluence_adv_restricted
    if 'ext-jupyter' in restricted:
        return

    if not jupyter_sphinx:
        return

    # replace mime bundle nodes with already-prepared Confluence LaTeX nodes;
    # this allows a translator to directly process a Confluence LaTeX node in
    # cell output node (or an image, if Confluence LaTeX nodes have been
    # transformed)
    for base in findall(doctree, jupyter_celloutputnode):
        for node in base.findall(jupyter_mimebundlenode):
            mimetypes = node.get('mimetypes', [])
            if 'text/latex' in mimetypes:
                idx = node['mimetypes'].index('text/latex')
                base.replace(node, node[idx])
