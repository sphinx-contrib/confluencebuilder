# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020-2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger as logger
import mimetypes

# dictionary of deprecated configuration entries and associated message
DEPRECATED_CONFIGS = {
    'confluence_adv_hierarchy_child_macro':
        'to be removed in a future version',
    'confluence_adv_trace_data':
        'to be removed in a future version',
    'confluence_adv_writer_no_section_cap':
        'to be removed in a future version',
    'confluence_master_homepage':
        'use "confluence_root_homepage" instead',
    'confluence_publish_subset':
        'use "confluence_publish_allowlist" instead',
    'confluence_purge_from_master':
        'use "confluence_purge_from_root" instead',
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
            logger.warn('%s deprecated; %s' % (key, msg))

    # promote singleconfluence over confluence_max_doc_depth=0
    if config.confluence_max_doc_depth == 0:
        logger.warn('confluence_max_doc_depth with a value of zero '
            "is deprecated; use the 'singleconfluence' builder instead")
    elif config.confluence_max_doc_depth:
        logger.warn('confluence_max_doc_depth is deprecated and will '
            "be removed; consider using the 'singleconfluence' builder instead")


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

    # check if any user defined mime types are unknown
    if config.confluence_additional_mime_types is not None:
        for mime_type in config.confluence_additional_mime_types:
            if not mimetypes.guess_extension(mime_type):
                logger.warn('confluence_additional_mime_types '
                    'defines an unknown mime type: ' + mime_type)

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
