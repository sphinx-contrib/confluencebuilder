# -*- coding: utf-8 -*-
"""
    sphinxcontrib.confluencebuilder.publisher
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2017 by the contributors (see AUTHORS file).
    :license: BSD, see LICENSE.txt for details.

    See also:
     Confluence Cloud REST API Reference
     https://docs.atlassian.com/confluence/REST/latest/

     Confluence XML-RPC and SOAP APIs
     https://developer.atlassian.com/confdev/deprecated-apis/confluence-xml-rpc-and-soap-apis
"""

from .exceptions import ConfluenceAuthenticationFailedUrlError
from .exceptions import ConfluenceBadApiError
from .exceptions import ConfluenceBadServerUrlError
from .exceptions import ConfluenceBadSpaceError
from .exceptions import ConfluenceConfigurationError
from .exceptions import ConfluenceLegacyError
from .exceptions import ConfluenceRemoteApiDisabledError
from .rest import Rest
import socket

try:
    import http.client as httplib
except ImportError:
    import httplib

try:
    import xmlrpc.client as xmlrpclib
except ImportError:
    import xmlrpclib

class ConfluencePublisher():
    def init(self, config):
        self.parent_id = config.confluence_parent_page_id_check
        self.parent_name = config.confluence_parent_page
        self.proxy = config.confluence_proxy
        self.server_url = config.confluence_server_url
        self.server_user = config.confluence_server_user
        self.server_pass = config.confluence_server_pass
        self.space_name = config.confluence_space_name
        self.timeout = config.confluence_timeout
        self.use_rest = not config.confluence_disable_rest
        self.use_xmlrpc = not config.confluence_disable_xmlrpc

    def connect(self):
        if not self.use_rest and not self.use_xmlrpc:
            raise ConfluenceConfigurationError("""Both REST and XML-RPC """
                """options have been explicitly disabled. Unable to publish.""")

        if self.use_rest:
            self.rest_client = Rest(self.server_url,
                self.server_user, self.server_pass, self.timeout);
            try:
                rsp = self.rest_client.get('space', [
                    'spaceKey=' + self.space_name,
                    'limit=1'
                    ])
                if rsp['size'] == 0:
                    raise ConfluenceBadSpaceError(self.space_name)
                self.use_xmlrpc = False
            except ConfluenceBadApiError:
                if not self.use_xmlrpc:
                    raise
                self.use_rest = False

        if self.use_xmlrpc:
            try:
                transport = None
                if self.proxy or self.timeout:
                    transport = ConfluenceTransport()
                    if self.proxy:
                        transport.set_proxy(self.proxy)
                    if self.timeout:
                        transport.set_timeout(self.timeout)

                self.xmlrpc = xmlrpclib.ServerProxy(
                    self.server_url + '/rpc/xmlrpc',
                    transport=transport, allow_none=True)
            except IOError as ex:
                raise ConfluenceBadServerUrlError(self.server_url, ex)

            if self.server_user:
                try:
                    token = self.xmlrpc.confluence1.login(
                            self.server_user, self.server_pass)
                    try:
                        self.token = self.xmlrpc.confluence2.login(
                            self.server_user, self.server_pass)
                        self.xmlrpc.confluence1.logout(token)
                        self.xmlrpc = self.xmlrpc.confluence2
                    except xmlrpclib.Error:
                        self.token = None
                except xmlrpclib.ProtocolError as ex:
                    if ex.errcode == 403:
                        raise ConfluenceRemoteApiDisabledError(self.server_url)
                    raise ConfluenceBadServerUrlError(self.server_url, ex)
                except (httplib.InvalidURL, socket.error) as ex:
                    raise ConfluenceBadServerUrlError(self.server_url, ex)
                except xmlrpclib.Fault as ex:
                    if ex.faultString.find('AuthenticationFailed') != -1:
                        raise ConfluenceAuthenticationFailedUrlError
                if not self.token:
                    raise ConfluenceLegacyError
            else:
                self.token = '' # Anonymous.

            if self.token:
                try:
                    self.xmlrpc.getSpace(self.token, self.space_name)
                except xmlrpclib.Fault as ex:
                    self.xmlrpc.logout(self.token)
                    raise ConfluenceBadSpaceError(self.space_name)
            else:
                try:
                    self.xmlrpc.confluence2.getSpace(None, self.space_name)
                    self.xmlrpc = self.xmlrpc.confluence2
                except xmlrpclib.Fault as ex:
                    try:
                        self.xmlrpc.confluence1.getSpace(None, self.space_name)
                        self.xmlrpc = self.xmlrpc.confluence1
                    except xmlrpclib.Fault as ex:
                        raise ConfluenceBadSpaceError(self.space_name)

    def disconnect(self):
        if self.use_xmlrpc and self.token:
            self.xmlrpc.logout(self.token)

    def getBasePageId(self):
        base_page_id = None

        if not self.parent_name:
            return base_page_id

        if self.use_rest:
            rsp = self.rest_client.get('content', [
                'type=page',
                'spaceKey=' + self.space_name,
                'title=' + self.parent_name,
                'status=current'
                ])
            if rsp['size'] == 0:
                raise ConfluenceConfigurationError("""Configured parent """
                    """page name do not exist.""")
            page = rsp['results'][0]
            if self.parent_id and page['id'] != str(self.parent_id):
                raise ConfluenceConfigurationError("""Configured parent """
                    """page ID and name do not match.""")
            base_page_id = page['id']
        else:
            try:
                page = self.xmlrpc.getPage(
                    self.token, self.space_name, self.parent_name)
            except xmlrpclib.Fault:
                raise ConfluenceConfigurationError("""Configured parent """
                    """page name do not exist.""")
            if self.parent_id and page['id'] != str(self.parent_id):
                raise ConfluenceConfigurationError("""Configured parent """
                    """page ID and name do not match.""")
            base_page_id = page['id']

        if not base_page_id and self.parent_id:
            raise ConfluenceConfigurationError("""Unable to find the """
                """parent page matching the ID or name provided.""")

        return base_page_id

    def getDescendents(self, page_id):
        descendents = []

        if not page_id:
            return descendents

        if self.use_rest:
            # Observed issues with "content/{id}/descendant"; using search.
            rsp = self.rest_client.get('content/search',
                ['cql=ancestor=' + str(page_id)])
            idx = 0
            while rsp['size'] > 0:
                for result in rsp['results']:
                    descendents.append(result['id'])

                if rsp['size'] != rsp['limit']:
                    break

                idx += int(rsp['limit'])
                rsp = self.rest_client.get('content/search', [
                    'cql=ancestor=' + str(page_id), 'start=' + str(idx)])
        else:
            pages = self.xmlrpc.getDescendents(self.token, page_id)
            for child_page in pages:
                descendents.append(child_page['id'])

        return descendents

    def storePage(self, page_name, raw_data, parent_id=None):
        uploaded_page_id = None

        if self.use_rest:
            raw_data_req = {
                'value': raw_data,
                'representation': 'wiki'
            }
            rsp = self.rest_client.post(
                'contentbody/convert/storage', raw_data_req)
            storage_data = rsp['value']

            rsp = self.rest_client.get('content', [
                'type=page',
                'spaceKey=' + self.space_name,
                'title=' + page_name,
                'status=current',
                'expand=version'
                ])
            if rsp['size'] == 0:
                newPage = {
                    'type': 'page',
                    'title': page_name,
                    'body': {
                        'storage': {
                            'representation': 'storage',
                            'value': storage_data
                        }
                    },
                    'space': {
                        'key': self.space_name
                    }
                }

                if parent_id:
                    newPage['ancestors'] = [{'id': parent_id}]

                rsp = self.rest_client.post('content', newPage)
            else:
                page = rsp['results'][0]
                last_version = int(page['version']['number'])
                updatePage = {
                    'id': page['id'],
                    'type': 'page',
                    'title': page_name,
                    'body': {
                        'storage': {
                            'representation': 'storage',
                            'value': storage_data
                        }
                    },
                    'space': {
                        'key': self.space_name
                    },
                    'version': {
                        'number': last_version + 1
                    }
                }

                if parent_id:
                    updatePage['ancestors'] = [{'id': parent_id}]

                self.rest_client.put('content', page['id'], updatePage)
                uploaded_page_id = page['id']
        else:
            try:
                page = self.xmlrpc.getPage(
                    self.token, self.space_name, page_name)
            except xmlrpclib.Fault:
                page = {
                    'title': page_name,
                    'space': self.space_name
                }

            storage_data = self.xmlrpc.convertWikiToStorageFormat(
                self.token, raw_data)
            page['content'] = storage_data

            if parent_id:
                page['parentId'] = parent_id

            uploaded_page = self.xmlrpc.storePage(self.token, page)
            uploaded_page_id = uploaded_page['id']

        return uploaded_page_id

    def removePage(self, page_id):
        if self.use_rest:
            self.rest_client.delete('content', page_id)
        else:
            self.xmlrpc.removePage(self.token, page_id)

class ConfluenceTransport(xmlrpclib.Transport):
    proxy = None
    timeout = None

    def make_connection(self, host):
        self.realhost = host
        if self.proxy:
            return httplib.HTTPConnection(self.proxy, timeout=self.timeout)
        else:
            return httplib.HTTPConnection(self.realhost, timeout=self.timeout)

    def send_host(self, connection, host):
        connection.putheader('Host', self.realhost)

    def send_request(self, connection, handler, request_body):
        connection.putrequest('POST', 'http://%s%s' % (self.realhost, handler))

    def set_proxy(self, proxy):
        self.proxy = proxy

    def set_timeout(self, timeout):
        self.timeout = timeout
