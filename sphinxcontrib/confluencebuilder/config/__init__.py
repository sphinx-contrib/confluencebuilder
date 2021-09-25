# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from sphinxcontrib.confluencebuilder import compat
from sphinxcontrib.confluencebuilder import util
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceConfigurationError
import sys

def handle_config_inited(app, config):
    """
    hook on when a configuration has been initialized

    Invoked when a configuration has been initialized by the Sphinx application.
    This event will be handled to process long term support for various options.

    Args:
        app: the application instance
        config: the configuration
    """

    def handle_legacy(new, orig):
        if getattr(config, new) is None and getattr(config, orig) is not None:
            config[new] = config[orig]

    # copy over deprecated configuration names to new names (if any)
    handle_legacy('confluence_master_homepage', 'confluence_root_homepage')
    handle_legacy('confluence_publish_allowlist', 'confluence_publish_subset')
    handle_legacy('confluence_purge_from_master', 'confluence_purge_from_root')

def process_ask_configs(config):
    """
    process any ask-based configurations for a user

    A series of asking configurations can be set in a configuration, such as
    asking for a password on a command line. This call will help process through
    the available questions and populate a final configuration state for the
    builder/publisher to use.

    Args:
        config: the configuration to check/update
    """

    if config.confluence_ask_user:
        print('(request to accept username from interactive session)')
        print(' Instance: ' + config.confluence_server_url)

        default_user = config.confluence_server_user
        u_str = ''
        if default_user:
            u_str = ' [{}]'.format(default_user)

        target_user = compat.input(' User{}: '.format(u_str)) or default_user
        if not target_user:
            raise ConfluenceConfigurationError('no user provided')

        config.confluence_server_user = target_user

    if config.confluence_ask_password:
        print('(request to accept password from interactive session)')
        if not config.confluence_ask_user:
            print(' Instance: ' + config.confluence_server_url)
            print('     User: ' + config.confluence_server_user)
        sys.stdout.write(' Password: ')
        sys.stdout.flush()
        config.confluence_server_pass = util.getpass2('')
        if not config.confluence_server_pass:
            raise ConfluenceConfigurationError('no password provided')
