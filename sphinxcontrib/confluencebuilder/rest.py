# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2017-2022 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from sphinxcontrib.confluencebuilder.exceptions import ConfluenceAuthenticationFailedUrlError
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceBadApiError
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceBadServerUrlError
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceCertificateError
from sphinxcontrib.confluencebuilder.exceptions import ConfluencePermissionError
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceProxyPermissionError
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceRateLimited
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceSeraphAuthenticationFailedUrlError
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceSslError
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceTimeoutError
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger as logger
from sphinxcontrib.confluencebuilder.std.confluence import API_REST_BIND_PATH
from sphinxcontrib.confluencebuilder.std.confluence import NOCHECK
from sphinxcontrib.confluencebuilder.std.confluence import RSP_HEADER_RETRY_AFTER
from requests.adapters import HTTPAdapter
import json
import math
import random
import requests
import ssl
import time


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


class Rest(object):
    CONFLUENCE_DEFAULT_ENCODING = 'utf-8'

    def __init__(self, config):
        self.url = config.confluence_server_url
        self.session = self._setup_session(config)
        self.timeout = config.confluence_timeout
        self.verbosity = config.sphinx_verbosity

    def __del__(self):
        self.session.close()

    def _setup_session(self, config):
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Sphinx Confluence Builder',
            'X-Atlassian-Token': NOCHECK,
        })

        if config.confluence_proxy is not None:
            session.proxies = {
                'http': config.confluence_proxy,
                'https': config.confluence_proxy,
            }

        # add custom header options based off the user's configuration
        if config.confluence_publish_headers:
            session.headers.update(config.confluence_publish_headers)

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

        if config.confluence_server_auth:
            session.auth = config.confluence_server_auth
        elif config.confluence_server_user:
            passwd = config.confluence_server_pass
            if passwd is None:
                passwd = ''
            session.auth = (config.confluence_server_user, passwd)

        if config.confluence_server_cookies:
            session.cookies.update(config.confluence_server_cookies)

        # provides users a direct hook into manipulating a built requests
        # session, to allow full control over requests capabilities which may
        # not be managed by this extension
        session_override = config.confluence_request_session_override
        if session_override:
            session_override(session)

        return session

    def get(self, key, params):
        rest_url = self.url + API_REST_BIND_PATH + '/' + key

        try:
            rsp = self.session.get(
                rest_url, params=params, timeout=self.timeout)
        except requests.exceptions.Timeout:
            raise ConfluenceTimeoutError(self.url)
        except requests.exceptions.SSLError as ex:
            raise ConfluenceSslError(self.url, ex)
        except requests.exceptions.ConnectionError as ex:
            raise ConfluenceBadServerUrlError(self.url, ex)
        if rsp.status_code == 401:
            raise ConfluenceAuthenticationFailedUrlError
        if rsp.status_code == 403:
            raise ConfluencePermissionError("REST GET")
        if rsp.status_code == 407:
            raise ConfluenceProxyPermissionError
        if rsp.status_code == 429 or RSP_HEADER_RETRY_AFTER in rsp.headers:
            raise ConfluenceRateLimited(rsp.headers.get(RSP_HEADER_RETRY_AFTER))
        if not rsp.ok:
            errdata = self._format_error(rsp, key)
            raise ConfluenceBadApiError(rsp.status_code, errdata)
        if not rsp.text:
            raise ConfluenceSeraphAuthenticationFailedUrlError

        try:
            rsp.encoding = self.CONFLUENCE_DEFAULT_ENCODING
            json_data = json.loads(rsp.text)
        except ValueError:
            raise ConfluenceBadServerUrlError(self.url,
                "REST reply did not provide valid JSON data.")

        return json_data

    def post(self, key, data, files=None):
        rest_url = self.url + API_REST_BIND_PATH + '/' + key
        try:
            rsp = self.session.post(
                rest_url, json=data, files=files, timeout=self.timeout)
        except requests.exceptions.Timeout:
            raise ConfluenceTimeoutError(self.url)
        except requests.exceptions.SSLError as ex:
            raise ConfluenceSslError(self.url, ex)
        except requests.exceptions.ConnectionError as ex:
            raise ConfluenceBadServerUrlError(self.url, ex)
        if rsp.status_code == 401:
            raise ConfluenceAuthenticationFailedUrlError
        if rsp.status_code == 403:
            raise ConfluencePermissionError("REST POST")
        if rsp.status_code == 407:
            raise ConfluenceProxyPermissionError
        if rsp.status_code == 429 or RSP_HEADER_RETRY_AFTER in rsp.headers:
            raise ConfluenceRateLimited(rsp.headers.get(RSP_HEADER_RETRY_AFTER))
        if not rsp.ok:
            errdata = self._format_error(rsp, key)
            if self.verbosity > 0:
                errdata += "\n"
                errdata += json.dumps(data, indent=2)
            raise ConfluenceBadApiError(rsp.status_code, errdata)
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
        rest_url = self.url + API_REST_BIND_PATH + '/' + key + '/' + str(value)
        try:
            rsp = self.session.put(rest_url, json=data, timeout=self.timeout)
        except requests.exceptions.Timeout:
            raise ConfluenceTimeoutError(self.url)
        except requests.exceptions.SSLError as ex:
            raise ConfluenceSslError(self.url, ex)
        except requests.exceptions.ConnectionError as ex:
            raise ConfluenceBadServerUrlError(self.url, ex)
        if rsp.status_code == 401:
            raise ConfluenceAuthenticationFailedUrlError
        if rsp.status_code == 403:
            raise ConfluencePermissionError("REST PUT")
        if rsp.status_code == 407:
            raise ConfluenceProxyPermissionError
        if rsp.status_code == 429 or RSP_HEADER_RETRY_AFTER in rsp.headers:
            raise ConfluenceRateLimited(rsp.headers.get(RSP_HEADER_RETRY_AFTER))
        if not rsp.ok:
            errdata = self._format_error(rsp, key)
            if self.verbosity > 0:
                errdata += "\n"
                errdata += json.dumps(data, indent=2)
            raise ConfluenceBadApiError(rsp.status_code, errdata)
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
        rest_url = self.url + API_REST_BIND_PATH + '/' + key + '/' + str(value)
        try:
            rsp = self.session.delete(rest_url, timeout=self.timeout)
        except requests.exceptions.Timeout:
            raise ConfluenceTimeoutError(self.url)
        except requests.exceptions.SSLError as ex:
            raise ConfluenceSslError(self.url, ex)
        except requests.exceptions.ConnectionError as ex:
            raise ConfluenceBadServerUrlError(self.url, ex)
        if rsp.status_code == 401:
            raise ConfluenceAuthenticationFailedUrlError
        if rsp.status_code == 403:
            raise ConfluencePermissionError("REST DELETE")
        if rsp.status_code == 407:
            raise ConfluenceProxyPermissionError
        if rsp.status_code == 429 or RSP_HEADER_RETRY_AFTER in rsp.headers:
            raise ConfluenceRateLimited(rsp.headers.get(RSP_HEADER_RETRY_AFTER))
        if not rsp.ok:
            errdata = self._format_error(rsp, key)
            raise ConfluenceBadApiError(rsp.status_code, errdata)

    def close(self):
        self.session.close()

    def _format_error(self, rsp, key):
        err = ""
        err += "REQ: {0}\n".format(rsp.request.method)
        err += "RSP: " + str(rsp.status_code) + "\n"
        err += "URL: " + self.url + API_REST_BIND_PATH + "\n"
        err += "API: " + key + "\n"
        try:
            err += 'DATA: {}'.format(json.dumps(rsp.json(), indent=2))
        except:  # noqa: E722
            err += 'DATA: <not-or-invalid-json>'
        return err


class RestRateLimited(Rest):
    def __init__(self, config):
        """
        a rest rate limited instance

        The following is a utility class to handle the same REST API calls
        provided by the `Rest` class, but attempt to handle rate-limited
        retries if Confluence reports that API calls should be limited.

        Args:
            config: the sphinx configuration
        """
        super(RestRateLimited, self).__init__(config)

        self.forced_delay = config.confluence_publish_delay
        self.last_retry = 1
        self.max_retries = 5
        self.max_retry_duration = 30

    def get(self, *args, **kwargs):
        method = super(RestRateLimited, self).get
        return self._process(method, *args, **kwargs)

    def post(self, *args, **kwargs):
        method = super(RestRateLimited, self).post
        return self._process(method, *args, **kwargs)

    def put(self, *args, **kwargs):
        method = super(RestRateLimited, self).put
        return self._process(method, *args, **kwargs)

    def delete(self, *args, **kwargs):
        method = super(RestRateLimited, self).delete
        return self._process(method, *args, **kwargs)

    def _process(self, call, *args, **kwargs):
        # apply any user-set delay on an api request
        if self.forced_delay:
            time.sleep(self.forced_delay)

        attempt = 1
        self.last_retry = max(self.last_retry / 2, 1)
        while True:
            try:
                return call(*args, **kwargs)
            except ConfluenceRateLimited as e:
                # if max attempts have been reached, stop any more attempts
                if attempt > self.max_retries:
                    raise e

                # determine the amount of delay to wait again -- either from the
                # provided delay (if any) or exponential backoff
                if e.delay:
                    delay = e.delay
                else:
                    delay = 2 * self.last_retry

                # cap delay to a maximum
                delay = min(delay, self.max_retry_duration)

                # add jitter
                delay += random.uniform(0.3, 1.3)

                # wait the calculated delay before retrying again
                logger.warn('rate-limit response detected; '
                            'waiting {} seconds...'.format(math.ceil(delay)))
                time.sleep(delay)
                self.last_retry = delay
                attempt += 1
