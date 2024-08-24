# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger as logger
from sphinxcontrib.confluencebuilder.std.confluence import EDITORS
from sphinxcontrib.confluencebuilder.std.confluence import SUPPORTED_CODE_BLOCK_THEMES
import mimetypes

# dictionary of deprecated configuration entries and associated message
DEPRECATED_CONFIGS = {
    'confluence_adv_aggressive_search':
        'use "confluence_cleanup_search_mode" instead',
    'confluence_adv_permit_raw_html':
        'use "confluence_permit_raw_html" instead',
    'confluence_lang_transform':
        'use "confluence_lang_overrides" instead',
    'confluence_adv_trace_data':
        'to be removed in a future version',
    'confluence_adv_writer_no_section_cap':
        'to be removed in a future version',
    'confluence_master_homepage':
        'use "confluence_root_homepage" instead',
    'confluence_max_doc_depth':
        'option does nothing',
    'confluence_parent_page_id_check':
        '"confluence_parent_page" now accepts a page id',
    'confluence_publish_disable_api_prefix':
        'use "confluence_publish_override_api_prefix" instead',
    'confluence_publish_subset':
        'use "confluence_publish_allowlist" instead',
    'confluence_purge_from_master':
        'use "confluence_cleanup_from_root" instead',
    'confluence_purge_from_root':
        'use "confluence_cleanup_from_root" instead',
    'confluence_space_name':
        'use "confluence_space_key" instead',
}


def deprecated(validator):
    """
    inform users of deprecated configurations

    This call will check if the provided configuration has any configurations
    which have been flagged as deprecated. If a deprecated configuration is
    detected, a warning message will be provided to the user.

    Args:
        validator: the configuration validator
    """

    config = validator.config

    # inform users of a deprecated configuration being used
    for key, msg in DEPRECATED_CONFIGS.items():
        if config[key] is not None:
            logger.warn(f'{key} deprecated; {msg}', subtype='deprecated')


def warnings(validator):
    """
    inform users of any warnings related to a configuration state

    This call will check if the provided configuration has any configurations
    which may be a concern to a user. If a concern is observed in the
    configuration, a warning message will be provided to the user.

    Args:
        validator: the configuration validator
    """

    config = validator.config

    # check that only a single authentication key is configured
    auth_keys = [
        'confluence_api_token',
        'confluence_publish_token',
        'confluence_server_pass',
    ]

    auth_keys_used = []
    for option in auth_keys:
        value = getattr(config, option)
        if value:
            auth_keys_used.append(option)

    if len(auth_keys_used) > 1:
        logger.warn('multiple authentication options configured; only one of '
            'these options should be set: ' + ', '.join(auth_keys_used))

    # check if any user defined mime types are unknown
    if config.confluence_additional_mime_types is not None:
        for mime_type in config.confluence_additional_mime_types:
            if not mimetypes.guess_extension(mime_type):
                logger.warn('confluence_additional_mime_types '
                    'defines an unknown mime type: ' + mime_type)

    # confluence_code_block_theme assigned an unsupported theme
    if config.confluence_code_block_theme is not None:
        theme = config.confluence_code_block_theme.lower()
        if theme not in SUPPORTED_CODE_BLOCK_THEMES:
            logger.warn('confluence_code_block_theme '
                        'defines an unknown theme: ' + theme)

    # warn when ssl validation is disabled
    if config.confluence_disable_ssl_validation:
        logger.warn('confluence_disable_ssl_validation is set; '
            'consider using confluence_ca_cert instead')

    # confluence_file_suffix "cannot" end with a dot
    if (config.confluence_file_suffix and
            config.confluence_file_suffix.endswith('.')):
        logger.warn(
            'confluence_file_suffix ends with a period; '
            'a default value will be applied instead')

    # confluence_editor assigned to an editor that is not supported
    if config.confluence_editor and config.confluence_editor not in EDITORS:
        logger.warn('confluence_editor configured with an unsupported editor')

    # confluence_publish_debug should be using the new string values
    if isinstance(config.confluence_publish_debug, bool):
        logger.warn('confluence_publish_debug using deprecated bool value')

    # check if password/token are wrapped in quotes; these values may be
    # passed in through arguments/etc. (i.e. not defined in `conf.py`); there
    # could be a risk of a shell/CI passed value which a user accidentally
    # quotes a password/token value -- provide a warning if we believe that
    # has been detected
    quote_wrap_check = [
        'confluence_api_token',
        'confluence_publish_token',
        'confluence_server_pass',
    ]

    quote_values = [
        '"',
        "'",
    ]

    for option in quote_wrap_check:
        value = getattr(config, option)
        if not value:
            continue

        for quote_value in quote_values:
            if value.startswith(quote_value) and value.endswith(quote_value):
                logger.warn(f'{option} is wrapped in quotes')
