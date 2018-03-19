# -*- coding: utf-8 -*-
"""
    sphinxcontrib.confluencebuilder.rest
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2017-2018 by the contributors (see AUTHORS file).
    :license: BSD, see LICENSE for details.
"""

import json
import requests

from .exceptions import ConfluenceAuthenticationFailedUrlError
from .exceptions import ConfluenceBadApiError
from .exceptions import ConfluenceBadServerUrlError
from .exceptions import ConfluencePermissionError
from .exceptions import ConfluenceProxyPermissionError
from .exceptions import ConfluenceSeraphAuthenticationFailedUrlError
from .exceptions import ConfluenceTimeoutError
from .std.confluence import API_REST_BIND_PATH

class Rest:
    CONFLUENCE_DEFAULT_ENCODING = 'utf-8'

    def __init__(self, config):
        self.url = config.confluence_server_url
        self.session = requests.Session()
        self.session.timeout = config.confluence_timeout
        self.session.proxies = {
            'http': config.confluence_proxy,
            'https': config.confluence_proxy
        }
        self.session.verify = not config.confluence_disable_ssl_validation
        if config.confluence_server_user:
            self.session.auth = (
                config.confluence_server_user,
                config.confluence_server_pass)
        self.verbosity = config.sphinx_verbosity

    def get(self, key, params):
        restUrl = self.url + API_REST_BIND_PATH + '/' + key
        try:
            rsp = self.session.get(restUrl, params=params)
        except requests.exceptions.Timeout:
            raise ConfluenceTimeoutError(self.url)
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
        err += "MSG: " + rsp.json()['message']
        return err
