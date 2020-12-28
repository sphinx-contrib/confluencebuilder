# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger

"""
dictionary of deprecated configuration entries and associated message
"""
DEPRECATED_CONFIGS = {
    'confluence_publish_subset':
        'use "confluence_publish_allowlist" instead',
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
            ConfluenceLogger.warn('%s deprecated; %s' % (key, msg))

def warnings(validator):
    """
    inform users of any warnings related to a configuration state

    This call will check if the provided configuration has any configurations
    which may be a concern to a user. If a concern is observed in the
    configuration, a warning message will be provided to the user.

    Args:
        validator: the configuration validator
    """

    pass
