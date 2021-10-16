# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2017-2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger

"""
maximum length for a confluence page title

The maximum length of a Confluence page is set to 255. This is a Confluence-
imposed limitation [1].

[1]: confluence-project/confluence-core/confluence/src/java/com/atlassian/confluence/pages/AbstractPage::isValidTitleLength
"""
CONFLUENCE_MAX_TITLE_LEN = 255


class ConfluenceState:
    """
    confluence state tracking

    This class is used to track the state of a Confluence building/publishing
    operation. This includes, but not limited to, remember title names for
    documents, tracking reference identifiers to other document names and more.
    """

    doc2uploadId = {}
    doc2parentDoc = {}
    doc2title = {}
    doc2ttd = {}
    refid2target = {}
    title2doc = {}

    @staticmethod
    def registerParentDocname(docname, parent_docname):
        """
        register a parent docname for a provided docname

        When using Sphinx's toctree, documents defined in the tree can be
        considered child pages (see the configuration option
        'confluence_page_hierarchy'). This method helps track a parent document
        for a provided child document. With the ability to track a parent
        document and track publish upload identifiers (see `registerUploadId`),
        the publish operation can help ensure pages are structured in a
        hierarchical fashion (see also `parentDocname`).

        [1]: http://www.sphinx-doc.org/en/stable/markup/toctree.html#directive-toctree
        """
        ConfluenceState.doc2parentDoc[docname] = parent_docname
        ConfluenceLogger.verbose(
            "setting parent of %s to: %s" % (docname, parent_docname)
        )

    @staticmethod
    def registerTarget(refid, target):
        """
        register a reference to a specific (anchor) target

        When interpreting a reference in reStructuredText, the reference could
        point to an anchor in the same document, another document or an anchor
        in another document. In Confluence, the target name is typically
        dependent on the document's title name (auto-generated targets provided
        by Confluence; ex. title#header). This register method allows a builder
        to track the target value to use for a provided reference (so that a
        writer can properly prepare a link; see also `target`).
        """
        ConfluenceState.refid2target[refid] = target
        ConfluenceLogger.verbose("mapping %s to target: %s" % (refid, target))

    @staticmethod
    def registerTitle(docname, title, config):
        """
        register the title for the provided document name

        In Confluence, a page is identified by the name/title of a page (at
        least, from the user's perspective). When processing a series of
        document names, the title value used for a document is based off the
        first heading detected. This register method allows a builder to track
        a document's title name name, so it may provide a document's contents
        and target title when passed to the publish operation.

        If a prefix (or postfix) value is provided, it will be added to the
        beginning (or at the end) of the provided title value.
        """
        try_max = CONFLUENCE_MAX_TITLE_LEN
        base_tail = ""

        if config.confluence_ignore_titlefix_on_index and docname == config.root_doc:
            postfix = None
            prefix = None
        else:
            postfix = config.confluence_publish_postfix
            prefix = config.confluence_publish_prefix

        if prefix:
            title = prefix + title

        if postfix:
            base_tail += postfix
            try_max += len(postfix)

        if len(title) > try_max:
            title = title[0:try_max]
            ConfluenceLogger.warn(
                "document title has been trimmed due to " "length: %s" % docname
            )

        base_title = title
        title += base_tail

        # check if title is already used; if so, append a new value
        offset = 2
        while title.lower() in ConfluenceState.title2doc:
            if offset == 2:
                ConfluenceLogger.warn(
                    "title conflict detected with "
                    "'{}' and '{}'".format(
                        ConfluenceState.title2doc[title.lower()], docname
                    )
                )

            tail = " ({}){}".format(offset, base_tail)
            try_max = CONFLUENCE_MAX_TITLE_LEN + len(tail)
            if len(base_title) > try_max:
                base_title = base_title[0:try_max]

            title = base_title + tail
            offset += 1

        ConfluenceState.doc2title[docname] = title
        ConfluenceState.title2doc[title.lower()] = docname
        ConfluenceLogger.verbose("mapping %s to title: %s" % (docname, title))
        return title

    @staticmethod
    def registerToctreeDepth(docname, depth):
        """
        register the toctree-depth for the provided document name

        Documents using toctree's will only use the first toctree's 'maxdepth'
        option [1]. This method provides the ability to track the depth of a
        document before toctree resolution removes any hints at the maximum
        depth desired.

        [1]: http://www.sphinx-doc.org/en/stable/markup/toctree.html#id3
        """
        ConfluenceState.doc2ttd[docname] = depth
        ConfluenceLogger.verbose("track %s toc-depth: %s" % (docname, depth))

    @staticmethod
    def registerUploadId(docname, id):
        """
        register a page (upload) identifier for a docname

        When a publisher creates/updates a page on a Confluence instance, the
        resulting page will have an identifier for it. This state utility class
        can help track the Confluence page's identifier by invoking this
        registration method. This method is primarily used to help track/order
        published documents into a hierarchical fashion (see
        `registerParentDocname`). It is important to note that the order of
        published documents will determine if a page's upload identifier is
        tracked in this state (see also `uploadId`).
        """
        ConfluenceState.doc2uploadId[docname] = id
        ConfluenceLogger.verbose("tracking docname %s's upload id: %s" % (docname, id))

    @staticmethod
    def reset():
        """
        reset all state information

        Provides the ability for uses of a Confluence state singleton to reset
        known tracked data.
        """
        ConfluenceState.doc2uploadId.clear()
        ConfluenceState.doc2parentDoc.clear()
        ConfluenceState.doc2title.clear()
        ConfluenceState.doc2ttd.clear()
        ConfluenceState.refid2target.clear()
        ConfluenceState.title2doc.clear()

    @staticmethod
    def parentDocname(docname):
        """
        return the parent docname (if any) for a provided docname

        See `registerParentDocname` for more information.
        """
        return ConfluenceState.doc2parentDoc.get(docname)

    @staticmethod
    def target(refid):
        """
        return the (anchor) target for a provided reference

        See `registerTarget` for more information.
        """
        return ConfluenceState.refid2target.get(refid)

    @staticmethod
    def title(docname, default=None):
        """
        return the title value for a provided docname

        See `registerTitle` for more information.
        """
        return ConfluenceState.doc2title.get(docname, default)

    @staticmethod
    def toctreeDepth(docname):
        """
        return the toctree-depth value for a provided docname

        See `registerToctreeDepth` for more information.
        """
        return ConfluenceState.doc2ttd.get(docname)

    @staticmethod
    def uploadId(docname):
        """
        return the confluence (upload) page id for the provided docname

        See `registerUploadId` for more information.
        """
        return ConfluenceState.doc2uploadId.get(docname)
