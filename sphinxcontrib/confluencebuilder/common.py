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

    @staticmethod
    def register(docname, title, prefix = None):
        if prefix:
            title = prefix + title

        if len(title) > CONFLUENCE_MAX_TITLE_LEN:
            title = title[0:CONFLUENCE_MAX_TITLE_LEN]
            ConfluenceLogger.warn("document title has been trimmed due to "
                "length: %s" % docname)

        ConfluenceDocMap.doc2title[docname] = title
        ConfluenceLogger.verbose("mapping %s to title: %s" % (docname, title))

    @staticmethod
    def title(docname):
        return ConfluenceDocMap.doc2title.get(docname)

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
