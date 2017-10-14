# -*- coding: utf-8 -*-
"""
    sphinxcontrib.confluencebuilder.compat
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2017 by the contributors (see AUTHORS file).
    :license: BSD, see LICENSE.txt for details.
"""

from .logger import ConfluenceLogger
import os.path

class ConfluenceConfig:
    """
    confluence configuration validation utility class

    This class is used to perform a series of sanity checks on a user's
    configuration to ensure the building/publishing environment is using sane
    options.
    """

    @staticmethod
    def validate(c, log=True):
        """
        validate a provided configuration

        The provided configuration will be checked for sane configuration
        options. The method will return True for an expected good configuration,
        while returning False for a known bad configuration.
        """
        errState = False

        if c.confluence_footer_file:
            if not os.path.isfile(c.confluence_footer_file):
                errState = True
                if log:
                    ConfluenceLogger.error(
"""missing footer file

The option 'confluence_footer_file' has been provided to find a footer template
file from a relative location. Ensure the value is set to a proper file path.
""")

        if c.confluence_header_file:
            if not os.path.isfile(c.confluence_header_file):
                errState = True
                if log:
                    ConfluenceLogger.error(
"""missing header file

The option 'confluence_header_file' has been provided to find a header template
file from a relative location. Ensure the value is set to a proper file path.
""")

        if c.confluence_publish:
            if c.confluence_disable_rest and c.confluence_disable_xmlrpc:
                errState = True
                if log:
                    ConfluenceLogger.error(
"""all publish protocols explicitly disabled

While publishing has been configured using 'confluence_publish', both REST and
XML-RPC have been explicitly disabled in the user configuration. This extension
cannot publish documents without a single publish protocol enabled.
""")

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

        return not errState
