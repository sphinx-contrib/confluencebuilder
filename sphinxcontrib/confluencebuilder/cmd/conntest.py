# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from contextlib import suppress
from enum import Enum
from pathlib import Path
from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace
from sphinxcontrib.confluencebuilder.config import process_ask_configs
from sphinxcontrib.confluencebuilder.config.defaults import apply_defaults
from sphinxcontrib.confluencebuilder.config.env import apply_env_overrides
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger as logger
from sphinxcontrib.confluencebuilder.publisher import ConfluencePublisher
from sphinxcontrib.confluencebuilder.reportbuilder import ConfluenceReportBuilder
from sphinxcontrib.confluencebuilder.util import ConfluenceUtil
from sphinxcontrib.confluencebuilder.util import temp_dir
from urllib.parse import urlparse
import json
import os
import requests
import sys
import traceback


#: rest point to fetch instance manifest state
MANIFEST_PATH = 'rest/applinks/1.0/manifest'


def conntest_main(args_parser):
    """
    connection test mainline

    The mainline for the 'connection-test' action.

    Args:
        args_parser: the argument parser to use for argument processing

    Returns:
        the exit code
    """

    args_parser.add_argument('--no-sanitize', action='store_true')

    known_args = sys.argv[1:]
    args, unknown_args = args_parser.parse_known_args(known_args)
    if unknown_args:
        logger.warn('unknown arguments: {}'.format(' '.join(unknown_args)))

    work_dir = args.work_dir if args.work_dir else Path.cwd()

    # ##################################################################
    # setup sphinx engine to extract configuration
    # ##################################################################
    config = {}
    publisher = ConfluencePublisher()

    try:
        with temp_dir() as tmp_dir, docutils_namespace():
            print('Fetching configuration information...')
            builder = ConfluenceReportBuilder.name
            oconf = {
                'extensions': [  # ignore extensions (except us)
                    'sphinxcontrib.confluencebuilder',
                ],
            }
            app = Sphinx(
                work_dir,             # document sources
                work_dir,             # directory with configuration
                tmp_dir,              # output for built documents
                tmp_dir,              # output for doctree files
                builder,              # builder to execute
                confoverrides=oconf,  # override configurations
                status=sys.stdout,    # sphinx status output
                warning=sys.stderr)   # sphinx warning output

            # apply environment-based configuration changes
            apply_env_overrides(app.builder)

            # extract configuration information
            for key in app.config.values:
                # ignore (most) non-extension options
                # (we only care for publishing-related ones)
                if not key.startswith('confluence_'):
                    continue

                raw = getattr(app.config, key)
                if raw is None:
                    continue

                value = '(callable)' if callable(raw) else raw
                config[key] = value

            # ensure internal defaults are applied after we already extracted
            # raw values and before attempting to use the publisher
            apply_defaults(app.builder)

            # initialize the publisher
            publisher.init(app.config)
            print()

    except Exception:  # noqa: BLE001
        sys.stdout.flush()
        tb_msg = traceback.format_exc()
        logger.error(tb_msg)
        if Path(work_dir / 'conf.py').is_file():
            print('unable to load configuration')
            print('\n\n' + tb_msg.strip())
        else:
            print('no documentation/missing configuration')
        return 1

    # ##################################################################
    # only run if publishing is enabled
    # ##################################################################
    confluence_publish = config.get('confluence_publish')
    if not confluence_publish:
        print('configuration has not explicitly enabled publishing')
        print('(ensure "confluence_publish = True")')
        return 1

    # ##################################################################
    # dump relevant configurations
    # ##################################################################

    opts = [
        'confluence_adv_embedded_certs',
        'confluence_api_token',
        'confluence_ca_cert',
        'confluence_client_cert',
        'confluence_client_cert_pass',
        'confluence_disable_ssl_validation',
        'confluence_proxy',
        'confluence_publish_disable_api_prefix',
        'confluence_publish_headers',
        'confluence_publish_token',
        'confluence_request_session_override',
        'confluence_server_auth',
        'confluence_server_cookies',
        'confluence_server_pass',
        'confluence_server_url',
        'confluence_server_user',
        'confluence_space_key',
    ]

    print("Network-related configurations]")
    for opt in opts:
        if opt in config:
            if config[opt]:
                value = str(config[opt]) if args.no_sanitize else '(set)'
            else:
                value = '(set; empty)'
        else:
            value = '(not set)'

        print(f' {opt}: {value}')
    print()

    # ##################################################################
    # configuration checks
    # ##################################################################

    print("Sanity checks]")
    is_cloud = False
    is_https = False
    is_http = False

    # check confluence_server_url
    confluence_server_url = config.get('confluence_server_url')
    base_url = ConfluenceUtil.normalize_base_url(confluence_server_url)

    print('Checking that "confluence_server_url" is set... ', end='')
    if confluence_server_url:
        print('good.')

        print('Checking "confluence_server_url" value... ', end='')
        try:
            parsed = urlparse(confluence_server_url)
        except ValueError:
            print('invalid value!')
            return 1
        else:
            if parsed.scheme:
                if parsed.scheme == 'https':
                    is_https = True
                    print('good (HTTPS).')
                elif parsed.scheme == 'http':
                    is_http = True
                    print('good (HTTP).')
                else:
                    print(f'warning; unknown scheme ({parsed.scheme}).')
            else:
                print('warning; missing scheme.')

            if parsed.netloc and parsed.netloc.endswith('atlassian.net'):
                print('Detected an Atlassian Cloud configuration.')
                is_cloud = True
    else:
        print('error!')
        return 1

    print(f'Confluence base URL: {base_url}')

    print('Confluence API endpoints:')
    print(f' v1: {base_url}{publisher.APIV1}')
    print(f' v2: {base_url}{publisher.APIV2}')

    # check confluence_space_key
    confluence_space_key = config.get('confluence_space_key')

    print('Checking that "confluence_space_key" is set... ', end='')
    if confluence_space_key:
        print('good.')

        print('Checking "confluence_space_key" value... ', end='')
        if confluence_space_key.isupper():
            print('looks good.')
        else:
            print('warning; not uppercase!')
    else:
        print('error!')
        return 1

    # proxy
    # (confluence_proxy, http_proxy, https_proxy)
    env = os.environ
    proxy = env.get('all_proxy', os.getenv('ALL_PROXY'))
    http_proxy = env.get('http_proxy', env.get('HTTP_PROXY', proxy))
    https_proxy = env.get('https_proxy', env.get('HTTPS_PROXY', proxy))

    print('Checking proxy settings... ', end='')
    if config.get('confluence_proxy') is not None:
        print('explicit proxy configured.')
    elif http_proxy or https_proxy:
        print('proxy options detected.')

        if is_https and not https_proxy:
            print('(warning) Proxy options detected, '
                  'but no https_proxy option set for https Confluence URL!')
        elif is_http and not http_proxy:
            print('(warning) Proxy options detected, '
                  'but no http_proxy option set for http Confluence URL!')
    else:
        print('no proxy configured.')

    # confluence_publish_token
    if is_cloud and config.get('confluence_publish_token'):
        print('(warning) Publish token (PAT) configured, '
              'but does not look like a Confluence self-hosted instance!')

    # confluence_publish_token
    pat = config.get('confluence_publish_token')
    if is_cloud and pat:
        print('(warning) Publish token (PAT) configured, '
              'but does not look like a Confluence self-hosted instance!')

    # confluence_publish_headers
    confluence_publish_headers = config.get('confluence_publish_headers')
    if confluence_publish_headers and pat:
        if 'Authorization' in confluence_publish_headers:
            print('(warning) Publish token (PAT) configured, '
                  'but "Authorization" header overridden by '
                  'confluence_publish_headers!')

    # confluence_server_auth
    if config.get('confluence_server_auth'):
        print('(note) Custom server authentication override detected!')

    # confluence_server_cookies
    if config.get('confluence_server_cookies'):
        print('(note) Custom server cookies overrides detected!')

    # confluence_request_session_override
    if config.get('confluence_request_session_override'):
        print('(note) Custom session overrides detected!')

    # confluence_server_pass + pat
    confluence_server_pass = config.get('confluence_server_pass')
    if confluence_server_pass and pat:
        print('(warning) Both server password/API token configured at the '
              'same time with a personal access token (PAT)!')

    # confluence_api_token + confluence_server_pass
    confluence_api_token = config.get('confluence_api_token')
    if confluence_api_token and confluence_server_pass:
        print('(warning) API token configured at the '
              'same time with a password!')

    # !confluence_server_user + confluence_server_pass
    confluence_server_user = config.get('confluence_server_user')
    if not confluence_server_user and confluence_server_pass:
        print('(warning) No user configured, but a server password/API '
              'has been configured!')

    print()

    # ##################################################################
    # connection check
    # ##################################################################

    print("Connection check]")

    sys.stdout.flush()
    process_ask_configs(app.config)

    try:
        print('Connecting to Confluence instance... ', end='')
        sys.stdout.flush()

        publisher.connect()
        print('connected!')
    except Exception:  # noqa: BLE001
        print('failed!', flush=True)
        logger.error(traceback.format_exc())
    else:
        try:
            print('Fetching Confluence instance information... ', end='')
            sys.stdout.flush()

            manifest_url = base_url + MANIFEST_PATH
            rsp = publisher.rest.session.get(manifest_url)

            if rsp.status_code == 200:
                print('fetched!')

                # extract
                print('Decoding information... ', end='')
                rsp.encoding = 'utf-8'
                raw_data = rsp.text
                print('decoded!')

                # parse
                try:
                    print('Parsing information... ', end='')
                    json_data = json.loads(raw_data)
                except ValueError as ex:
                    print('error!', flush=True)
                    logger.error(f'bad parse ({ex})')
                    print(raw_data)
                    return 1
                else:
                    print('parsed!')
                    build_number = json_data.get('buildNumber', '(unknown)')
                    type_id = json_data.get('typeId', '(unknown)')
                    version = json_data.get('version', '(unknown)')

                    print(f'    Type: {type_id}')
                    print(f' Version: {version}')
                    print(f'   Build: {build_number}')
            else:
                print('error!', flush=True)
                logger.error(f'bad response ({rsp.status_code})')
                return 1
        except Exception:  # noqa: BLE001
            print('error!', flush=True)
            logger.error(traceback.format_exc())
            return 1

        return 0

    print('Connection failure. Probing...')
    conntest_probe(app.config)
    return 1


class ProbeModes(Enum):
    clean = 'no-auth-no-headers'
    auth = 'with-http-auth'
    headers = 'with-headers'
    pat = 'with-pat'


def conntest_probe(config):
    api_token = config.confluence_api_token
    ca_cert = config.confluence_ca_cert or True
    pat = config.confluence_publish_token
    publish_headers = config.confluence_publish_headers
    server_pass = config.confluence_server_pass or ''
    server_user = config.confluence_server_user
    space_key = config.confluence_space_key
    url = config.confluence_server_url
    auth_value = api_token or server_pass

    space_queries = {
        'v1': {
            'bind': 'rest/api',
            'path': 'space',
            'params': {
                'spaceKey': space_key,
                'limit': 1,
            },
        },
        'v2': {
            'bind': 'api/v2',
            'path': 'spaces',
            'params': {
                'keys': space_key,
                'limit': 1,
            },
        },
    }

    print('Will attempt to probe multiple API endpoints.')
    for mode in ProbeModes:
        for api_ver, opts in space_queries.items():
            print(f'Probing {api_ver} ({mode.value})...', end='', flush=True)
            auth = None
            headers = None

            if mode == ProbeModes.auth:
                if server_user:
                    auth = (server_user, auth_value)
                    headers = publish_headers
                else:
                    print('skipped (no username configured).')
                    continue

            if mode == ProbeModes.headers:
                if publish_headers:
                    headers = publish_headers
                else:
                    print('skipped (no custom headers configured).')
                    continue

            if mode == ProbeModes.pat:
                if pat:
                    headers = {
                        'Authorization': 'Bearer ' + pat,
                    }
                else:
                    print('skipped (no PAT configured).')
                    continue

            req_url = f'{url}{opts["bind"]}/{opts["path"]}'
            try:
                rsp = requests.get(
                    req_url,
                    auth=auth,
                    headers=headers,
                    params=opts['params'],
                    timeout=60,
                    verify=ca_cert,
                )
            except Exception:  # noqa: BLE001
                print(flush=True)
                tb_msg = traceback.format_exc()
                logger.error(tb_msg)
            else:
                json_data = None
                with suppress(ValueError):
                    rsp.encoding = 'utf-8'
                    json_data = json.loads(rsp.text)

                sts_txt = 'good' if rsp.ok else 'fail'
                is_json = 'yes' if json_data else 'no'
                print(f'{sts_txt} (code: {rsp.status_code}; json: {is_json}).')

                if json_data:
                    print(f'({req_url})')
                    print(json.dumps(json_data, indent=2))
                    print()

    print('Probing has completed.')
