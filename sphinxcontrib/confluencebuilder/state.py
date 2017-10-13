# -*- coding: utf-8 -*-
"""
    sphinxcontrib.confluencebuilder.state
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2017 by the contributors (see AUTHORS file).
    :license: BSD, see LICENSE.txt for details.
"""

from .logger import ConfluenceLogger

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
    doc2title = {}
    refid2target = {}

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
    def registerTitle(docname, title, prefix = None):
        """
        register the title for the provided document name

        In Confluence, a page is identified by the name/title of a page (at
        least, from the user's perspective). When processing a series of
        document names, the title value used for a document is based off the
        first heading detected. This register method allows a builder to track
        a document's title name name, so it may provide a document's contents
        and target title when passed to the publish operation.

        If a prefix value is provided, it will be added to the beginning of the
        provided title value.
        """
        if prefix:
            title = prefix + title

        if len(title) > CONFLUENCE_MAX_TITLE_LEN:
            title = title[0:CONFLUENCE_MAX_TITLE_LEN]
            ConfluenceLogger.warn("document title has been trimmed due to "
                "length: %s" % docname)

        ConfluenceState.doc2title[docname] = title
        ConfluenceLogger.verbose("mapping %s to title: %s" % (docname, title))
        return title

    @staticmethod
    def target(refid):
        """
        return the (anchor) target for a provided reference

        See `registerTarget` for more information.
        """
        return ConfluenceState.refid2target.get(refid)

    @staticmethod
    def title(docname):
        """
        return the title value for a provided document name

        See `registerTitle` for more information.
        """
        return ConfluenceState.doc2title.get(docname)

    @staticmethod
    def titleConflictCheck():
        """
        check for title conflicts with known documents

        The following cycles through known documents to see if any documents are
        using the same title name. If multiple documents have the same title
        value, the publish operation would update the contents of a page
        multiple times (last served wins). This check only generates a warning
        for the user (as this should not really happen).
        """
        d = ConfluenceState.doc2title
        for key_a in d:
            for key_b in d:
                if key_a == key_b:
                    break
                if (d[key_a] == d[key_b]):
                    ConfluenceLogger.warn("title conflict detected with "
                        "'%s' and '%s'" % (key_a, key_b))
