# SPDX-License-Identifier: BSD-2-Clause
# Copyright 2020-2023 Sphinx Confluence Builder Contributors (AUTHORS)
# Copyright 2007-2021 by the Sphinx team (sphinx-doc/sphinx#AUTHORS)

from docutils import __version_info__ as docutils_version_info
from docutils import nodes
from sphinx import addnodes
from sphinx import version_info as sphinx_version_info
from sphinx.locale import __
from sphinx.util.nodes import inline_all_toctrees as sphinx_inline_all_toctrees
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger as logger
from typing import cast

# pylint: disable=no-name-in-module
if sphinx_version_info >= (6, 1):
    from sphinx.util.display import status_iterator  # noqa: F401
    from sphinx.util.display import progress_message  # noqa: F401
else:
    from sphinx.util import status_iterator  # noqa: F401
    from sphinx.util import progress_message  # noqa: F401
# pylint: enable=no-name-in-module


# use docutil's findall call over traverse (obsolete)
def docutils_findall(doctree, *args, **kwargs):
    if docutils_version_info >= (0, 18, 1):
        return doctree.findall(*args, **kwargs)
    else:
        return doctree.traverse(*args, **kwargs)


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
    for toctreenode in list(docutils_findall(tree, addnodes.toctree)):
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
