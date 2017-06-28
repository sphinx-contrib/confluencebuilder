# -*- coding: utf-8 -*-
"""
    sphinxcontrib.confluencebuilder.common
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2017 by the contributors (see AUTHORS file).
    :license: BSD, see LICENSE.txt for details.
"""

# Maximum length for a Confluence page title.
CONFLUENCE_MAX_TITLE_LEN = 255

class ConfluenceDocMap:
    doc2title = {}
    doc2id = {}
    doc2parent = {}
    refid2target = {}

    @staticmethod
    def registerTarget(refid, target):
        ConfluenceDocMap.refid2target[refid] = target
        ConfluenceLogger.verbose("mapping %s to target: %s" % (refid, target))

    @staticmethod
    def registerTitle(docname, title, prefix = None):
        if prefix:
            title = prefix + title

        if len(title) > CONFLUENCE_MAX_TITLE_LEN:
            title = title[0:CONFLUENCE_MAX_TITLE_LEN]
            ConfluenceLogger.warn("document title has been trimmed due to "
                "length: %s" % docname)

        ConfluenceDocMap.doc2title[docname] = title
        ConfluenceLogger.verbose("mapping %s to title: %s" % (docname, title))
        return title

    @staticmethod
    def registerParent(docname, parent_docname):
        ConfluenceDocMap.doc2parent[docname] = parent_docname
        ConfluenceLogger.verbose("setting parent of %s to: %s" % (docname, parent_docname))
        return docname

    @staticmethod
    def registerID(docname, conf_id):
        ConfluenceDocMap.doc2id[docname] = conf_id
        return docname

    @staticmethod
    def target(refid):
        return ConfluenceDocMap.refid2target.get(refid)

    @staticmethod
    def parent(docname):
        return ConfluenceDocMap.doc2parent.get(docname)

    @staticmethod
    def id(docname):
        return ConfluenceDocMap.doc2id.get(docname)

    @staticmethod
    def title(docname):
        return ConfluenceDocMap.doc2title.get(docname)

    @staticmethod
    def conflictCheck():
        d = ConfluenceDocMap.doc2title
        for key_a in d:
            for key_b in d:
                if key_a == key_b:
                    break
                if (d[key_a] == d[key_b]):
                    ConfluenceLogger.warn("title conflict detected with "
                        "'%s' and '%s'" % (key_a, key_b))

class ConfluenceLogger():
    app = None

    @staticmethod
    def initialize(app):
        ConfluenceLogger.app = app

    @staticmethod
    def info(*args, **kwargs):
        if ConfluenceLogger.app:
            ConfluenceLogger.app.info(*args, **kwargs)

    @staticmethod
    def verbose(*args, **kwargs):
        if ConfluenceLogger.app:
            ConfluenceLogger.app.verbose(*args, **kwargs)

    @staticmethod
    def warn(*args, **kwargs):
        if ConfluenceLogger.app:
            ConfluenceLogger.app.warn(*args, **kwargs)
