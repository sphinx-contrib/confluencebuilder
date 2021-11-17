# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020-2021 Sphinx Confluence Builder Contributors (AUTHORS)
:copyright: Copyright 2007-2021 by the Sphinx team (sphinx-doc/sphinx#AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from __future__ import absolute_import
from docutils import nodes
from sphinx import addnodes
from sphinx import version_info as sphinx_version_info
from sphinx.locale import __
from sphinx.util.console import bold  # pylint: disable=no-name-in-module
from sphinx.util.nodes import inline_all_toctrees as sphinx_inline_all_toctrees
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger as logger
from typing import cast

# input support with all supported python interpreters
try:
    input = raw_input
except NameError:
    input = input  # pylint: disable=W0127

# load sphinx's progress_message or use a compatible instance
try:
    from sphinx.util import progress_message  # pylint: disable=W0611
except ImportError:
    class progress_message:
        def __init__(self, msg):
            self.msg = msg

        def __enter__(self):
            logger.info(bold(self.msg + '... '), nonl=True)

        def __exit__(self, type_, value, traceback):
            if type_:
                logger.info(__('failed'))
            else:
                logger.info(__('done'))


# use sphinx's inline_all_toctrees which supports the `replace` argument;
# otherwise, use this local variant instead
def inline_all_toctrees(builder, docnameset, docname, tree, colorfunc,
                        traversed, replace):
    # TODO: https://github.com/sphinx-doc/sphinx/pull/9839
    if False and sphinx_version_info > (4, 4):
        return sphinx_inline_all_toctrees(builder,  # pylint: disable=E1123
            docnameset, docname, tree, colorfunc, traversed, replace=replace)
    else:
        return _inline_all_toctrees(builder, docnameset, docname, tree,
            colorfunc, traversed, replace)


def _inline_all_toctrees(builder, docnameset, docname, tree, colorfunc,
                        traversed, replace):
    tree = cast(nodes.document, tree.deepcopy())
    for toctreenode in list(tree.traverse(addnodes.toctree)):
        newnodes = []
        includefiles = map(str, toctreenode['includefiles'])
        for includefile in includefiles:
            if includefile not in traversed:
                try:
                    traversed.append(includefile)
                    logger.info(colorfunc(includefile) + " ", nonl=True)
                    subtree = _inline_all_toctrees(
                        builder, docnameset, includefile,
                        builder.env.get_doctree(includefile),
                        colorfunc, traversed, replace)
                    docnameset.add(includefile)
                except Exception:
                    logger.warn(
                        __('toctree contains ref to nonexisting file %r'),
                        includefile, location=docname)
                else:
                    sof = addnodes.start_of_file(docname=includefile)
                    sof.children = subtree.children
                    for sectionnode in sof.traverse(nodes.section):
                        if 'docname' not in sectionnode:
                            sectionnode['docname'] = includefile
                    newnodes.append(sof)

        if replace:
            toctreenode.parent.replace(toctreenode, newnodes)
        else:
            for node in newnodes:
                toctreenode.parent.append(node)

    return tree
