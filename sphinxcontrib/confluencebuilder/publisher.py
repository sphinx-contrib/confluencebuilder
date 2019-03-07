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
from .logger import ConfluenceLogger
from .rest import Rest
from .std.confluence import API_XMLRPC_BIND_PATH
import os
import socket
import ssl
import sys
import time

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

    def getDescendants(self, page_id):
        """
        generate a list of descendants

        Queries the configured Confluence instance for a set of descendants for
        the provided `page_id` or (if set to `None`) the configured space.

        Args:
            page_id: the ancestor to search on (if not `None`)

        Returns:
            the descendants
        """
        descendants = set()

        if self.use_rest:
            if page_id:
                search_fields = {'cql': 'ancestor=' + str(page_id)}
            else:
                search_fields = {'cql': 'space="' + self.space_name +
                    '" and type=page'}

            # Configure a larger limit value than the default (no provided
            # limit defaults to 25). This should reduce the number of queries
            # needed to fetch a complete descendants set (for larger sets).
            search_fields['limit'] = 1000;

            rsp = self.rest_client.get('content/search', search_fields)
            idx = 0
            while rsp['size'] > 0:
                for result in rsp['results']:
                    descendants.add(result['id'])

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
                descendants.add(child_page['id'])

        return descendants

    def getDescendantsCompat(self, page_id):
        """
        generate a list of descendants (aggressive)

        Queries the configured Confluence instance for a set of descendants for
        the provided `page_id` or (if set to `None`) the configured space. This
        request is a more aggressive search for descendants when compared to
        `getDescendants`. Each page found will be again searched on for
        descendants. This is to handle rare cases where a Confluence instance
        does not provide a complete set of descendants (this has been observed
        on some instances of Confluence server; speculated to be possible
        cache corruption). This search can be extremely slow for large document
        sets.

        Args:
            page_id: the ancestor to search on (if not `None`)

        Returns:
            the descendants
        """
        visited_pages = set()

        def find_legacy_pages(page_id, pages):
            descendants = self.getDescendants(page_id)
            for descendant in descendants:
                if descendant not in pages:
                    pages.add(descendant)
                    find_legacy_pages(descendant, pages)

        find_legacy_pages(page_id, visited_pages)
        return visited_pages

    def getAttachment(self, page_id, name):
        """
        get attachment information with the provided page id and name

        Performs an API call to acquire known information about a specific
        attachment. This call can returns both the attachment identifier (for
        convenience) and the attachment object. If the attachment cannot be
        found, the returned tuple will return ``None`` entries.

        Args:
            page_id: the page identifier
            name: the attachment name

        Returns:
            the attachment id and attachment object
        """
        attachment = None
        attachment_id = None

        if self.use_rest:
            url = 'content/{}/child/attachment'.format(page_id)
            rsp = self.rest_client.get(url, {
                #'type': 'attachment',
                'filename': name,
                })

            if rsp['size'] != 0:
                attachment = rsp['results'][0]
                attachment_id = attachment['id']
        else:
            try:
                MOST_RECENT_VERSION = '0'
                attachment = self.xmlrpc.getAttachment(
                    self.token, page_id, name, MOST_RECENT_VERSION)
                attachment_id = attachment['id']
            except xmlrpclib.Fault:
                pass

        return attachment_id, attachment

    def getAttachments(self, page_id):
        """
        get all known attachments for a provided page id

        Query a specific page identifier for all attachments being held by the
        page.

        Args:
            page_id: the page identifier

        Returns:
            dictionary of attachment identifiers to their respective names
        """
        attachment_info = {}

        if self.use_rest:
            url = 'content/{}/child/attachment'.format(page_id)
            search_fields = {}

            # Configure a larger limit value than the default (no provided
            # limit defaults to 25). This should reduce the number of queries
            # needed to fetch a complete attachment set (for larger sets).
            search_fields['limit'] = 1000;

            rsp = self.rest_client.get(url, search_fields)
            idx = 0
            while rsp['size'] > 0:
                for result in rsp['results']:
                    attachment_info[result['id']] = result['title']

                if rsp['size'] != rsp['limit']:
                    break

                idx += int(rsp['limit'])
                sub_search_fields = dict(search_fields)
                sub_search_fields['start'] = idx;
                rsp = self.rest_client.get(url, sub_search_fields)
        else:
            rsp = self.xmlrpc.getAttachments(self.token, page_id)

            for attachment in rsp:
                attachment_info[attachment['id']] = attachment['fileName']

        return attachment_info

    def getPage(self, page_name):
        """
        get page information with the provided page name

        Performs an API call to acquire known information about a specific page.
        This call can returns both the page identifier (for convenience) and the
        page object. If the page cannot be found, the returned tuple will
        return ``None`` entries.

        Args:
            page_name: the page name

        Returns:
            the page id and page object
        """
        page = None
        page_id = None

        if self.use_rest:
            rsp = self.rest_client.get('content', {
                'type': 'page',
                'spaceKey': self.space_name,
                'title': page_name,
                'status': 'current',
                'expand': 'version'
                })

            if rsp['size'] != 0:
                page = rsp['results'][0]
                page_id = page['id']
        else:
            try:
                page = self.xmlrpc.getPage(
                    self.token, self.space_name, page_name)
                page_id = page['id']
            except xmlrpclib.Fault:
                pass

        return page_id, page

    def storeAttachment(self, page_id, name, data, mimetype, hash, force=False):
        """
        request to store an attachment on a provided page

        Makes a request to a Confluence instance to either publish a new
        attachment or update an existing attachment. If the attachment's hash
        matches the tracked hash (via the comment field) of an existing
        attachment, this call will assume the attachment is already published
        and will return (unless forced).

        Args:
            page_id: the identifier of the page to attach to
            name: the attachment name
            data: the attachment data
            mimetype: the mime type of this attachment
            hash: the hash of the attachment
            force (optional): force publishing if exists (defaults to False)

        Returns:
            the attachment identifier
        """
        HASH_KEY = 'SCB_KEY'
        uploaded_attachment_id = None

        _, attachment = self.getAttachment(page_id, name)

        # check if attachment (of same hash) is already published to this page
        comment = None
        if self.use_rest:
            if attachment and 'metadata' in attachment:
                metadata = attachment['metadata']
                if 'comment' in metadata:
                    comment = metadata['comment']
        else:
            if attachment and 'comment' in attachment:
                comment = attachment['comment']

        if not force and comment:
            parts = comment.split(HASH_KEY + ':')
            if len(parts) > 1:
                tracked_hash = parts[1]
                if hash == tracked_hash:
                    ConfluenceLogger.verbose('attachment ({}) is already '
                        'published to document with same hash'.format(name))
                    return attachment['id']

        # publish attachment
        if self.use_rest:
            try:
                data = {
                    'comment': '{}:{}'.format(HASH_KEY, hash),
                    'file': (name, data, mimetype),
                }

                if not self.notify:
                    # using str over bool to support requests pre-v2.19.0
                    data['minorEdit'] = 'true'

                if not attachment:
                    url = 'content/{}/child/attachment'.format(page_id)
                    rsp = self.rest_client.post(url, None, files=data)
                    uploaded_attachment_id = rsp['results'][0]['id']
                else:
                    url = 'content/{}/child/attachment/{}/data'.format(
                        page_id, attachment['id'])
                    rsp = self.rest_client.post(url, None, files=data)
                    uploaded_attachment_id = rsp['id']

            except ConfluencePermissionError:
                raise ConfluencePermissionError(
                    """Publish user does not have permission to add an """
                    """attachment to the configured space."""
                )
        else:
            isNewAttachment = False
            if not attachment:
                attachment = {
                    'contentType': mimetype,
                    'pageId': page_id,
                    'fileName': name,
                }
                isNewAttachment = True

            attachment['comment'] = '{}:{}'.format(HASH_KEY, hash)

            if not self.notify:
                attachment['minorEdit'] = True

            try:
                uploaded_attachment = self.xmlrpc.addAttachment(
                    self.token, page_id, attachment, data)
            except xmlrpclib.Fault as ex:
                if ex.faultString.find('NotPermittedException') != -1:
                    raise ConfluencePermissionError(
                        """Publish user does not have permission to add an """
                        """attachment to the configured space."""
                    )
                raise
            uploaded_attachment_id = uploaded_attachment['id']

        return uploaded_attachment_id

    def storePage(self, page_name, data, parent_id=None):
        uploaded_page_id = None

        if self.config.confluence_adv_trace_data:
            ConfluenceLogger.trace('data', data)

        _, page = self.getPage(page_name)

        if self.use_rest:
            try:
                if not page:
                    newPage = {
                        'type': 'page',
                        'title': page_name,
                        'body': {
                            'storage': {
                                'representation': 'storage',
                                'value': data
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
                    last_version = int(page['version']['number'])
                    updatePage = {
                        'id': page['id'],
                        'type': 'page',
                        'title': page_name,
                        'body': {
                            'storage': {
                                'representation': 'storage',
                                'value': data
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

                    try:
                        self.rest_client.put('content', page['id'], updatePage)
                    except ConfluenceBadApiError as ex:
                        # Confluence Cloud may (rarely) fail to complete a
                        # content request with an OptimisticLockException/
                        # StaleObjectStateException exception. It is suspected
                        # that this is just an instance timing/processing issue.
                        # If this is observed, wait a moment and retry the
                        # content request. If it happens again, the put request
                        # will fail as it normally would.
                        if str(ex).find('OptimisticLockException') == -1:
                            raise
                        ConfluenceLogger.warn(
                            'remote page updated failed; retrying...')
                        time.sleep(1)
                        self.rest_client.put('content', page['id'], updatePage)

                    uploaded_page_id = page['id']
            except ConfluencePermissionError:
                raise ConfluencePermissionError(
                    """Publish user does not have permission to add page """
                    """content to the configured space."""
                )
        else:
            isNewPage = False
            if not page:
                page = {
                    'title': page_name,
                    'space': self.space_name
                }
                isNewPage = True

            page['content'] = data

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

    def removeAttachment(self, page_id, id, name):
        """
        request to remove an attachment

        Makes a request to a Confluence instance to remove an existing
        attachment.

        Args:
            page_id: the identifier of the page to remove from (XML-RPC only)
            id: the attachment (REST only)
            name: name of the attachment (XML-RPC only)
        """
        if self.use_rest:
            try:
                self.rest_client.delete('content', id)
            except ConfluencePermissionError:
                raise ConfluencePermissionError(
                    """Publish user does not have permission to delete """
                    """from the configured space."""
                )
        else:
            try:
                self.xmlrpc.removeAttachment(self.token, page_id, name)
            except xmlrpclib.Fault as ex:
                if ex.faultString.find('NotPermittedException') != -1:
                    raise ConfluencePermissionError(
                        """Publish user does not have permission to delete """
                        """from the configured space."""
                    )
                raise

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

