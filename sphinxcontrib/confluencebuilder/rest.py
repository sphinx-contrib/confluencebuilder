# -*- coding: utf-8 -*-
"""
    sphinxcontrib.confluencebuilder.rest
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2017-2018 by the contributors (see AUTHORS file).
    :license: BSD, see LICENSE for details.
"""

import json
import ssl
import requests
from requests.adapters import HTTPAdapter

from .exceptions import ConfluenceAuthenticationFailedUrlError
from .exceptions import ConfluenceBadApiError
from .exceptions import ConfluenceBadServerUrlError
from .exceptions import ConfluencePermissionError
from .exceptions import ConfluenceProxyPermissionError
from .exceptions import ConfluenceSeraphAuthenticationFailedUrlError
from .exceptions import ConfluenceTimeoutError
from .exceptions import ConfluenceSSLError
from .std.confluence import API_REST_BIND_PATH

class SSLAdapter(HTTPAdapter):
    def __init__(self, cert, password=None, *args, **kwargs):
        if isinstance(cert, tuple) and len(cert) >= 2:
            if len(cert) < 2:
                self._certfile = cert[0]
                self._keyfile = None
            else:
                self._certfile = cert[0]
                self._keyfile = cert[1]
        else:
            self._certfile = cert
            self._keyfile = None
        self._password = password
        super(SSLAdapter, self).__init__(*args, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_cert_chain(certfile=self._certfile,
                                keyfile=self._keyfile,
                                password=self._password)
        kwargs['ssl_context'] = context
        return super(SSLAdapter, self).init_poolmanager(*args, **kwargs)


class Rest:
    CONFLUENCE_DEFAULT_ENCODING = 'utf-8'

    def __init__(self, config):
        self.url = config.confluence_server_url
        self.session = self._setup_session(config)
        self.verbosity = config.sphinx_verbosity

    def _setup_session(self, config):
        session = requests.Session()
        session.timeout = config.confluence_timeout
        session.proxies = {
            'http': config.confluence_proxy,
            'https': config.confluence_proxy,
        }

        if config.confluence_disable_ssl_validation:
            session.verify = False
        elif config.confluence_ca_cert:
            session.verify = config.confluence_ca_cert
        else:
            session.verify = True

        # In order to support encrypted certificates, we need to
        # use the Adapter pattern that requests uses. If requests
        # ever adds native support for encrypted keys then we can
        # remove the SSLAdapter and just use the native API.
        # see: https://github.com/requests/requests/issues/2519 for more
        # information.
        if config.confluence_client_cert:
            adapter = SSLAdapter(config.confluence_client_cert,
                                 config.confluence_client_cert_pass)
            session.mount(self.url, adapter)

        if config.confluence_server_user:
            session.auth = (
                config.confluence_server_user,
                config.confluence_server_pass)
        return session

    def get(self, key, params):
        restUrl = self.url + API_REST_BIND_PATH + '/' + key
        try:
            rsp = self.session.get(restUrl, params=params)
        except requests.exceptions.Timeout:
            raise ConfluenceTimeoutError(self.url)
        except requests.exceptions.SSLError as ex:
            raise ConfluenceSSLError(self.url, ex)
        except requests.exceptions.ConnectionError as ex:
            raise ConfluenceBadServerUrlError(self.url, ex)
        if rsp.status_code == 401:
            raise ConfluenceAuthenticationFailedUrlError
        if rsp.status_code == 403:
            raise ConfluencePermissionError("REST GET")
        if rsp.status_code == 407:
            raise ConfluenceProxyPermissionError
        if not rsp.ok:
            raise ConfluenceBadApiError(self._format_error(rsp, key))
        if not rsp.text:
            raise ConfluenceSeraphAuthenticationFailedUrlError

        try:
            rsp.encoding = self.CONFLUENCE_DEFAULT_ENCODING
            json_data = json.loads(rsp.text)
        except ValueError:
            raise ConfluenceBadServerUrlError(self.url,
                "REST reply did not provide valid JSON data.")

        return json_data

    def post(self, key, data):
        restUrl = self.url + API_REST_BIND_PATH + '/' + key
        try:
            rsp = self.session.post(restUrl, json=data)
        except requests.exceptions.Timeout:
            raise ConfluenceTimeoutError(self.url)
        except requests.exceptions.SSLError as ex:
            raise ConfluenceSSLError(self.url, ex)
        except requests.exceptions.ConnectionError as ex:
            raise ConfluenceBadServerUrlError(self.url, ex)
        if rsp.status_code == 401:
            raise ConfluenceAuthenticationFailedUrlError
        if rsp.status_code == 403:
            raise ConfluencePermissionError("REST POST")
        if rsp.status_code == 407:
            raise ConfluenceProxyPermissionError
        if not rsp.ok:
            errdata = self._format_error(rsp, key)
            if self.verbosity > 0:
                errdata += "\n"
                errdata += json.dumps(data, indent=2)
            raise ConfluenceBadApiError(errdata)
        if not rsp.text:
            raise ConfluenceSeraphAuthenticationFailedUrlError

        try:
            rsp.encoding = self.CONFLUENCE_DEFAULT_ENCODING
            json_data = json.loads(rsp.text)
        except ValueError:
            raise ConfluenceBadServerUrlError(self.url,
                "REST reply did not provide valid JSON data.")

        return json_data

    def put(self, key, value, data):
        restUrl = self.url + API_REST_BIND_PATH + '/' + key + '/' + value
        try:
            rsp = self.session.put(restUrl, json=data)
        except requests.exceptions.Timeout:
            raise ConfluenceTimeoutError(self.url)
        except requests.exceptions.SSLError as ex:
            raise ConfluenceSSLError(self.url, ex)
        except requests.exceptions.ConnectionError as ex:
            raise ConfluenceBadServerUrlError(self.url, ex)
        if rsp.status_code == 401:
            raise ConfluenceAuthenticationFailedUrlError
        if rsp.status_code == 403:
            raise ConfluencePermissionError("REST PUT")
        if rsp.status_code == 407:
            raise ConfluenceProxyPermissionError
        if not rsp.ok:
            errdata = self._format_error(rsp, key)
            if self.verbosity > 0:
                errdata += "\n"
                errdata += json.dumps(data, indent=2)
            raise ConfluenceBadApiError(errdata)
        if not rsp.text:
            raise ConfluenceSeraphAuthenticationFailedUrlError

        try:
            rsp.encoding = self.CONFLUENCE_DEFAULT_ENCODING
            json_data = json.loads(rsp.text)
        except ValueError:
            raise ConfluenceBadServerUrlError(self.url,
                "REST reply did not provide valid JSON data.")

        return json_data

    def delete(self, key, value):
        restUrl = self.url + API_REST_BIND_PATH + '/' + key + '/' + value
        try:
            rsp = self.session.delete(restUrl)
        except requests.exceptions.Timeout:
            raise ConfluenceTimeoutError(self.url)
        except requests.exceptions.SSLError as ex:
            raise ConfluenceSSLError(self.url, ex)
        except requests.exceptions.ConnectionError as ex:
            raise ConfluenceBadServerUrlError(self.url, ex)
        if rsp.status_code == 401:
            raise ConfluenceAuthenticationFailedUrlError
        if rsp.status_code == 403:
            raise ConfluencePermissionError("REST DELETE")
        if rsp.status_code == 407:
            raise ConfluenceProxyPermissionError
        if not rsp.ok:
            raise ConfluenceBadApiError(self._format_error(rsp, key))

    def close(self):
        self.session.close()

    def _format_error(self, rsp, key):
        err = ""
        err += "REQ: {0}\n".format(rsp.request.method)
        err += "RSP: " + str(rsp.status_code) + "\n"
        err += "URL: " + self.url + API_REST_BIND_PATH + "\n"
        err += "API: " + key + "\n"
        try:
            err += 'MSG: {}'.format(rsp.json()['message'])
        except ValueError:
            err += 'MSG: <not-or-invalid-json>'
        return err
