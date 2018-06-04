# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2017-2018 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from sphinx.errors import ConfigError
from sphinx.errors import SphinxError

class ConfluenceError(SphinxError):
    category = 'sphinxcontrib.confluencebuilder error'

class ConfluenceAuthenticationFailedUrlError(ConfluenceError):
    def __init__(self):
        SphinxError.__init__(self,
            """---\n"""
            """Unable to authenticate with the Confluence server.\n"""
            """\n"""
            """Ensure your username and password are correct. If your """
            """username and password is correct, you may need to unlock """
            """your Confluence account be re-logging in with your browser """
            """or asking your Confluence administrator for help.\n"""
            """---\n"""
        )

class ConfluenceBadApiError(ConfluenceError):
    def __init__(self, details):
        SphinxError.__init__(self,
            """---\n"""
            """An unsupported Confluence API call has been made.\n"""
            """\n"""
            """%s""" % details +
            """\n---\n"""
        )

class ConfluenceBadSpaceError(ConfluenceError):
    def __init__(self, space_name):
        SphinxError.__init__(self,
            """---\n"""
            """The configured Confluence space does not appear to be """
            """valid: %s\n""" % space_name +
            """---\n"""
        )

class ConfluenceBadServerUrlError(ConfluenceError):
    def __init__(self, server_url, ex):
        SphinxError.__init__(self,
            """---\n"""
            """An issue has been detected when trying to communicate with """
            """Confluence server.\n"""
            """\n"""
            """Ensure the server is running or your Confluence server URL """
            """is valid:\n\n"""
            """    %s\n""" % server_url +
            """\n(details: %s""" % ex +
            """)\n"""
            """---\n"""
        )

class ConfluenceConfigurationError(ConfluenceError, ConfigError):
    pass

class ConfluenceLegacyError(ConfluenceError):
    def __init__(self):
        SphinxError.__init__(self,
            """---\n"""
            """Your Confluence server is too old. Need at least Confluence """
            """v4.0 or higher.\n"""
            """---\n"""
        )

class ConfluencePermissionError(ConfluenceError):
    def __init__(self, details):
        SphinxError.__init__(self,
            """---\n"""
            """Do not have permission for this action on the Confluence """
            """server.\n\n"""
            """%s\n""" % details +
            """---\n"""
        )

class ConfluenceProxyPermissionError(ConfluenceError):
    def __init__(self):
        SphinxError.__init__(self,
            """---\n"""
            """Unable to authenticate with the proxy server.\n"""
            """\n"""
            """Ensure your proxy's username and password are correct.\n"""
            """---\n"""
        )

class ConfluenceRemoteApiDisabledError(ConfluenceError):
    def __init__(self, server_url):
        SphinxError.__init__(self,
            """---\n"""
            """Confluence Remote API appears to be disabled.\n"""
            """\n"""
            """First, ensure the server is running or your Confluence """
            """server URL is valid:\n\n"""
            """    %s\n""" % server_url +
            """\n"""
            """If you are sure your server URL is correct, you will need """
            """to ask your Confluence administrator to enable """
            """'Remote API (XML-RPC & SOAP)'.\n"""
            """---\n"""
        )

class ConfluenceSeraphAuthenticationFailedUrlError(ConfluenceError):
    def __init__(self):
        SphinxError.__init__(self,
            """---\n"""
            """Unable to authenticate with the Confluence server.\n"""
            """\n"""
            """While this could be your username or password being """
            """incorrect, this plugin as detected that the Atlassian """
            """Seraph instance has logged you out. This could be a """
            """result of a server-related issue. If this persisted, """
            """try contacting your Confluence administrator for help.\n"""
            """---\n"""
        )

class ConfluenceTimeoutError(ConfluenceError):
    def __init__(self, server_url):
        SphinxError.__init__(self,
            """---\n"""
            """A request to communicate with the Confluence server has """
            """timed out.\n"""
            """\n"""
            """Ensure the server is running or your Confluence server URL """
            """is valid:\n\n"""
            """    %s\n""" % server_url +
            """---\n"""
        )

class ConfluenceSSLError(ConfluenceError):
    def __init__(self, server_url, ex):
        SphinxError.__init__(self,
            """---\n"""
            """An SSL issue has been detected when trying to communicate """
            """with Confluence server.\n"""
            """\n"""
            """Ensure the server is running or your Confluence server URL """
            """is valid:\n\n"""
            """    %s\n""" % server_url +
            """\n(details: %s""" % ex +
            """)\n"""
            """---\n"""
        )

class ConfluenceCertificateError(ConfluenceError):
    def __init__(self, ex):
        SphinxError.__init__(self,
            """---\n"""
            """An SSL issue has been detected when trying to load the """
            """the certificates provided.\n"""
            """details: %s\n""" % ex +
            """---\n"""
        )