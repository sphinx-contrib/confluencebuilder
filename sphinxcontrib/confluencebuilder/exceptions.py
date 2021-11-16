# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2017-2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from sphinx.errors import ConfigError
from sphinx.errors import SphinxError


class ConfluenceError(SphinxError):
    category = 'sphinxcontrib.confluencebuilder error'


class ConfluenceAuthenticationFailedUrlError(ConfluenceError):
    def __init__(self):
        super(ConfluenceAuthenticationFailedUrlError, self).__init__(
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
    def __init__(self, code, details):
        super(ConfluenceBadApiError, self).__init__(
            """---\n"""
            """An unsupported Confluence API call has been made.\n"""
            """\n"""
            """%s""" % details +
            """\n---\n"""
        )
        self.status_code = code


class ConfluenceBadSpaceError(ConfluenceError):
    def __init__(self, space_key, uname, pw_set, extras):
        uname_value = uname if uname else '(empty)'
        pw_value = '<set>' if pw_set else '(empty)'
        super(ConfluenceBadSpaceError, self).__init__(
            """---\n"""
            """The configured Confluence space key does not appear to be """
            """valid:\n\n"""
            """    Space key: {}\n"""
            """     Username: {}\n"""
            """     Password: {}\n"""
            """\n"""
            """Ensure the server is running or your Confluence URL is valid. """
            """Also ensure your authentication options are properly set.\n"""
            """\n"""
            """Note: Confluence space keys are case-sensitive.\n"""
            """{}"""
            """---\n""".format(space_key, uname_value, pw_value, extras)
        )


class ConfluenceBadServerUrlError(ConfluenceError):
    def __init__(self, server_url, ex):
        super(ConfluenceBadServerUrlError, self).__init__(
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


class ConfluenceCertificateError(ConfluenceError):
    def __init__(self, ex):
        super(ConfluenceCertificateError, self).__init__(
            """---\n"""
            """An SSL issue has been detected when trying to load the """
            """the certificates provided.\n"""
            """details: %s\n""" % ex +
            """---\n"""
        )


class ConfluenceConfigurationError(ConfluenceError, ConfigError):
    pass


class ConfluenceMissingPageIdError(ConfluenceError):
    def __init__(self, space_key, page_id):
        super(ConfluenceMissingPageIdError, self).__init__(
            """---\n"""
            """A request to publish to a specific Confluence page identifier """
            """has failed as the identifier could not be found.\n\n"""
            """    Space: {}\n"""
            """  Page Id: {}\n"""
            """\n"""
            """---\n""".format(space_key, page_id)
        )


class ConfluencePermissionError(ConfluenceError):
    def __init__(self, details):
        super(ConfluencePermissionError, self).__init__(
            """---\n"""
            """Do not have permission for this action on the Confluence """
            """server.\n\n"""
            """%s\n""" % details +
            """---\n"""
        )


class ConfluenceProxyPermissionError(ConfluenceError):
    def __init__(self):
        super(ConfluenceProxyPermissionError, self).__init__(
            """---\n"""
            """Unable to authenticate with the proxy server.\n"""
            """\n"""
            """Ensure your proxy's username and password are correct.\n"""
            """---\n"""
        )


class ConfluencePublishCheckError(ConfluenceError):
    pass


class ConfluencePublishSelfAncestorError(ConfluencePublishCheckError):
    def __init__(self, page_name):
        super(ConfluencePublishSelfAncestorError, self).__init__('''
---
Ancestor publish check failed for: {name}

A request has been made to publish a page as a child of itself. This is most
likely due to a configuration of `confluence_parent_page` with the same value of
the title page for the documentation's `root_doc`. If this is the case and the
configuration uses `confluence_page_hierarchy`, there may be no need to set the
`confluence_parent_page` option for this documentation's configuration. However,
if `confluence_page_hierarchy` is not set, users will most likely want to use
the `confluence_publish_root` option instead.

If the above does not appear to be related to the current use case, please
inform the maintainers of this extension.
---
'''.format(name=page_name))


class ConfluenceSeraphAuthenticationFailedUrlError(ConfluenceError):
    def __init__(self):
        super(ConfluenceSeraphAuthenticationFailedUrlError, self).__init__(
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


class ConfluenceSslError(ConfluenceError):
    def __init__(self, server_url, ex):
        super(ConfluenceSslError, self).__init__(
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


class ConfluenceTimeoutError(ConfluenceError):
    def __init__(self, server_url):
        super(ConfluenceTimeoutError, self).__init__(
            """---\n"""
            """A request to communicate with the Confluence server has """
            """timed out.\n"""
            """\n"""
            """Ensure the server is running or your Confluence server URL """
            """is valid:\n\n"""
            """    %s\n""" % server_url +
            """---\n"""
        )


class ConfluenceUnreconciledPageError(ConfluenceError):
    def __init__(self, page_name, page_id, url, ex):
        super(ConfluenceUnreconciledPageError, self).__init__('''
---
Unable to update unreconciled page: {name} (id: {id})

Unable to update the target page due to the Confluence instance reporting an
unreconciled page. This is either due to a conflict with another instance
updating the page, Confluence having trouble updating a large page request or
possibly an old Confluence version bug [1] (pre-v7.3.3).

A possible workaround for this is to manually browse the page using a browser
which could help force Confluence to reconcile the page. A link to the page is
a follows:

   {url}pages/viewpage.action?pageId={id}

If an attempt to re-publish fails after a page refresh attempt, a user could
also try manually deleting the page and retrying again. If the page cannot be
removed, assistance from a Confluence administrator may be needed. See also the
sphinx-contrib/confluencebuilder#528 [2] discussion on GitHub.

[1]: https://jira.atlassian.com/browse/CONFSERVER-59196
[2]: https://github.com/sphinx-contrib/confluencebuilder/issues/528

(details: {ex})
---
'''.format(name=page_name, id=page_id, url=url, ex=ex))
