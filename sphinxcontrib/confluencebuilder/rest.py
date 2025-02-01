# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from email.utils import mktime_tz
from email.utils import parsedate_tz
from functools import wraps
from requests.adapters import HTTPAdapter
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
from sphinxcontrib.confluencebuilder.retry import API_NORETRY_ERRORS
from sphinxcontrib.confluencebuilder.retry import API_RETRY_ERRORS
from sphinxcontrib.confluencebuilder.std.confluence import NOCHECK
from sphinxcontrib.confluencebuilder.std.confluence import RSP_HEADER_RETRY_AFTER
import inspect
import json
import math
import random
import requests
import sphinxcontrib.confluencebuilder
import ssl
import time


# the maximum times a request will be retried until stopping (rate limiting)
RATE_LIMITED_MAX_RETRIES = 5

# the maximum duration (in seconds) a retry on a rate-limited request can be
# delayed
RATE_LIMITED_MAX_RETRY_DURATION = 30

# the maximum times a request will be retried until stopping (erred instance)
REMOTE_ERR_MAX_RETRIES = 2

# the maximum duration (in seconds) a retry on a erred request can be delayed
REMOTE_ERR_MAX_RETRY_DURATION = 4


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


def confluence_error_retries():
    """
    a confluence error retry "decorator"

    A utility "decorator" to handle automatic attempt to retry an API call
    if Confluence reports an unexpected server error (e.g. a 5xx error).
    There can be issues where Confluence may have issues with a transaction
    on a page update, or an unexpected error processing properties on a page.
    If such a call is detected, the call will be retried again in hopes that
    it was a one time occurrence.
    """
    def _decorator(func):
        @wraps(func)
        def _wrapper(self, *args, **kwargs):
            if self.config.confluence_publish_retry_attempts:
                retry_attempts = self.config.confluence_publish_retry_attempts
            else:
                retry_attempts = REMOTE_ERR_MAX_RETRIES

            if self.config.confluence_publish_retry_duration:
                retry_duration = self.config.confluence_publish_retry_duration
            else:
                retry_duration = REMOTE_ERR_MAX_RETRY_DURATION

            attempt = 1
            while True:
                try:
                    return func(self, *args, **kwargs)
                except ConfluenceBadApiError as ex:  # noqa: PERF203
                    # if max attempts have been reached, stop any more attempts
                    if attempt > retry_attempts:
                        raise

                    # The following will contain a series of known error
                    # states reported by Confluence and whether we will
                    # consider the reported state as a possible condition
                    # to retry the request.
                    ex_str = str(ex)

                    # Errors to not retry on.
                    if any(x in ex_str for x in API_NORETRY_ERRORS):
                        raise

                    # Always retry on 5xx error codes.
                    if ex.status_code >= 500 and ex.status_code <= 599:
                        pass
                    # Check if the reported state is a retry condition, but
                    # Confluence does not report a 5xx error code for the
                    # state.
                    elif not any(x in ex_str for x in API_RETRY_ERRORS):
                        raise

                    # configure the delay
                    delay = retry_duration

                    # add jitter
                    delay += random.uniform(0.0, 0.5)  # noqa: S311

                    # wait the calculated delay before retrying again
                    reported_delay = math.ceil(delay)
                    logger.info('unexpected rest response detected; '
                                f'retrying in {reported_delay} seconds...')
                    time.sleep(delay)
                    attempt += 1

        return _wrapper
    return _decorator


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

                    # determine the amount of delay to wait again -- either
                    # from the provided delay (if any) or exponential backoff
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
                    logger.info('rate-limit response detected; '
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
        self.scb_version = sphinxcontrib.confluencebuilder.__version__
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
            'User-Agent': f'SphinxConfluenceBuilder/{self.scb_version}',
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
        elif config.confluence_api_token or config.confluence_server_user:
            passwd = config.confluence_api_token
            if passwd is None:
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

    @confluence_error_retries()
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

    @confluence_error_retries()
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

    @confluence_error_retries()
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

    @confluence_error_retries()
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
        publish_debug_opts = self.config.confluence_publish_debug
        dump = PublishDebug.headers in publish_debug_opts
        dump_body = PublishDebug.headers_and_data in publish_debug_opts

        rest_url = f'{self.url}{path}'
        base_req = requests.Request(method, rest_url, *args, **kwargs)
        req = self.session.prepare_request(base_req)

        # debug logging
        if dump:
            # attempt to track the origin of the request
            frame = inspect.currentframe().f_back.f_back
            while frame and frame.f_code.co_name.startswith('_wrapper'):
                frame = frame.f_back
            origin = frame.f_code.co_name if frame else 'unknown'

            # filter out special header items, to help avoid users from
            # sharing raw data like authorization data in tickets, etc.;
            # advanced users can use the hidden `headers_raw` option to
            # see non-redacted content
            filtered_headers = dict(req.headers)
            if PublishDebug.headers_raw not in publish_debug_opts:
                fde = [
                    'Authorization',
                    'Cookie',
                ]
                for entry in fde:
                    if filtered_headers.get(entry):
                        filtered_headers[entry] = '(redacted)'

            print()  # leading newline, if debugging into active line
            print(f'(debug) Request: {origin}]')
            print(f'{req.method} {req.url}')
            print('\n'.join(f'{k}: {v}' for k, v in filtered_headers.items()))
            print(flush=True)

            if dump_body and req.body:
                print('(debug) Request data]')
                content_type = req.headers.get('Content-Type') or ''
                if content_type == 'application/json;charset=utf-8':
                    try:
                        json_data = json.dumps(json.loads(req.body), indent=2)
                        print(json_data)
                    except TypeError:
                        print('(bad-json)')
                else:
                    print('(non-json)')
                print(flush=True)

        # perform the rest request
        rsp = self.session.send(req, timeout=self.timeout)

        # debug logging
        if dump:
            print('(debug) Response]')
            print(f'Code: {rsp.status_code}')
            print('\n'.join(f'{k}: {v}' for k, v in rsp.headers.items()))
            print(flush=True)

            if dump_body and rsp.text:
                print('(debug) Response data]')
                try:
                    rsp.encoding = self.CONFLUENCE_DEFAULT_ENCODING
                    json_data = json.dumps(json.loads(rsp.text), indent=2)
                    print(json_data)
                except ValueError:
                    print('(non-json)')
                print(flush=True)

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
