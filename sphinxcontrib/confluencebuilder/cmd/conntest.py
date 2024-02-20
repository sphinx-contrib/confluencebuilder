# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace
from sphinxcontrib.confluencebuilder.std.confluence import API_REST_BIND_PATH
from sphinxcontrib.confluencebuilder.config import process_ask_configs
from sphinxcontrib.confluencebuilder.config.env import apply_env_overrides
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger as logger
from sphinxcontrib.confluencebuilder.publisher import ConfluencePublisher
from sphinxcontrib.confluencebuilder.reportbuilder import ConfluenceReportBuilder
from sphinxcontrib.confluencebuilder.util import ConfluenceUtil
from sphinxcontrib.confluencebuilder.util import temp_dir
from urllib.parse import urlparse
from xml.etree import ElementTree
import os
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

    args_parser.add_argument('--dump-cfg', action='store_true')

    known_args = sys.argv[1:]
    args, unknown_args = args_parser.parse_known_args(known_args)
    if unknown_args:
        logger.warn('unknown arguments: {}'.format(' '.join(unknown_args)))

    work_dir = args.work_dir if args.work_dir else os.getcwd()

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

            # initialize the publisher
            publisher.init(app.config)
            print('')

    except Exception:  # noqa: BLE001
        sys.stdout.flush()
        tb_msg = traceback.format_exc()
        logger.error(tb_msg)
        if os.path.isfile(os.path.join(work_dir, 'conf.py')):
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
    # dump relavant configurations
    # ##################################################################
    if args.dump_cfg:
        opts = [
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
                if config[opt].strip():
                    value = config[opt]
                else:
                    value = '(set; empty)'
            else:
                value = '(not set)'

            print(f' {opt}: {value}')
        print('')

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
        print('set.')

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
                print('Detected an Atlassian Cloud instance.')
                is_cloud = True
    else:
        print('error!')
        return 1

    print(f'Confluence base URL: {base_url}')

    bind_path = API_REST_BIND_PATH
    if config.get('confluence_publish_disable_api_prefix'):
        bind_path = ''
        print('Note: API endpoint prefixed disabled by configuration!')

    print(f'Confluence API endpoint: {base_url}{bind_path}')

    # check confluence_space_key
    confluence_space_key = config.get('confluence_space_key')

    print('Checking that "confluence_space_key" is set... ', end='')
    if confluence_space_key:
        print('set.')

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

    # confluence_publish_token
    confluence_server_pass = config.get('confluence_server_pass')
    if confluence_server_pass and pat:
        print('(warning) Both server password/API token configured at the '
              'same time with a personal access token (PAT)!')

    # confluence_publish_token
    confluence_server_user = config.get('confluence_server_user')
    if not confluence_server_user and confluence_server_pass:
        print('(warning) No user configured, but a server password/API '
              'has been configured!')

    print("")

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
        print('failed to connect!')
        logger.error(traceback.format_exc())
        return 1
    else:
        try:
            print('Fetching Confluence instance information... ', end='')
            sys.stdout.flush()

            manifest_url = base_url + MANIFEST_PATH
            rsp = publisher.rest_client.session.get(manifest_url)

            if rsp.status_code == 200:
                print('fetched!')

                # extract
                print('Decoding information... ', end='')
                rsp.encoding = 'utf-8'
                raw_data = rsp.text
                print('decoded!')

                # parse
                print('Parsing information... ', end='')
                xml_data = ElementTree.fromstring(raw_data)
                print('parsed!')

                root = ElementTree.ElementTree(xml_data)
                for o in root.findall('typeId'):
                    print(f'    Type: {o.text}')
                for o in root.findall('version'):
                    print(f' Version: {o.text}')
                for o in root.findall('buildNumber'):
                    print(f'   Build: {o.text}')
            else:
                print('error!')
                logger.error(f'bad response ({rsp.status_code})')
                return 1
        except Exception:  # noqa: BLE001
            print('error!')
            logger.error(traceback.format_exc())
            return 1

    return 0
