# -*- coding: utf-8 -*-
"""
    sphinxcontrib.confluencebuilder.rest
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2017 by the contributors (see AUTHORS file).
    :license: BSD, see LICENSE.txt for details.
"""

import json
import requests

from .exceptions import ConfluenceAuthenticationFailedUrlError
from .exceptions import ConfluenceBadApiError
from .exceptions import ConfluenceBadServerUrlError
from .exceptions import ConfluencePermissionError
from .exceptions import ConfluenceSeraphAuthenticationFailedUrlError
from .exceptions import ConfluenceTimeoutError


class Rest:
    BIND_PATH = "/rest/api/"
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

    def get(self, key, params):
        restUrl = self.url + self.BIND_PATH + key
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
        restUrl = self.url + self.BIND_PATH + key
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

    def put(self, key, value, data):
        restUrl = self.url + self.BIND_PATH + key + "/" + value
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

    def delete(self, key, value):
        restUrl = self.url + self.BIND_PATH + key + "/" + value
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
        if not rsp.ok:
            raise ConfluenceBadApiError(self._format_error(rsp, key))

    def _format_error(self, rsp, key):
        err = ""
        err += "REQ: {0}\n".format(rsp.request.method)
        err += "RSP: " + str(rsp.status_code) + "\n"
        err += "URL: " + self.url + self.BIND_PATH + "\n"
        err += "API: " + key + "\n"
        err += "MSG: " + rsp.json()['message']
        return err
