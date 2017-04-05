# -*- coding: utf-8 -*-
"""
    sphinxcontrib.confluencebuilder.publisher
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2017 by the contributors (see AUTHORS file).
    :license: BSD, see LICENSE.txt for details.
"""

try:
    from confluence import Confluence
    HAS_CONFLUENCE = True
except ImportError:
    HAS_CONFLUENCE = False

class ConfluenceConnectionError(Exception):
    pass

class ConfluencePublisher():
    def connect(self, config):
        if not HAS_CONFLUENCE:
            raise ImportError("Must install confluence module first to publish, see README.")

        try:
            self.instance = Confluence(url=config.confluence_server_url,
                                         username=config.confluence_server_user,
                                         password=config.confluence_server_pass)
        except ImportError:
            raise ImportError("Must install confluence PyPi package to publish")
        except Exception as ex:
            raise ConfluenceConnectionError("Could not connect, check remote API is configured. %s" % ex)

    def getPageId(self, space, title):
        return self.instance.getPageId(title, space)

    def getPageContent(self, space, title):
        return self.instance.getPage(title, space)

    def getDescendents(self, parentId):
        return self.instance._server.confluence2.getDescendents(
            self.instance._token2, parentId)

    def storePage(self, page, rawData, parentId=None):
        data = self.instance._server.confluence2.convertWikiToStorageFormat(
                self.instance._token2, rawData)
        page['content'] = data

        if parentId:
            page['parentId'] = parentId

        rsp = self.instance._server.confluence2.storePage(
            self.instance._token2, page)
        return rsp['id']

    def removePage(self, pageId):
        self.instance._server.confluence2.removePage(
            self.instance._token2, pageId)
