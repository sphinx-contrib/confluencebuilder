# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from collections import OrderedDict
from docutils import __version__ as docutils_version
from pathlib import Path
from requests import __version__ as requests_version
from sphinx import __version__ as sphinx_version
from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace
from sphinxcontrib.confluencebuilder import __version__ as scb_version
from sphinxcontrib.confluencebuilder.config import process_ask_configs
from sphinxcontrib.confluencebuilder.config.defaults import apply_defaults
from sphinxcontrib.confluencebuilder.config.env import apply_env_overrides
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluenceConfigError
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger as logger
from sphinxcontrib.confluencebuilder.publisher import ConfluencePublisher
from sphinxcontrib.confluencebuilder.reportbuilder import ConfluenceReportBuilder
from sphinxcontrib.confluencebuilder.util import ConfluenceUtil
from sphinxcontrib.confluencebuilder.util import temp_dir
from urllib.parse import urlparse
from urllib3 import __version__ as urllib3_version
import json
import platform
import sys
import traceback


#: rest point to fetch instance manifest state
MANIFEST_PATH = 'rest/applinks/1.0/manifest'

#: prefixes for builder-specific configurations to always be sanitized
IGNORE_BUILDER_CONFS = (
    'applehelp_',
    'devhelp_',
    'epub_',
    'html_',
    'htmlhelp_',
    'latex_',
    'man_',
    'qthelp_',
    'texinfo_',
    'text_',
    'xml_',
)


def report_main(args_parser):
    """
    report mainline

    The mainline for the 'report' action.

    Args:
        args_parser: the argument parser to use for argument processing

    Returns:
        the exit code
    """

    args_parser.add_argument('--full-config', '-C', action='store_true')
    args_parser.add_argument('--no-sanitize', action='store_true')
    args_parser.add_argument('--offline', action='store_true')

    known_args = sys.argv[1:]
    args, unknown_args = args_parser.parse_known_args(known_args)
    if unknown_args:
        logger.warn('unknown arguments: {}'.format(' '.join(unknown_args)))

    rv = 0
    offline = args.offline
    work_dir = args.work_dir if args.work_dir else Path.cwd()

    # setup sphinx engine to extract configuration
    config = {}
    configuration_load_issue = None
    confluence_instance_info = None
    publisher = ConfluencePublisher()

    try:
        with temp_dir() as tmp_dir, docutils_namespace():
            print('fetching configuration information...')
            builder = ConfluenceReportBuilder.name
            app = Sphinx(
                str(work_dir),       # document sources
                str(work_dir),       # directory with configuration
                str(tmp_dir),        # output for built documents
                str(tmp_dir),        # output for doctree files
                builder,             # builder to execute
                status=sys.stdout,   # sphinx status output
                warning=sys.stderr)  # sphinx warning output

            # keep track of unset options in the configuration
            pre_env_keys = set()
            config_manager = app.config_manager_   # pylint: disable=no-member
            for key in config_manager.options:
                if getattr(app.config, key) is None:
                    pre_env_keys.add(key)

            # apply environment-based configuration changes
            apply_env_overrides(app.builder)

            # track for any remaining unset options to see if the environment
            # has changed any options
            post_env_keys = set()
            for key in config_manager.options:
                if getattr(app.config, key) is None:
                    post_env_keys.add(key)

            new_env_keys = pre_env_keys - post_env_keys

            # if the configuration is enabled for publishing, check if
            # we need to ask for authentication information (to perform
            # the connection sanity checks)
            if app.config.confluence_publish:
                try:
                    process_ask_configs(app.config)
                except ConfluenceConfigError:
                    offline = True

            # extract configuration information
            cm = app.config_manager_  # pylint: disable=no-member
            for key in app.config.values:
                raw = getattr(app.config, key)
                if raw is None:
                    continue

                value = '(callable)' if callable(raw) else raw

                if not args.full_config and key not in cm.options:
                    continue

                # always extract some known builder configurations
                if args.full_config and key.startswith(IGNORE_BUILDER_CONFS):
                    continue

                config[key] = value

            # ensure internal defaults are applied after we already extracted
            # raw values and before attempting to use the publisher
            apply_defaults(app.builder)

            # initialize the publisher (if needed later)
            publisher.init(app.config)

    except Exception:  # noqa: BLE001
        sys.stdout.flush()
        tb_msg = traceback.format_exc()
        logger.error(tb_msg)
        if Path(work_dir / 'conf.py').is_file():
            configuration_load_issue = 'unable to load configuration'
            configuration_load_issue += '\n\n' + tb_msg.strip()
        else:
            configuration_load_issue = 'no documentation/missing configuration'
        rv = 1

    # attempt to fetch confluence instance version
    confluence_publish = config.get('confluence_publish')
    confluence_server_url = config.get('confluence_server_url')
    if not offline and confluence_publish and confluence_server_url:
        base_url = ConfluenceUtil.normalize_base_url(confluence_server_url)
        info = ''

        session = None
        try:
            print('connecting to confluence instance...')
            sys.stdout.flush()

            publisher.connect()
            info += ' connected: yes\n'
            session = publisher.rest.session
        except Exception:  # noqa: BLE001
            sys.stdout.flush()
            logger.error(traceback.format_exc())
            info += ' connected: no\n'
            rv = 1

        if session:
            try:
                # fetch
                print('fetching confluence instance information...')
                manifest_url = base_url + MANIFEST_PATH
                rsp = session.get(manifest_url)

                if rsp.status_code == 200:
                    info += '   fetched: yes\n'

                    # extract
                    print('decoding information...')
                    rsp.encoding = 'utf-8'
                    raw_data = rsp.text
                    info += '   decoded: yes\n'

                    # parse
                    print('parsing information...')
                    json_data = json.loads(raw_data)
                    info += '    parsed: yes\n'

                    build_number = json_data.get('buildNumber', '(unknown)')
                    type_id = json_data.get('typeId', '(unknown)')
                    version = json_data.get('version', '(unknown)')

                    info += f'      type: {type_id}\n'
                    info += f'   version: {version}\n'
                    info += f'     build: {build_number}\n'
                else:
                    code = rsp.status_code
                    logger.error(f'bad response from server ({code})')
                    info += f'   fetched: error ({code})\n'
                    rv = 1
            except Exception:  # noqa: BLE001
                sys.stdout.flush()
                logger.error(traceback.format_exc())
                info += 'failure to determine confluence data\n'
                rv = 1

        confluence_instance_info = info

    def sensitive_config(key):
        if key in config:
            if config[key]:
                config[key] = '(set)'
            else:
                config[key] = '(set; empty)'

    # always sanitize out sensitive information
    sensitive_config('confluence_api_token')
    sensitive_config('confluence_client_cert_pass')
    sensitive_config('confluence_publish_headers')
    sensitive_config('confluence_publish_token')
    sensitive_config('confluence_server_pass')

    # optional sanitization
    if not args.no_sanitize:
        sensitive_config('author')
        sensitive_config('confluence_client_cert')
        sensitive_config('confluence_global_labels')
        sensitive_config('confluence_jira_servers')
        sensitive_config('confluence_mentions')
        sensitive_config('confluence_parent_page')
        sensitive_config('confluence_parent_page_id_check')
        sensitive_config('confluence_proxy')
        sensitive_config('confluence_publish_root')
        sensitive_config('confluence_server_auth')
        sensitive_config('confluence_server_cookies')
        sensitive_config('confluence_server_user')
        sensitive_config('project')

        # remove confluence instance (attempt to keep scheme)
        if 'confluence_server_url' in config:
            value = config['confluence_server_url']
            parsed = urlparse(value)

            if parsed.scheme:
                value = parsed.scheme + '://(removed)'
            else:
                value = '(set; no scheme)'

            if parsed.netloc and parsed.netloc.endswith('atlassian.net'):
                value += ' (cloud)'

            config['confluence_server_url'] = value

        # remove space key, but track casing
        space_cfgs = [
            'confluence_space_key',
            'confluence_space_name',  # deprecated
        ]
        for space_cfg in space_cfgs:
            if space_cfg not in config:
                continue

            value = config[space_cfg]
            if value.startswith('~'):
                value = '(set; user)'
            elif value.isupper():
                value = '(set; upper)'
            elif value.islower():
                value = '(set; lower)'
            else:
                value = '(set; mixed)'
            config[space_cfg] = value

    print()
    print('Confluence builder report has been generated.')
    print('Please copy the following text for the GitHub issue:')
    print()
    logger.note('------------[ cut here ]------------')
    print('```')
    print('(system)')
    print(' platform:', single_line_version(platform.platform()))
    print('   python:', single_line_version(sys.version))
    print('   sphinx:', single_line_version(sphinx_version))
    print(' docutils:', single_line_version(docutils_version))
    print(' requests:', single_line_version(requests_version))
    print('  urllib3:', single_line_version(urllib3_version))
    print('  builder:', single_line_version(scb_version))

    print()
    print('(configuration)')
    if config:
        for k, v in OrderedDict(sorted(config.items())).items():
            pf = ' (env)' if k in new_env_keys else ''
            print(f'{k}: {v}{pf}')
    else:
        print('~default configuration~')

    if configuration_load_issue:
        print()
        print('(error loading configuration)')
        print(configuration_load_issue)

    if confluence_instance_info:
        print()
        print('(confluence instance)')
        print(confluence_instance_info.rstrip())

    print('```')
    logger.note('------------[ cut here ]------------')

    return rv


def single_line_version(value):
    """
    ensure a version value is represented in a single string

    When processing version entries, the output may attempt to print out
    multiple lines. This call helps join the multiple lines together.

    Args:
        value: the value to extract a version from

    Returns:
        the single-line version string
    """
    return ' '.join(str(value).split())
