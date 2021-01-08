# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from sphinxcontrib.confluencebuilder.config.notifications import deprecated
from sphinxcontrib.confluencebuilder.config.notifications import warnings
from sphinxcontrib.confluencebuilder.config.validation import ConfigurationValidation
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceConfigurationError
from requests.auth import AuthBase
import os

try:
    basestring
except NameError:
    basestring = str

def validate_configuration(builder):
    """
    validate a builder's configuration state

    This call will check if the provided builder's configuration has any issues
    with the existing configuration. For errors in the existing configuration,
    an `ConfluenceConfigurationError` exception will be thrown.

    In addition to errors, this call will also generate warning messages on
    other configuration issues such as deprecated configurations.

    Args:
        builder: the builder state to validate a configuration on
    """

    config = builder.config
    env = builder.app.env
    validator = ConfigurationValidation(builder)

    # ##################################################################

    # confluence_add_secnumbers
    validator.conf('confluence_add_secnumbers') \
             .bool()

    # ##################################################################

    # confluence_additional_mime_types
    validator.conf('confluence_additional_mime_types') \
             .strings(no_space=True)

    # ##################################################################

    # confluence_adv_aggressive_search
    validator.conf('confluence_adv_aggressive_search') \
             .bool()

    # ##################################################################

    # confluence_adv_hierarchy_child_macro
    validator.conf('confluence_adv_hierarchy_child_macro') \
             .bool()

    # ##################################################################

    # confluence_adv_trace_data
    validator.conf('confluence_adv_trace_data') \
             .bool()

    # ##################################################################

    # confluence_adv_writer_no_section_cap
    validator.conf('confluence_adv_writer_no_section_cap') \
             .bool()

    # ##################################################################

    # confluence_ask_password
    validator.conf('confluence_ask_password') \
             .bool()

    # ##################################################################

    # confluence_ask_user
    validator.conf('confluence_ask_user') \
             .bool()

    # ##################################################################

    # confluence_asset_force_standalone
    validator.conf('confluence_asset_force_standalone') \
             .bool()

    # ##################################################################

    validator.conf('confluence_ca_cert') \
             .file()

    # ##################################################################

    if config.confluence_client_cert is not None:
        client_cert = config.confluence_client_cert
        if isinstance(client_cert, tuple):
            cert_files = client_cert
        else:
            cert_files = (client_cert, None)

        if len(cert_files) != 2:
            raise ConfluenceConfigurationError(
"""confluence_client_cert is not a 2-tuple

The option 'confluence_client_cert' has been provided but there are too many
values. The client certificate can either be a file/path which defines a
certificate/key-pair, or a 2-tuple of the certificate and key.
""")

        for cert in cert_files:
            if cert and not os.path.isfile(os.path.join(env.srcdir, cert)):
                raise ConfluenceConfigurationError(
"""confluence_ca_cert missing certificate file

The option 'confluence_client_cert' has been provided to find a client
certificate file from a relative location, but the certificate could not be
found. Ensure the following file exists:

    %s

""" % cert)

    # ##################################################################

    # confluence_client_cert_pass
    validator.conf('confluence_client_cert_pass') \
             .string()

    # ##################################################################

    # confluence_default_alignment
    try:
        validator.conf('confluence_default_alignment') \
                 .matching('left', 'center', 'right')
    except ConfluenceConfigurationError as e:
        raise ConfluenceConfigurationError(
"""%s

The option 'confluence_default_alignment' has been provided to override the
default alignment for tables, figures, etc. Accepted values include 'left',
'center' and 'right'.
""" % str(e))

    # ##################################################################

    # confluence_disable_autogen_title
    validator.conf('confluence_disable_autogen_title') \
             .bool()

    # ##################################################################

    # confluence_disable_notifications
    validator.conf('confluence_disable_notifications') \
             .bool()

    # ##################################################################

    # confluence_disable_ssl_validation
    validator.conf('confluence_disable_ssl_validation') \
             .bool()

    # ##################################################################

    # confluence_file_suffix
    validator.conf('confluence_file_suffix') \
             .string()

    # ##################################################################

    # confluence_file_transform
    validator.conf('confluence_file_transform') \
             .callable_()

    # ##################################################################

    # confluence_footer_file
    try:
        validator.conf('confluence_footer_file') \
                 .string() \
                 .file()
    except ConfluenceConfigurationError as e:
        raise ConfluenceConfigurationError(
"""%s

The option 'confluence_footer_file' has been provided to find a footer template
file from a path relative to the documentation source. Ensure the value is set
to a proper file path.
""" % str(e))

    # ##################################################################

    # confluence_global_labels
    try:
        validator.conf('confluence_global_labels') \
                 .strings(no_space=True)
    except ConfluenceConfigurationError as e:
        raise ConfluenceConfigurationError(
"""%s

The option 'confluence_global_labels' can provide a collection to string values
to use as labels for published documentation. Each label value must be a string
that contains no spaces.
""" % str(e))

    # ##################################################################

    # confluence_header_file
    try:
        validator.conf('confluence_header_file') \
                 .string() \
                 .file()
    except ConfluenceConfigurationError as e:
        raise ConfluenceConfigurationError(
"""%s

The option 'confluence_header_file' has been provided to find a header template
file from a path relative to the documentation source. Ensure the value is set
to a proper file path.
""" % str(e))

    # ##################################################################

    # confluence_ignore_titlefix_on_index
    validator.conf('confluence_ignore_titlefix_on_index') \
             .bool()

    # ##################################################################

    # confluence_jira_servers
    if config.confluence_jira_servers is not None:
        issue = False
        jira_servers = config.confluence_jira_servers

        if not isinstance(jira_servers, dict):
            issue = True
        else:
            for name, info in jira_servers.items():
                if not isinstance(name, basestring):
                    issue = True
                    break

                if not isinstance(info, dict):
                    issue = True
                    break

                jira_id = info.get('id')
                jira_name = info.get('name')

                if not (isinstance(jira_id, basestring) and
                        isinstance(jira_name, basestring)):
                    issue = True
                    break

        if issue:
            raise ConfluenceConfigurationError(
"""confluence_jira_servers is not properly formed

JIRA server definitions should be a dictionary of string keys which contain
dictionaries with keys 'id' and 'name' which identify the JIRA instances.
""")

    # ##################################################################

    # confluence_lang_transform
    validator.conf('confluence_lang_transform') \
             .callable_()

    # ##################################################################

    # confluence_link_suffix
    validator.conf('confluence_link_suffix') \
             .string()

    # ##################################################################

    # confluence_link_transform
    validator.conf('confluence_link_transform') \
             .callable_()

    # ##################################################################

    # confluence_master_homepage
    validator.conf('confluence_master_homepage') \
             .bool()

    # ##################################################################

    # confluence_max_doc_depth
    try:
        validator.conf('confluence_max_doc_depth') \
                 .int_()
    except ConfluenceConfigurationError as e:
        raise ConfluenceConfigurationError(
"""%s

When limiting the document depth permitted for a building/publishing event, the
defined maximum document depth must be defined as a non-negative integer value.

If planning to use a depth of zero, it is recommended to use the
'singleconfluence' builder instead.
""" % str(e))

    # ##################################################################

    validator.conf('confluence_parent_page') \
             .string()

    # ##################################################################

    validator.conf('confluence_parent_page_id_check') \
             .int_(positive=True)

    # ##################################################################

    # confluence_page_hierarchy
    validator.conf('confluence_page_hierarchy') \
             .bool()

    # ##################################################################

    # confluence_prev_next_buttons_location
    try:
        validator.conf('confluence_prev_next_buttons_location') \
                 .matching('bottom', 'both', 'top')
    except ConfluenceConfigurationError as e:
        raise ConfluenceConfigurationError(
"""%s

The option 'confluence_prev_next_buttons_location' has been configured to enable
navigational buttons onto generated pages. Accepted values include 'bottom',
'both' and 'top'.
""" % str(e))

    # ##################################################################

    # confluence_proxy
    validator.conf('confluence_proxy') \
             .string()

    # ##################################################################

    # confluence_publish_allowlist
    # confluence_publish_denylist
    publish_list_options = [
        'confluence_publish_allowlist',
        'confluence_publish_denylist',
    ]

    for option in publish_list_options:
        value = getattr(config, option)
        if not value:
            continue

        # if provided via command line, treat as a list
        def conf_translate(value):
            if option in config['overrides'] and isinstance(value, basestring):
                value = value.split(',')
            return value
        value = conf_translate(value)

        try:
            validator.conf(option, conf_translate) \
                     .string_or_strings()

            if isinstance(value, basestring):
                validator.docnames_from_file()
            else:
                validator.docnames()
        except ConfluenceConfigurationError as e:
            raise ConfluenceConfigurationError(
"""%s

The value type permitted for this publish list option can either be a list of
document names or a string pointing to a file containing documents. Document
names are relative to the documentation's source directory.
""" % str(e))

    # ##################################################################

    # confluence_publish_dryrun
    validator.conf('confluence_publish_dryrun') \
             .bool()

    # ##################################################################

    # confluence_publish_onlynew
    validator.conf('confluence_publish_onlynew') \
             .bool()

    # ##################################################################

    # confluence_publish_postfix
    validator.conf('confluence_publish_postfix') \
             .string()

    # ##################################################################

    # confluence_publish_prefix
    validator.conf('confluence_publish_prefix') \
             .string()

    # ##################################################################

    # confluence_purge
    validator.conf('confluence_purge') \
             .bool()

    # ##################################################################

    # confluence_purge_from_master
    validator.conf('confluence_purge_from_master') \
             .bool()

    # ##################################################################

    # confluence_remove_title
    validator.conf('confluence_remove_title') \
             .bool()

    # ##################################################################

    # confluence_secnumber_suffix
    validator.conf('confluence_secnumber_suffix') \
             .string()

    # ##################################################################

    # confluence_server_auth
    if config.confluence_server_auth is not None:
        if not issubclass(type(config.confluence_server_auth), AuthBase):
            raise ConfluenceConfigurationError(
"""confluence_server_auth is not an implementation of requests.auth.AuthBase

Providing a custom authentication for Requests requires an implementation that
inherits 'requests.auth.AuthBase'. For more information, please consult the
following:

    requests -- Authentication
    https://requests.readthedocs.io/en/latest/user/authentication/
""")

    # ##################################################################

    # confluence_server_cookies
    validator.conf('confluence_server_cookies') \
             .dict_str_str()

    # ##################################################################

    # confluence_server_pass
    validator.conf('confluence_server_pass') \
             .string()

    # ##################################################################

    # confluence_server_url
    validator.conf('confluence_server_url') \
             .string()

    # ##################################################################

    # confluence_server_user
    validator.conf('confluence_server_user') \
             .string()

    # ##################################################################

    # confluence_space_name
    validator.conf('confluence_space_name') \
             .string()

    # ##################################################################

    # confluence_title_overrides
    validator.conf('confluence_title_overrides') \
             .dict_str_str()

    # ##################################################################

    # confluence_timeout
    try:
        validator.conf('confluence_timeout') \
                 .int_()
    except ConfluenceConfigurationError as e:
        raise ConfluenceConfigurationError(
"""%s

A configured timeout should be set to a value, in seconds, before any network
request to timeout after inactivity. This should be set to a positive integer
value (e.g. 2).
""" % str(e))

    # ##################################################################

    # confluence_watch
    validator.conf('confluence_watch') \
             .bool()

    # ##################################################################

    if config.confluence_publish:
        if not config.confluence_server_url:
            raise ConfluenceConfigurationError(
"""confluence server url not provided

While publishing has been configured using 'confluence_publish', the Confluence
server URL has not. Ensure 'confluence_server_url' has been set to target
Confluence instance to be published to.
""")

        if not config.confluence_space_name:
            raise ConfluenceConfigurationError(
"""confluence space name not provided

While publishing has been configured using 'confluence_publish', the Confluence
space name has not. Ensure 'confluence_space_name' has been set to space's name
which content should be published under.
""")

        if (config.confluence_ask_password and not config.confluence_server_user
                and not config.confluence_ask_user):
            raise ConfluenceConfigurationError(
"""confluence username not provided

A publishing password has been flagged with 'confluence_ask_password';
however, no username has been configured. Ensure 'confluence_server_user' is
properly set with the publisher's Confluence username or have
'confluence_ask_user' set to provide a username.
""")

        if config.confluence_server_pass:
            if not config.confluence_server_user:
                raise ConfluenceConfigurationError(
"""confluence username not provided

A publishing password has been configured with 'confluence_server_pass';
however, no username has been configured. Ensure 'confluence_server_user' is
properly set with the publisher's Confluence username.
""")

        if config.confluence_parent_page_id_check:
            if not config.confluence_parent_page:
                raise ConfluenceConfigurationError(
"""parent page (holder) name not set

When a parent page identifier check has been configured with the option
'confluence_parent_page_id_check', no parent page name has been provided with
the 'confluence_parent_page' option. Ensure the name of the parent page name
is provided as well.
""")

    # ##################################################################

    # inform users of aadditional configuration information
    deprecated(validator)
    warnings(validator)
