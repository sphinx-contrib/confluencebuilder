# -*- coding: utf-8 -*-
"""
    sphinxcontrib.confluencebuilder.common
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2017 by the contributors (see AUTHORS file).
    :license: BSD, see LICENSE.txt for details.
"""

from sphinx.util import logging
import io

# Maximum length for a Confluence page title.
CONFLUENCE_MAX_TITLE_LEN = 255

class ConfluenceDocMap:
    doc2title = {}
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
    def target(refid):
        return ConfluenceDocMap.refid2target.get(refid)

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
    logger = None

    @staticmethod
    def initialize():
        ConfluenceLogger.logger = logging.getLogger("confluence")

    @staticmethod
    def info(*args, **kwargs):
        if ConfluenceLogger.logger:
            ConfluenceLogger.logger.info(*args, **kwargs)

    @staticmethod
    def verbose(*args, **kwargs):
        if ConfluenceLogger.logger:
            ConfluenceLogger.logger.verbose(*args, **kwargs)

    @staticmethod
    def warn(*args, **kwargs):
        if ConfluenceLogger.logger:
            ConfluenceLogger.logger.warning(*args, **kwargs)

    @staticmethod
    def trace(title, data):
        try:
            with io.open('trace.log', 'a', encoding='utf-8') as file:
                file.write(u'[%s]\n' % title)
                file.write(data)
                file.write(u'\n')
        except (IOError, OSError) as err:
            ConfluenceLogger.warn('unable to trace: %s' % err)
