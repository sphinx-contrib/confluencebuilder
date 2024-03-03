# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)
# Copyright 2007-2021 by the Sphinx team (sphinx-doc/sphinx#AUTHORS)

from docutils import __version_info__ as docutils_version_info
from docutils import nodes
from sphinx import addnodes
from sphinx.locale import __
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger as logger
from typing import cast


# use docutil's findall call over traverse (obsolete)
def docutils_findall(doctree, *args, **kwargs):
    if docutils_version_info >= (0, 18, 1):
        return doctree.findall(*args, **kwargs)

    return doctree.traverse(*args, **kwargs)


# use this extension's variant of sphinx's inline_all_toctrees which has
# include support for a `replace` argument
def inline_all_toctrees(builder, docnameset, docname, tree, colorfunc,
                        traversed, replace):
    tree = cast(nodes.document, tree.deepcopy())
    for toctreenode in list(docutils_findall(tree, addnodes.toctree)):
        newnodes = []
        includefiles = map(str, toctreenode['includefiles'])
        for includefile in includefiles:
            if includefile not in traversed:
                try:
                    traversed.append(includefile)
                    logger.info(colorfunc(includefile) + " ", nonl=True)
                    subtree = inline_all_toctrees(
                        builder, docnameset, includefile,
                        builder.env.get_doctree(includefile),
                        colorfunc, traversed, replace)
                    docnameset.add(includefile)
                except Exception:  # noqa: BLE001
                    logger.warn(
                        __('toctree contains ref to nonexisting file %r'),
                        includefile, location=docname)
                else:
                    sof = addnodes.start_of_file(docname=includefile)
                    sof.children = subtree.children
                    for sectionnode in docutils_findall(sof, nodes.section):
                        if 'docname' not in sectionnode:
                            sectionnode['docname'] = includefile
                    newnodes.append(sof)

        if replace:
            toctreenode.parent.replace(toctreenode, newnodes)
        else:
            for node in newnodes:
                toctreenode.parent.append(node)

    return tree
