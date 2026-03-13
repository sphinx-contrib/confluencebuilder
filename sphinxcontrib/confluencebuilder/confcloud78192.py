# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)
#
# https://github.com/sphinx-contrib/confluencebuilder/issues/1178
# https://jira.atlassian.com/browse/CONFCLOUD-78192

from docutils import nodes
from pathlib import Path
from sphinxcontrib.confluencebuilder.compat import docutils_findall as findall
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger as logger


def find_risked_delayed_anchor_pages(docname, doctree, track):
    """
    populate a list of at-risk pages with broken anchors on publishing

    There is a risk when a page is published to Confluence Cloud that the
    link may auto-drop its anchor value if the target page is not yet
    published. This is a result of a Confluence issue (CONFCLOUD-78192).
    In attempt to workaround this, we try to detect pages that may result
    in losing anchor values and try to later use this to re-publish pages
    to correct these links.

    Args:
        docname: the document being processed
        doctree: the doctree of the document
        track: dictionary tracking target pages to referencee pages
    """
    for node in findall(doctree, nodes.reference):
        # immediately rule out non-anchor uris or uris that are local anchors
        if 'refuri' not in node or '#' not in node['refuri'] \
                or node['refuri'].startswith('#'):
            continue

        # also ensure we either have a external document or non-internal hint
        if 'refdocname' not in node and not node.get('internal'):
            continue

        refuri = Path(node['refuri'].split('#')[0])
        target_docname = str(refuri.parent / refuri.stem)

        logger.verbose(f'anchor risk: : {docname} -> {target_docname}')
        track.setdefault(target_docname, set()).add(docname)
        break
