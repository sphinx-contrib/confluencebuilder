# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from functools import wraps
from email.utils import mktime_tz
from email.utils import parsedate_tz
from sphinxcontrib.confluencebuilder.debug import PublishDebug
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceAuthenticationFailedUrlError
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceBadApiError
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceBadServerUrlError
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceCertificateError
from sphinxcontrib.confluencebuilder.exceptions import ConfluencePermissionError
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceProxyPermissionError
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceRateLimitedError
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceSeraphAuthenticationFailedUrlError
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceSslError
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceTimeoutError
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger as logger
from sphinxcontrib.confluencebuilder.std.confluence import NOCHECK
from sphinxcontrib.confluencebuilder.std.confluence import RSP_HEADER_RETRY_AFTER
from requests.adapters import HTTPAdapter
import json
import math
import random
import requests
import ssl
import time


# the maximum times a request will be retried until stopping
RATE_LIMITED_MAX_RETRIES = 5

# the maximum duration (in seconds) a retry on a rate-limited request can be
# delayed
RATE_LIMITED_MAX_RETRY_DURATION = 30


class SslAdapter(HTTPAdapter):
    def __init__(self, config, *args, **kwargs):
        self._config = config
        super().__init__(*args, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()

        # if a custom certificate is provided, load it into this session's
        # SSL context
        if self._config.confluence_client_cert:
            try:
                cf, kf = self._config.confluence_client_cert
                pw = self._config.confluence_client_cert_pass
                context.load_cert_chain(certfile=cf, keyfile=kf, password=pw)
            except ssl.SSLError as ex:
                raise ConfluenceCertificateError(ex) from ex
        # otherwise, load default certificates on the system
        else:
            context.load_default_certs()

        if self._config.confluence_disable_ssl_validation:
            context.check_hostname = False

        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

    def cert_verify(self, conn, url, verify, *args, **kwargs):
        super().cert_verify(conn, url, verify, *args, **kwargs)

        # prevent requests from injecting embedded certificates instead of
        # relying on the default certificate stores loaded by the context
        if verify is True and not self._config.confluence_adv_embedded_certs:
            conn.ca_certs = None


def rate_limited_retries():
    """
    a rest rate limited "decorator"

    A utility "decorator" to handle rate-limited retries if Confluence reports
    that API calls should be limited.
    """
    def _decorator(func):
        @wraps(func)
        def _wrapper(self, *args, **kwargs):
            # apply any user-set delay on an api request
            if self.config.confluence_publish_delay:
                delay = self.config.confluence_publish_delay
                logger.verbose('user-set api delay set; '
                               f'waiting {math.ceil(delay)} seconds...')
                time.sleep(delay)

            # if confluence asked us to wait so many seconds before a next
            # api request, wait a moment
            if self.next_delay:
                delay = self.next_delay
                logger.verbose('rate-limit header detected; '
                               f'waiting {math.ceil(delay)} seconds...')
                time.sleep(delay)
                self.next_delay = None

            # if we have imposed some rate-limiting requests where confluence
            # did not provide retry information, slowly decrease our tracked
            # delay if requests are going through
            self.last_retry = max(self.last_retry / 2, 1)

            attempt = 1
            while True:
                try:
                    return func(self, *args, **kwargs)
                except ConfluenceRateLimitedError:  # noqa: PERF203
                    # if max attempts have been reached, stop any more attempts
                    if attempt > RATE_LIMITED_MAX_RETRIES:
                        raise

                    # determine the amount of delay to wait again -- either from the
                    # provided delay (if any) or exponential backoff
                    if self.next_delay:
                        delay = self.next_delay
                        self.next_delay = None
                    else:
                        delay = 2 * self.last_retry

                    # cap delay to a maximum
                    delay = min(delay, RATE_LIMITED_MAX_RETRY_DURATION)

                    # add jitter
                    delay += random.uniform(0.3, 1.3)  # noqa: S311

                    # wait the calculated delay before retrying again
                    logger.warn('rate-limit response detected; '
                                f'waiting {math.ceil(delay)} seconds...')
                    time.sleep(delay)
                    self.last_retry = delay
                    attempt += 1

        return _wrapper
    return _decorator


def requests_exception_wrappers():
    """
    requests exception wrapping

    A utility "decorator" which will wrap common Requests exceptions with this
    extension's tailored exception types.
    """
    def _decorator(func):
        @wraps(func)
        def _wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except requests.exceptions.Timeout as ex:
                raise ConfluenceTimeoutError(self.url) from ex
            except requests.exceptions.SSLError as ex:
                raise ConfluenceSslError(self.url, ex) from ex
            except requests.exceptions.ConnectionError as ex:
                raise ConfluenceBadServerUrlError(self.url, ex) from ex

        return _wrapper
    return _decorator


class Rest:
    CONFLUENCE_DEFAULT_ENCODING = 'utf-8'

    def __init__(self, config):
        self.config = config
        self.last_retry = 1
        self.next_delay = None
        self.url = config.confluence_server_url
        self.session = None
        self.timeout = config.confluence_timeout
        self.verbosity = config.sphinx_verbosity
        self._reported_large_delay = False

        self.session = self._setup_session(config)

    def __del__(self):
        if self.session:
            self.session.close()

    def _setup_session(self, config):
        session = requests.Session()
        session.headers.update({
            'Accept': 'application/json; charset=utf-8',
            'User-Agent': 'Sphinx Confluence Builder',
            'X-Atlassian-Token': NOCHECK,
        })

        if config.confluence_proxy is not None:
            session.proxies = {
                'http': config.confluence_proxy,
                'https': config.confluence_proxy,
            }

        # add pat into header if provided
        if config.confluence_publish_token:
            session.headers.update({
                'Authorization': 'Bearer ' + config.confluence_publish_token,
            })

        # add custom header options based off the user's configuration
        if config.confluence_publish_headers:
            session.headers.update(config.confluence_publish_headers)

        if config.confluence_disable_ssl_validation:
            session.verify = False
        elif config.confluence_ca_cert:
            session.verify = config.confluence_ca_cert
        else:
            session.verify = True

        # mount custom ssl adapter to support various secure-session options
        adapter = SslAdapter(config)
        session.mount('https://', adapter)

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

    @rate_limited_retries()
    @requests_exception_wrappers()
    def get(self, path, params=None):
        rsp = self._process_request('GET', path, params=params)

        if not rsp.ok:
            errdata = self._format_error(rsp, path)
            raise ConfluenceBadApiError(rsp.status_code, errdata)
        if not rsp.text:
            raise ConfluenceSeraphAuthenticationFailedUrlError

        try:
            rsp.encoding = self.CONFLUENCE_DEFAULT_ENCODING
            json_data = json.loads(rsp.text)
        except ValueError as ex:
            msg = 'REST reply did not provide valid JSON data.'
            raise ConfluenceBadServerUrlError(self.url, msg) from ex

        return json_data

    @rate_limited_retries()
    @requests_exception_wrappers()
    def post(self, path, data, files=None):
        rsp = self._process_request('POST', path, json=data, files=files)

        if not rsp.ok:
            errdata = self._format_error(rsp, path)
            if self.verbosity > 0:
                errdata += "\n"
                errdata += json.dumps(data, indent=2)
            raise ConfluenceBadApiError(rsp.status_code, errdata)
        if not rsp.text:
            raise ConfluenceSeraphAuthenticationFailedUrlError

        try:
            rsp.encoding = self.CONFLUENCE_DEFAULT_ENCODING
            json_data = json.loads(rsp.text)
        except ValueError as ex:
            msg = 'REST reply did not provide valid JSON data.'
            raise ConfluenceBadServerUrlError(self.url, msg) from ex

        return json_data

    @rate_limited_retries()
    @requests_exception_wrappers()
    def put(self, path, value, data):
        rsp = self._process_request('PUT', f'{path}/{value}', json=data)

        if not rsp.ok:
            errdata = self._format_error(rsp, path)
            if self.verbosity > 0:
                errdata += "\n"
                errdata += json.dumps(data, indent=2)
            raise ConfluenceBadApiError(rsp.status_code, errdata)
        if not rsp.text:
            raise ConfluenceSeraphAuthenticationFailedUrlError

        try:
            rsp.encoding = self.CONFLUENCE_DEFAULT_ENCODING
            json_data = json.loads(rsp.text)
        except ValueError as ex:
            msg = 'REST reply did not provide valid JSON data.'
            raise ConfluenceBadServerUrlError(self.url, msg) from ex

        return json_data

    @rate_limited_retries()
    @requests_exception_wrappers()
    def delete(self, path, value):
        rsp = self._process_request('DELETE', f'{path}/{value}')

        if not rsp.ok:
            errdata = self._format_error(rsp, path)
            raise ConfluenceBadApiError(rsp.status_code, errdata)

    def close(self):
        self.session.close()

    def _format_error(self, rsp, path):
        err = ""
        err += f"REQ: {rsp.request.method}\n"
        err += "RSP: " + str(rsp.status_code) + "\n"
        err += "URL: " + self.url + "\n"
        err += "API: " + path + "\n"
        try:
            err += f'DATA: {json.dumps(rsp.json(), indent=2)}'
        except:  # noqa: E722
            err += 'DATA: <not-or-invalid-json>'
        return err

    def _process_request(self, method, path, *args, **kwargs):
        dump = PublishDebug.headers in self.config.confluence_publish_debug

        rest_url = f'{self.url}{path}'
        base_req = requests.Request(method, rest_url, *args, **kwargs)
        req = self.session.prepare_request(base_req)

        # debug logging
        if dump:
            print('')  # leading newline, if debugging into active line
            print('(debug) Request]')
            print(f'{req.method} {req.url}')
            print('\n'.join(f'{k}: {v}' for k, v in req.headers.items()))
            print('', flush=True)

        # perform the rest request
        rsp = self.session.send(req, timeout=self.timeout)

        # debug logging
        if dump:
            print('(debug) Response]')
            print(f'Code: {rsp.status_code}')
            print('\n'.join(f'{k}: {v}' for k, v in rsp.headers.items()))
            print('', flush=True)

        # if confluence or a proxy reports a retry-after delay (to pace us),
        # track it to delay the next request made
        # (https://datatracker.ietf.org/doc/html/rfc2616.html#section-14.37)
        raw_delay = rsp.headers.get(RSP_HEADER_RETRY_AFTER)
        if raw_delay:
            delay = None
            try:
                # attempt to parse a seconds value from the header
                delay = int(raw_delay)
            except ValueError:
                # if seconds are not provided, attempt to parse
                parsed_dtz = parsedate_tz(raw_delay)
                if parsed_dtz:
                    target_datetime = mktime_tz(parsed_dtz)
                    delay = target_datetime - time.time()

            if delay > 0:
                self.next_delay = delay

                # if this delay is over a minute, provide a notice to a client
                # that requests are being delayed -- but we'll only notify a
                # user once
                if delay >= 60 and not self._reported_large_delay:
                    logger.warn('(warning) site has reported a long '
                                'rate-limit delay '
                                f'({math.ceil(delay)} seconds)')
                    self._reported_large_delay = True

        # check if Confluence reports a `Deprecation` header in the response;
        # if so, log a message is we have the debug message enabled to help
        # inform developers that this api call may required updating
        if PublishDebug.deprecated in self.config.confluence_publish_debug:
            if rsp.headers.get('Deprecation'):
                logger.warn(f'(warning) deprecated api call made: {path}')

        if rsp.status_code == 401:
            raise ConfluenceAuthenticationFailedUrlError
        if rsp.status_code == 403:
            msg = 'rest-call'
            raise ConfluencePermissionError(msg)
        if rsp.status_code == 407:
            raise ConfluenceProxyPermissionError
        if rsp.status_code == 429:
            raise ConfluenceRateLimitedError

        return rsp
