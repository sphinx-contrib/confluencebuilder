# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2017-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from getpass import getpass
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceConfigurationError
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger
from sphinxcontrib.confluencebuilder.util import extract_strings_from_file
import os.path
import sys

try:
    basestring
except NameError:
    basestring = str

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

    # copy over deprecated configuration names to new names
    handle_legacy('confluence_publish_allowlist', 'confluence_publish_subset')

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

        target_user = input(' User{}: '.format(u_str)) or default_user
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
        config.confluence_server_pass = getpass('')
        if not config.confluence_server_pass:
            raise ConfluenceConfigurationError('no password provided')

class ConfluenceConfig:
    """
    confluence configuration validation utility class

    This class is used to perform a series of sanity checks on a user's
    configuration to ensure the building/publishing environment is using sane
    options.
    """
    _tracked_deprecated = []

    @staticmethod
    def validate(builder, log=True):
        """
        validate a provided configuration

        The provided configuration will be checked for sane configuration
        options. The method will return True for an expected good configuration,
        while returning False for a known bad configuration.
        """
        errState = False
        c = builder.config
        env = builder.app.env

        if c.confluence_default_alignment:
            if c.confluence_default_alignment not in (
                    'left', 'center', 'right'):
                errState = True
                if log:
                    ConfluenceLogger.error(
"""invalid default alignment

The option 'confluence_default_alignment' has been provided to override the
default alignment for tables, figures, etc. Accepted values include 'left',
'center' and 'right'.
""")

        if c.confluence_footer_file:
            if not os.path.isfile(os.path.join(env.srcdir,
                    c.confluence_footer_file)):
                errState = True
                if log:
                    ConfluenceLogger.error(
"""missing footer file

The option 'confluence_footer_file' has been provided to find a footer template
file from a relative location. Ensure the value is set to a proper file path.
""")

        if c.confluence_global_labels:
            if not (isinstance(c.confluence_global_labels, (tuple, list, set))
                    and all(isinstance(label, basestring)
                            for label in c.confluence_global_labels)):
                errState = True
                if log:
                    ConfluenceLogger.error(
"""'confluence_global_labels' should be a collection of strings""")
            else:
                for label in c.confluence_global_labels:
                    if ' ' in label:
                        errState = True
                        if log:
                            ConfluenceLogger.error(
"""label '%s' contains a space (not supported in confluence)""", label)

        if c.confluence_header_file:
            if not os.path.isfile(os.path.join(env.srcdir,
                    c.confluence_header_file)):
                errState = True
                if log:
                    ConfluenceLogger.error(
"""missing header file

The option 'confluence_header_file' has been provided to find a header template
file from a relative location. Ensure the value is set to a proper file path.
""")

        if c.confluence_max_doc_depth:
            depth = c.confluence_max_doc_depth
            if not isinstance(depth, int) or depth < 0:
                errState = True
                if log:
                    ConfluenceLogger.error(
"""maximum document depth is not an integer value

When limiting the document depth permitted for a building/publishing event, the
defined maximum document depth must be defined as an integer value (not a float,
string, etc.).
""")

        # ######################################################################

        publish_list_options = [
            'confluence_publish_allowlist',
            'confluence_publish_denylist',
        ]

        for option in publish_list_options:
            value = getattr(c, option)
            if value is None:
                continue

            # if provided via command line, treat as a list
            if option in c['overrides']:
                value = value.split(',')

            if not (isinstance(value, (tuple, list, set, basestring))):
                errState = True
                if log:
                    ConfluenceLogger.error(
"""invalid {} value

The value type permitted for this publish list option can either be a list of
document names or a string pointing to a file containing documents.
""".format(option))
            elif value:
                files = []
                if isinstance(value, basestring):
                    if os.path.isfile(value):
                        files = extract_strings_from_file(value)
                    else:
                        errState = True
                        if log:
                            ConfluenceLogger.error(
"""invalid {} filename

The filename provided in this option cannot be found on the system.
""".format(option))
                elif not (isinstance(value, (tuple, list, set)) and
                        all(isinstance(doc, basestring) for doc in value)):
                    errState = True
                    if log:
                        ConfluenceLogger.error(
"""invalid contents in {}

The values provided in this option should be a collection of strings.
""".format(option))
                else:
                    files = value

                for docname in files:
                    if not any(
                            os.path.isfile(
                                os.path.join(env.srcdir, docname + suffix))
                            for suffix in c.source_suffix):
                        errState = True
                        if log:
                            ConfluenceLogger.error(
"""missing document in {}

The document name {} provided in this option cannot be found on the system.
""".format(option, docname))

        # ######################################################################

        if c.confluence_publish:
            if not c.confluence_parent_page:
                if c.confluence_parent_page_id_check:
                    errState = True
                    if log:
                        ConfluenceLogger.error(
"""parent page (holder) name not set

When a parent page identifier check has been configured with the option
'confluence_parent_page_id_check', no parent page name has been provided with
the 'confluence_parent_page' option. Ensure the name of the parent page name
is provided as well.
""")

            prev_next_loc = c.confluence_prev_next_buttons_location
            if prev_next_loc and prev_next_loc not in ('bottom', 'both', 'top'):
                errState = True
                if log:
                    ConfluenceLogger.error(
"""prev-next button location invalid

When defining the previous/next button locations, only the following values are
permitted: bottom, top, both, or None.
""")

            if not c.confluence_server_url:
                errState = True
                if log:
                    ConfluenceLogger.error(
"""confluence server url not provided

While publishing has been configured using 'confluence_publish', the Confluence
server URL has not. Ensure 'confluence_server_url' has been set to target
Confluence instance to be published to.
""")

            if not c.confluence_space_name:
                errState = True
                if log:
                    ConfluenceLogger.error(
"""confluence space name not provided

While publishing has been configured using 'confluence_publish', the Confluence
space name has not. Ensure 'confluence_space_name' has been set to space's name
which content should be published under.
""")

            if not c.confluence_server_user and c.confluence_server_pass:
                errState = True
                if log:
                    ConfluenceLogger.error(
"""confluence username not provided

A publishing password has been configured with 'confluence_server_pass';
however, no username has been configured. Ensure 'confluence_server_user' is
properly set with the publisher's Confluence username.
""")

            if c.confluence_title_overrides is not None:
                if not isinstance(c.confluence_title_overrides, dict):
                    errState = True
                    if log:
                        ConfluenceLogger.error(
"""invalid type for confluence title overrides

While providing title overrides using 'confluence_title_overrides', the option
should be a dictionary of (str, str) entries.
""")

            if c.confluence_ca_cert:
                if not os.path.exists(c.confluence_ca_cert):
                    errState = True
                    if log:
                        ConfluenceLogger.error(
"""missing certificate authority

The option 'confluence_ca_cert' has been provided to find a certificate
authority file or path from a relative location. Ensure the value is set to a
proper file path.
""")
            if c.confluence_client_cert:
                if isinstance(c.confluence_client_cert, tuple):
                    cert_files = c.confluence_client_cert
                else:
                    cert_files = (c.confluence_client_cert, None)

                if len(cert_files) != 2:
                    errState = True
                    if log:
                        ConfluenceLogger.error(
"""invalid client certificate

The option 'confluence_client_cert' has been provided but there are too many
values. The client cert can either be a file/path to a certificate & key pair
or a tuple for the certificate and key in different files.
""")

                for cert_file in cert_files:
                    if cert_file and not os.path.isfile(cert_file):
                        errState = True
                        if log:
                            ConfluenceLogger.error(
"""missing certificate file

The option 'confluence_client_cert' has been provided to find a client
certificate file from a relative location, but the file %s was not found.
Ensure the value is set to a proper file path and the file exists.
""" % cert_file
                            )

                c.confluence_client_cert = cert_files

        # inform users of a deprecated configuration being used
        deprecated_configs = {
            'confluence_publish_subset':
                'use "confluence_publish_allowlist" instead',
        }

        cls = ConfluenceConfig
        for key, msg in deprecated_configs.items():
            if c[key] is not None and key not in cls._tracked_deprecated:
                cls._tracked_deprecated.append(key)
                ConfluenceLogger.warn('config "%s" deprecated; %s' % (key, msg))

        return not errState
