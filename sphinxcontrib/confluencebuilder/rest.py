# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2017-2018 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from .exceptions import ConfluenceAuthenticationFailedUrlError
from .exceptions import ConfluenceBadApiError
from .exceptions import ConfluenceBadServerUrlError
from .exceptions import ConfluenceCertificateError
from .exceptions import ConfluencePermissionError
from .exceptions import ConfluenceProxyPermissionError
from .exceptions import ConfluenceSSLError
from .exceptions import ConfluenceSeraphAuthenticationFailedUrlError
from .exceptions import ConfluenceTimeoutError
from .std.confluence import API_REST_BIND_PATH
from requests.adapters import HTTPAdapter
import json
import requests
import ssl

class SslAdapter(HTTPAdapter):
    def __init__(self, cert, password=None, disable_validation=False,
                 *args, **kwargs):
        self._certfile, self._keyfile = cert
        self._password = password
        self._disable_validation = disable_validation
        super(SslAdapter, self).__init__(*args, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        try:
            context.load_cert_chain(certfile=self._certfile,
                                    keyfile=self._keyfile,
                                    password=self._password)
        except ssl.SSLError as ex:
            raise ConfluenceCertificateError(ex)
        if self._disable_validation:
            context.check_hostname = False

        kwargs['ssl_context'] = context
        return super(SslAdapter, self).init_poolmanager(*args, **kwargs)

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
            adapter = SslAdapter(config.confluence_client_cert,
                                 config.confluence_client_cert_pass,
                                 config.confluence_disable_ssl_validation)
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
