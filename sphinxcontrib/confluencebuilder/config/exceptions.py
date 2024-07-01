# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from sphinx.errors import ConfigError
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceError


class ConfluenceConfigError(ConfluenceError, ConfigError):
    pass


class ConfluenceApiModeConfigError(ConfluenceConfigError):
    def __init__(self, modes):
        super().__init__(f'''\
invalid api version provided in confluence_api_mode

The following API modes are supported:

 - {modes}
''')


class ConfluenceCleanupSearchModeConfigError(ConfluenceConfigError):
    def __init__(self, msg):
        super().__init__(f'''\
{msg}

The option 'confluence_cleanup_search_mode' has been provided to override the
default search method for page descendants. Accepted values include 'direct',
'search' and '<mode>-aggressive'.
''')


class ConfluenceClientCertBadTupleConfigError(ConfluenceConfigError):
    def __init__(self):
        super().__init__('''\
confluence_client_cert is not a 2-tuple

The option 'confluence_client_cert' has been provided but there are too many
values. The client certificate can either be a file/path which defines a
certificate/key-pair, or a 2-tuple of the certificate and key.
''')


class ConfluenceClientCertMissingCertConfigError(ConfluenceConfigError):
    def __init__(self, file):
        super().__init__(f'''\
confluence_client_cert missing certificate file

The option 'confluence_client_cert' has been provided to find a client
certificate file from a relative location, but the certificate could not be
found. Ensure the following file exists:

    {file}
''')


class ConfluenceDefaultAlignmentConfigError(ConfluenceConfigError):
    def __init__(self, msg):
        super().__init__(f'''\
{msg}

The option 'confluence_default_alignment' has been provided to override the
default alignment for tables, figures, etc. Accepted values include 'left',
'center' and 'right'.
''')


class ConfluenceDomainIndicesConfigError(ConfluenceConfigError):
    def __init__(self):
        super().__init__('''\
confluence_domain_indices is not a boolean or collection of strings

The option 'confluence_domain_indices' has been provided to indicate that
domain indices should be generated. This value can either be set to `True` or
set to a list of domains (strings) to be included.
''')


class ConfluenceEditorConfigError(ConfluenceConfigError):
    def __init__(self, editors):
        super().__init__(f'''\
invalid editor provided in confluence_editor

The following editors are supported:

 - {editors}
''')


class ConfluenceFooterFileConfigError(ConfluenceConfigError):
    def __init__(self, msg):
        super().__init__(f'''\
{msg}

The option 'confluence_footer_file' has been provided to find a footer template
file from a path relative to the documentation source. Ensure the value is set
to a proper file path.
''')


class ConfluenceGlobalLabelsConfigError(ConfluenceConfigError):
    def __init__(self, msg):
        super().__init__(f'''\
{msg}

The option 'confluence_global_labels' can provide a collection to string values
to use as labels for published documentation. Each label value must be a string
that contains no spaces.
''')


class ConfluenceHeaderFileConfigError(ConfluenceConfigError):
    def __init__(self, msg):
        super().__init__(f'''\
{msg}

The option 'confluence_header_file' has been provided to find a header template
file from a path relative to the documentation source. Ensure the value is set
to a proper file path.
''')


class ConfluenceJiraServersConfigError(ConfluenceConfigError):
    def __init__(self):
        super().__init__('''\
confluence_jira_servers is not properly formed

Jira server definitions should be a dictionary of string keys which contain
dictionaries with keys 'id' and 'name' which identify the Jira instances.
''')


class ConfluenceLatexMacroInvalidConfigError(ConfluenceConfigError):
    def __init__(self):
        super().__init__('''\
confluence_latex_macro is not a string or dictionary of strings

The option 'confluence_latex_macro' has been provided to indicate that a
LaTeX content should be rendered with a LaTeX macro supported on a Confluence
instance. This value can either be set to a string of the macro to be used or
set to a dictionary of key-value strings for advanced options.
''')


class ConfluenceLatexMacroMissingKeysConfigError(ConfluenceConfigError):
    def __init__(self, keys):
        super().__init__(f'''\
missing keys in confluence_latex_macro

The following keys are required:

 - {keys}
''')


class ConfluencePageGenerationNoticeConfigError(ConfluenceConfigError):
    def __init__(self):
        super().__init__('''\
confluence_page_generation_notice is not a boolean or a string

The option 'confluence_page_generation_notice' has been provided to
indicate that a notice should be added at the top of each page about
pages being generated. This value can either be set to `True` or
configured with the message to inform users.
''')


class ConfluencePageSearchModeConfigError(ConfluenceConfigError):
    def __init__(self, msg):
        super().__init__(f'''\
{msg}

The option 'confluence_page_search_mode' has been provided to override the
default method for querying page content. Accepted values include 'default',
'content' and 'search'.
''')


class ConfluenceParentPageConfigError(ConfluenceConfigError):
    def __init__(self):
        super().__init__('''\
confluence_parent_page is not a string or a positive integer
''')


class ConfluencePermitRawHtmlConfigError(ConfluenceConfigError):
    def __init__(self):
        super().__init__('''\
confluence_permit_raw_html is not a boolean or a string

The option 'confluence_permit_raw_html' has been provided to indicate that
raw HTML should be published. This value can either be set to `True` or
configured to the name of a supported macro identifier.
''')


class ConfluencePrevNextButtonsLocationConfigError(ConfluenceConfigError):
    def __init__(self, msg):
        super().__init__(f'''\
{msg}

The option 'confluence_prev_next_buttons_location' has been configured to enable
navigational buttons onto generated pages. Accepted values include 'bottom',
'both' and 'top'.
''')


class ConfluencePublishCleanupConflictConfigError(ConfluenceConfigError):
    def __init__(self):
        super().__init__('''\
conflicting cleanup configurations

When configuring for cleanup of legacy pages, a user can configure for either
'confluence_cleanup_archive' or 'confluence_publish_root'; however, both
cannot be configured at the same time.
''')


class ConfluencePublishConflictPublishPointConfigError(ConfluenceConfigError):
    def __init__(self):
        super().__init__('''\
conflicting publish point configurations

When configuring for a publishing container, a user can configure for either
'confluence_parent_page' or 'confluence_publish_root'; however, both cannot be
configured at the same time.
''')


class ConfluencePublishDebugConfigError(ConfluenceConfigError):
    def __init__(self, msg):
        super().__init__(f'''\
{msg}

The option 'confluence_publish_debug' has been configured to enable publish
debugging. Accepted values include:

 - all
 - deprecated
 - headers
 - headers-and-data
 - urllib3
''')


class ConfluencePublishListConfigError(ConfluenceConfigError):
    def __init__(self, msg):
        super().__init__(f'''\
{msg}

The value type permitted for this publish list option can either be a list of
document names or a string pointing to a file containing documents. Document
names are relative to the documentation's source directory.
''')


class ConfluencePublishMissingParentPageConfigError(ConfluenceConfigError):
    def __init__(self):
        super().__init__('''\
parent page (holder) name not set

When a parent page identifier check has been configured with the option
'confluence_parent_page_id_check', no parent page name has been provided with
the 'confluence_parent_page' option. Ensure the name of the parent page name
is provided as well.
''')


class ConfluencePublishMissingServerUrlConfigError(ConfluenceConfigError):
    def __init__(self):
        super().__init__('''\
confluence server url not provided

While publishing has been configured using 'confluence_publish', the Confluence
server URL has not. Ensure 'confluence_server_url' has been set to target
Confluence instance to be published to.
''')


class ConfluencePublishMissingSpaceKeyConfigError(ConfluenceConfigError):
    def __init__(self):
        super().__init__('''\
confluence space key not provided

While publishing has been configured using 'confluence_publish', the Confluence
space key has not. Ensure 'confluence_space_key' has been set to space's key
which content should be published under.
''')


class ConfluencePublishMissingUsernameAskConfigError(ConfluenceConfigError):
    def __init__(self):
        super().__init__('''\
confluence username not provided

A publishing password has been flagged with 'confluence_ask_password';
however, no username has been configured. Ensure 'confluence_server_user' is
properly set with the publisher's Confluence username or have
'confluence_ask_user' set to provide a username.
''')


class ConfluencePublishMissingUsernameAuthConfigError(ConfluenceConfigError):
    def __init__(self):
        super().__init__('''\
confluence username not provided

A publishing password has been configured with 'confluence_api_token';
however, no username has been configured. Ensure 'confluence_server_user' is
properly set with the publisher's Confluence username.
''')


class ConfluencePublishMissingUsernamePassConfigError(ConfluenceConfigError):
    def __init__(self):
        super().__init__('''\
confluence username not provided

A publishing password has been configured with 'confluence_server_pass';
however, no username has been configured. Ensure 'confluence_server_user' is
properly set with the publisher's Confluence username.
''')


class ConfluenceServerAuthConfigError(ConfluenceConfigError):
    def __init__(self):
        super().__init__('''\
confluence_server_auth is not an implementation of requests.auth.AuthBase

Providing a custom authentication for Requests requires an implementation that
inherits 'requests.auth.AuthBase'. For more information, please see the
following:

    requests -- Authentication
    https://requests.readthedocs.io/en/latest/user/authentication/
''')


class ConfluenceSourcelinkRequiredConfigError(ConfluenceConfigError):
    def __init__(self, required):
        super().__init__(f'''\
required option missing in confluence_sourcelink

The following options are required for the provided template type:

 - {required}
''')


class ConfluenceSourcelinkReservedConfigError(ConfluenceConfigError):
    def __init__(self, reserved):
        super().__init__(f'''\
reserved option set in confluence_sourcelink

The following options are reserved with confluence_sourcelink
and cannot be set:

 - {reserved}
''')


class ConfluenceSourcelinkTypeConfigError(ConfluenceConfigError):
    def __init__(self, supported_types):
        super().__init__(f'''\
unsupported type provided in confluence_sourcelink

The following types are supported:

 - {supported_types}
''')


class ConfluenceSourcelinkUrlConfigError(ConfluenceConfigError):
    def __init__(self):
        super().__init__('''\
url option is not set in confluence_sourcelink

If a template type is not being configured for a source link,
the `url` field must be configured.
''')


class ConfluenceTimeoutConfigError(ConfluenceConfigError):
    def __init__(self, msg):
        super().__init__(f'''\
{msg}

A configured timeout should be set to a duration, in seconds, before any network
request to timeout after inactivity. This should be set to a positive integer
value (e.g. 2).
''')
