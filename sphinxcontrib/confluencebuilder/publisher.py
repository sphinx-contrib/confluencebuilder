# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2017-2018 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.

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
from .exceptions import ConfluenceCertificateError
from .exceptions import ConfluenceConfigurationError
from .exceptions import ConfluenceLegacyError
from .exceptions import ConfluencePermissionError
from .exceptions import ConfluenceProxyPermissionError
from .exceptions import ConfluenceRemoteApiDisabledError
from .experimental import ConfluenceExperimentalQuoteSupport
from .logger import ConfluenceLogger
from .rest import Rest
from .std.confluence import API_XMLRPC_BIND_PATH
import os
import socket
import ssl
import sys

try:
    import http.client as httplib
except ImportError:
    import httplib

try:
    import urllib.parse as urllib
except ImportError:
    import urllib

try:
    import xmlrpc.client as xmlrpclib
except ImportError:
    import xmlrpclib

class ConfluencePublisher():
    def __init__(self):
        self.space_display_name = None

    def init(self, config):
        self.config = config
        self.notify = not config.confluence_disable_notifications
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
        self.ca_cert = config.confluence_ca_cert
        self.client_cert = config.confluence_client_cert
        self.client_cert_pass = config.confluence_client_cert_pass

    def connect(self):
        if not self.use_rest and not self.use_xmlrpc:
            raise ConfluenceConfigurationError("""Both REST and XML-RPC """
                """options have been explicitly disabled. Unable to publish.""")

        if self.use_rest:
            self.rest_client = Rest(self.config);
            try:
                rsp = self.rest_client.get('space', {
                    'spaceKey': self.space_name,
                    'limit': 1
                    })
                if rsp['size'] == 0:
                    raise ConfluenceBadSpaceError(self.space_name)
                self.space_display_name = rsp['results'][0]['name']
                self.use_xmlrpc = False
            except ConfluenceBadApiError:
                if not self.use_xmlrpc:
                    raise
                self.use_rest = False
            except ConfluenceBadServerUrlError:
                if not self.use_xmlrpc:
                    raise
                self.use_rest = False

        if self.use_xmlrpc:
            try:
                self.xmlrpc_transport = ConfluenceTransport(
                    self.server_url, self.proxy, self.timeout,
                    self.ca_cert, self.client_cert, self.client_cert_pass)
                if self.config.confluence_disable_ssl_validation:
                    self.xmlrpc_transport.disable_ssl_verification()

                self.xmlrpc = xmlrpclib.ServerProxy(
                    self.server_url + API_XMLRPC_BIND_PATH,
                    transport=self.xmlrpc_transport, allow_none=True)
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
                    if ex.errcode == 407:
                        raise ConfluenceProxyPermissionError
                    raise ConfluenceBadServerUrlError(self.server_url, ex)
                except (httplib.InvalidURL, socket.error) as ex:
                    raise ConfluenceBadServerUrlError(self.server_url, ex)
                except xmlrpclib.Fault as ex:
                    if ex.faultString.find('AuthenticationFailed') != -1:
                        raise ConfluenceAuthenticationFailedUrlError
                    raise
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
                except socket.gaierror as ex:
                    raise ConfluenceBadServerUrlError(self.server_url, ex)

    def disconnect(self):
        if self.use_rest:
            self.rest_client.close()
        elif self.use_xmlrpc and self.token:
            self.xmlrpc.logout(self.token)
            self.xmlrpc_transport.close()

    def getBasePageId(self):
        base_page_id = None

        if not self.parent_name:
            return base_page_id

        if self.use_rest:
            rsp = self.rest_client.get('content', {
                'type': 'page',
                'spaceKey': self.space_name,
                'title': self.parent_name,
                'status': 'current'
                })
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

        if self.use_rest:
            if page_id:
                search_fields = {'cql': 'ancestor=' + str(page_id)}
            else:
                search_fields = {'cql': 'space=' + self.space_name +
                    ' and type=page'}

            # Observed issues with "content/{id}/descendant"; using search.
            rsp = self.rest_client.get('content/search', search_fields)
            idx = 0
            while rsp['size'] > 0:
                for result in rsp['results']:
                    descendents.append(result['id'])

                if rsp['size'] != rsp['limit']:
                    break

                idx += int(rsp['limit'])
                sub_search_fields = dict(search_fields)
                sub_search_fields['start'] = idx;
                rsp = self.rest_client.get('content/search', sub_search_fields)
        else:
            if page_id:
                pages = self.xmlrpc.getDescendents(self.token, page_id)
            else:
                pages = self.xmlrpc.getPages(self.token, self.space_name)

            for child_page in pages:
                descendents.append(child_page['id'])

        return descendents

    def getDescendentsCompat(self, page_id):
        visited_pages = set()

        def find_legacy_pages(page_id, pages):
            descendents = self.getDescendents(page_id)
            for descendent in descendents:
                if descendent not in pages:
                    pages.add(descendent)
                    find_legacy_pages(descendent, pages)

        find_legacy_pages(page_id, visited_pages)
        return list(visited_pages)

    def storePage(self, page_name, raw_data, parent_id=None):
        uploaded_page_id = None

        if self.config.confluence_adv_trace_data:
            ConfluenceLogger.trace('raw_data', raw_data)

        if self.use_rest:
            raw_data_req = {
                'value': raw_data,
                'representation': 'wiki'
            }
            rsp = self.rest_client.post(
                'contentbody/convert/storage', raw_data_req)
            storage_data = rsp['value']
        else:
            isNewPage = False
            try:
                page = self.xmlrpc.getPage(
                    self.token, self.space_name, page_name)
            except xmlrpclib.Fault:
                page = {
                    'title': page_name,
                    'space': self.space_name
                }
                isNewPage = True

            try:
                storage_data = self.xmlrpc.convertWikiToStorageFormat(
                    self.token, raw_data)
            except xmlrpclib.Fault as ex:
                if ex.faultString.find('UnknownMacroMigration') != -1:
                    print("\nWARNING: Unsupported macro is page generation.");
                    print(" (details: %s)" % ex.faultString);

                    # Track known ID so legacy page does not get deleted if
                    # purge is enabled.
                    if 'id' in page:
                        uploaded_page_id = page['id']
                    return uploaded_page_id
                raise

        assert storage_data

        if self.config.confluence_adv_trace_data:
            ConfluenceLogger.trace('storage', storage_data)

        if self.config.confluence_experimental_indentation:
            storage_data = \
                ConfluenceExperimentalQuoteSupport.process(storage_data)
            if self.config.confluence_adv_trace_data:
                ConfluenceLogger.trace('storage-post-exp', storage_data)

        if self.use_rest:
            rsp = self.rest_client.get('content', {
                'type': 'page',
                'spaceKey': self.space_name,
                'title': page_name,
                'status': 'current',
                'expand': 'version'
                })
            try:
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
                    uploaded_page_id = rsp['id']
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

                    if not self.notify:
                        updatePage['version']['minorEdit'] = True

                    if parent_id:
                        updatePage['ancestors'] = [{'id': parent_id}]

                    self.rest_client.put('content', page['id'], updatePage)
                    uploaded_page_id = page['id']
            except ConfluencePermissionError:
                raise ConfluencePermissionError(
                    """Publish user does not have permission to add page """
                    """content to the configured space."""
                )
        else:
            page['content'] = storage_data

            if parent_id:
                page['parentId'] = parent_id

            try:
                if isNewPage:
                    uploaded_page = self.xmlrpc.storePage(self.token, page)
                else:
                    updateOptions = {}

                    if not self.notify:
                        updateOptions['minorEdit'] = True

                    uploaded_page = self.xmlrpc.updatePage(
                        self.token, page, updateOptions)
            except xmlrpclib.Fault as ex:
                if ex.faultString.find('NotPermittedException') != -1:
                    raise ConfluencePermissionError(
                        """Publish user does not have permission to add page """
                        """content to the configured space."""
                    )
                raise
            uploaded_page_id = uploaded_page['id']

        return uploaded_page_id

    def removePage(self, page_id):
        if self.use_rest:
            try:
                self.rest_client.delete('content', page_id)
            except ConfluencePermissionError:
                raise ConfluencePermissionError(
                    """Publish user does not have permission to delete """
                    """from the configured space."""
                )
        else:
            try:
                self.xmlrpc.removePage(self.token, page_id)
            except xmlrpclib.Fault as ex:
                if ex.faultString.find('NotPermittedException') != -1:
                    raise ConfluencePermissionError(
                        """Publish user does not have permission to delete """
                        """from the configured space."""
                    )
                raise

    def updateSpaceHome(self, page_id):
        if not page_id:
            return

        if self.use_rest:
            page = self.rest_client.get('content/' + page_id, None)
            try:
                self.rest_client.put('space', self.space_name, {
                    'key': self.space_name,
                    'name': self.space_display_name,
                    'homepage': page
                })
            except ConfluencePermissionError:
                raise ConfluencePermissionError(
                    """Publish user does not have permission to update """
                    """space's homepage."""
                )
        else:
            space = self.xmlrpc.getSpace(self.token, self.space_name)
            space['homePage'] = page_id
            try:
                self.xmlrpc.storeSpace(self.token, space)
            except xmlrpclib.Fault as ex:
                if ex.faultString.find('NotPermittedException') != -1:
                    raise ConfluencePermissionError(
                        """Publish user does not have permission to update """
                        """space's homepage."""
                    )
                raise

class ConfluenceTransport(xmlrpclib.Transport):
    """
    transport class for http/https transactions to an xml-rpc server

    This transport class has been introduced to allow proxy settings and timeout
    settings to be applied to XML-RPC ServerProxy sessions.

    [1]: https://github.com/python/cpython/blob/2.7/Lib/xmlrpclib.py
    [2]: https://github.com/python/cpython/blob/2.7/Lib/httplib.py
    [4]: https://github.com/python/cpython/blob/3.4/Lib/http/client.py
    [3]: https://github.com/python/cpython/blob/3.4/Lib/xmlrpc/client.py
    [5]: https://github.com/python/cpython/blob/3.5/Lib/http/client.py
    [6]: https://github.com/python/cpython/blob/3.5/Lib/xmlrpc/client.py
    [7]: https://github.com/python/cpython/blob/3.6/Lib/http/client.py
    [8]: https://github.com/python/cpython/blob/3.6/Lib/xmlrpc/client.py
    """
    def __init__(self, server_url, proxy=None,
            timeout=socket._GLOBAL_DEFAULT_TIMEOUT, ca_cert=None,
            client_cert=None, client_cert_pass=None):
        """
        initialize the transport class
        """
        xmlrpclib.Transport.__init__(self)

        client_cert = client_cert or (None, None)
        self.disable_ssl_validation = False
        self.scheme = urllib.splittype(server_url)[0]
        self.https = (self.scheme == 'https')
        self.proxy = None
        self.timeout = timeout
        self._certfile, self._keyfile = client_cert
        self.ca_cert = ca_cert
        self.client_cert_pass = client_cert_pass

        # pull system proxy if no proxy is forced
        if not proxy:
            if self.https:
                proxy = os.environ.get('https_proxy', None)
            else:
                proxy = os.environ.get('http_proxy', None)

        if proxy:
            scheme, proxy_url = urllib.splittype(proxy)
            self.proxy = urllib.splithost(proxy_url)[0]

            # re-check if we need to support https
            self.https = (scheme == 'https')

    def make_connection(self, host):
        """
        make an http/https connection

        Overrides the transport's `make_connection` implementation to forcefully
        configure proxy and timeout settings.
        """

        # existing connection exist (keep-alive)?
        if self._connection and host == self._connection[0]:
            return self._connection[1]

        # extract host, extra headers (if any) or x509 info (if any)
        chost, self._extra_headers, x509 = self.get_host_info(host)
        self.chost = chost

        # if we have a proxy, override chost for connection and configure proxy
        # authentication (if required)
        if self.proxy:
            chost, proxy_headers, x509 = self.get_host_info(self.proxy)
            for key, val in proxy_headers:
                if key == 'Authorization':
                    if not self._extra_headers:
                        self._extra_headers = []
                    self._extra_headers.append(
                        tuple(['Proxy-Authorization',val]))
                    break

        # build connection
        if self.https:
            try:
                context = self._setup_ssl_context()
                self._connection = host, httplib.HTTPSConnection(chost,
                    timeout=self.timeout, context=context, **(x509 or {}))
            except AttributeError:
                raise NotImplementedError('httplib does not support https')
        else:
            self._connection = host, httplib.HTTPConnection(
                chost, timeout=self.timeout)

        return self._connection[1]

    # handle variant versions of 'send_request', note that in:
    #  - python 2: make_connection first, then send_request
    #  - python 3: send_request first, then make_connection
    if sys.version_info.major == 2:
        def send_request(self, connection, handler, request_body):
            """
            handle an http/https request on the current connection

            Overrides the transport's `send_request` implementation to ensure
            proper scheme and host is set in the handler.
            """
            handler = '%s://%s%s' % (self.scheme, self.chost, handler)
            return xmlrpclib.Transport.send_request(
                self, connection, handler, request_body)
    else:
        def send_request(self, host, handler, request_body, debug):
            """
            handle an http/https request for the future connection

            Overrides the transport's `send_request` implementation to ensure
            proper scheme and host is set in the handler.
            """
            chost = self.get_host_info(host)[0]
            handler = '%s://%s%s' % (self.scheme, chost, handler)
            return xmlrpclib.Transport.send_request(
                self, host, handler, request_body, debug)

    def _setup_ssl_context(self):
        cafile = None
        capath = None
        if self.ca_cert:
            if os.path.isdir(self.ca_cert):
                capath = self.ca_cert
            elif os.path.isfile(self.ca_cert):
                cafile = self.ca_cert

        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH,
                                             cafile=cafile, capath=capath)
        if self._certfile:
            try:
                context.load_cert_chain(certfile=self._certfile,
                                        keyfile=self._keyfile,
                                        password=self.client_cert_pass)
            except ssl.SSLError as ex:
                raise ConfluenceCertificateError(ex)

        if self.disable_ssl_validation:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

        return context

    def disable_ssl_verification(self):
        """
        disable ssl verification for an https connection

        Pushes an "unverified" context to an HTTPSConnection to disable SSL
        verification (although, this is never recommended).
        """
        self.disable_ssl_validation = True

