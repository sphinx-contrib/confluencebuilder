# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2017-2020 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from .logger import ConfluenceLogger
import os.path

try:
    basestring
except NameError:
    basestring = str

class ConfluenceConfig:
    """
    confluence configuration validation utility class

    This class is used to perform a series of sanity checks on a user's
    configuration to ensure the building/publishing environment is using sane
    options.
    """

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
            if not c.confluence_default_alignment in (
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

        if c.confluence_publish_subset:
            if not (isinstance(c.confluence_publish_subset, (tuple, list, set))
                    and all(isinstance(docname, basestring)
                            for docname in c.confluence_publish_subset)):
                errState = True
                if log:
                    ConfluenceLogger.error(
"""'confluence_publish_subset' should be a collection of strings""")
            else:
                for docname in c.confluence_publish_subset:
                    if not any(os.path.isfile(os.path.join(env.srcdir,
                                                           docname + suffix))
                               for suffix in c.source_suffix):
                        errState = True
                        if log:
                            ConfluenceLogger.error(
"""Document '%s' in 'confluence_publish_subset' not found""", docname)

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

        return not errState
