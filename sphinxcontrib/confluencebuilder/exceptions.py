# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2017-2022 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from sphinx.errors import ConfigError
from sphinx.errors import SphinxError


class ConfluenceError(SphinxError):
    category = 'sphinxcontrib.confluencebuilder error'


class ConfluenceAuthenticationFailedUrlError(ConfluenceError):
    def __init__(self):
        super(ConfluenceAuthenticationFailedUrlError, self).__init__('''
---
Unable to authenticate with Confluence

Unable to authenticate with the Confluence instance. Ensure the
configured username and password are correct. If credentials appear to
be correct, the user may need to be unlocked be re-logging in with above
browser or asking an administrator of the Confluence instance for help.
---
''')


class ConfluenceBadApiError(ConfluenceError):
    def __init__(self, code, details):
        super(ConfluenceBadApiError, self).__init__('''
---
Unsupported Confluence API call

An unsupported Confluence API call has been made. See the following
details for more information:

{details}
---
'''.format(details=details))
        self.status_code = code


class ConfluenceBadSpaceError(ConfluenceError):
    def __init__(self, space_key, uname, pw_set, extras):
        uname_value = uname if uname else '(empty)'
        pw_value = '<set>' if pw_set else '(empty)'
        super(ConfluenceBadSpaceError, self).__init__('''
---
Invalid Confluence URL detected

The configured Confluence space key does not appear to be valid:

    Space key: {space_key}
     Username: {uname}
     Password: {pw}

Ensure the instance is running and inspect that the configured
Confluence URL is valid. Also ensure authentication options are properly
set.

Note: Confluence space keys are case-sensitive.
{details}
---
'''.format(space_key=space_key, uname=uname_value, pw=pw_value, details=extras))


class ConfluenceBadServerUrlError(ConfluenceError):
    def __init__(self, server_url, ex):
        super(ConfluenceBadServerUrlError, self).__init__('''
---
Invalid Confluence URL detected

An issue has been detected when trying to communicate with the
configured Confluence instance. Ensure the instance is running and
inspect that the configured Confluence URL is valid:

   {url}


(details: {details})
---
'''.format(url=server_url, details=ex))


class ConfluenceCertificateError(ConfluenceError):
    def __init__(self, ex):
        super(ConfluenceCertificateError, self).__init__('''
---
SSL certificate issue

An SSL issue has been detected when trying to load the configured
certificates.

(details: {details})
---
'''.format(details=ex))


class ConfluenceConfigurationError(ConfluenceError, ConfigError):
    pass


class ConfluenceMissingPageIdError(ConfluenceError):
    def __init__(self, space_key, page_id):
        super(ConfluenceMissingPageIdError, self).__init__('''
---
Unable to find a requested page

A request to publish to a specific Confluence page identifier has failed
as the identifier could not be found.

      Space: {space_key}
    Page Id: {page_id}

---
'''.format(space_key=space_key, page_id=page_id))


class ConfluencePermissionError(ConfluenceError):
    def __init__(self, details):
        super(ConfluencePermissionError, self).__init__('''
---
Permission denied on Confluence ({desc})

The configured user does not have permission to perform an action on the
Confluence instance.
---
'''.format(desc=details))


class ConfluenceProxyPermissionError(ConfluenceError):
    def __init__(self):
        super(ConfluenceProxyPermissionError, self).__init__('''
---
Unable to authenticate with the proxy server

The proxy server being used is reporting that authentication is
required. Verify that the credentials used for the system's proxy
configuration are correct (this is unrelated to the configured
Confluence username/password configurations).
---
''')


class ConfluencePublishCheckError(ConfluenceError):
    pass


class ConfluencePublishAncestorError(ConfluencePublishCheckError):
    def __init__(self, page_name):
        super(ConfluencePublishAncestorError, self).__init__('''
---
Ancestor publish check failed for: {name}

A request has been made to publish a page as a nested child of itself.
This is most likely a result of an existing documentation set on a
Confluence instance where a publish attempt is trying to push new pages
into a parent page which has an ancestor with a matching name:

    {name} (original)
        |
         --> Configured Parent/Root
                     |
                      --> {name} (new update)

This extension will not reorder a configured base page from its
location. A user can either rename the page in their documentation to
prevent the page title conflict (either in the document itself or using
the `confluence_title_overrides` option), or rename/reorder the existing
page on the Confluence instance.

If the above does not appear to be related to the current use case,
please inform the maintainers of this extension.
---
'''.format(name=page_name))


class ConfluencePublishSelfAncestorError(ConfluencePublishCheckError):
    def __init__(self, page_name):
        super(ConfluencePublishSelfAncestorError, self).__init__('''
---
Ancestor (self) publish check failed for: {name}

A request has been made to publish a page as a child of itself. This is
most likely due to a configuration of `confluence_parent_page` with the
same value of the title page for the documentation's `root_doc`. If this
is the case and the configuration uses `confluence_page_hierarchy`,
there may be no need to set the `confluence_parent_page` option for this
documentation's configuration. However, if `confluence_page_hierarchy`
is not set, users will most likely want to use the
`confluence_publish_root` option instead.

If the above does not appear to be related to the current use case,
please inform the maintainers of this extension.
---
'''.format(name=page_name))


class ConfluenceRateLimited(ConfluenceError):
    def __init__(self, delay=None):
        super(ConfluenceRateLimited, self).__init__('''
---
Request has been rate limited

The configured Confluence instance is reporting that too many requests
are being made and has instructed to client to limit the amount of
requests to make at this time.
---
''')
        try:
            self.delay = int(delay)
        except (TypeError, ValueError):
            self.delay = None


class ConfluenceSeraphAuthenticationFailedUrlError(ConfluenceError):
    def __init__(self):
        super(ConfluenceSeraphAuthenticationFailedUrlError, self).__init__('''
---
Unable to authenticate with the Confluence instance (Seraph)

While this could be the configured username or password being incorrect,
this plugin as detected that the Atlassian Seraph instance has logged
this user out. This may be a result of a Confluence instance-related
issue. If this persisted, try contacting an administrator of the
Confluence instance for help.
---
''')


class ConfluenceSslError(ConfluenceError):
    def __init__(self, server_url, ex):
        super(ConfluenceSslError, self).__init__('''
---
SSL connection issue has been detected

An SSL issue has been detected when trying to communicate with the
configured Confluence instance. Ensure the instance is running and
inspect that the configured Confluence URL is valid:

   {url}

This can be common for internal/self-hosted Confluence instances which
may have been signed with an internal/corporate root authority. If the
environment is not setup in a way to verify self-signed certificates,
users may be interested in manually configure the `confluence_ca_cert`
option.

(details: {details})
---
'''.format(url=server_url, details=ex))


class ConfluenceTimeoutError(ConfluenceError):
    def __init__(self, server_url):
        super(ConfluenceTimeoutError, self).__init__('''
---
Connection has timed out

A request to communicate with the configured Confluence instance has
timed out. Ensure the instance is running and inspect that the
configured Confluence URL is valid:

   {url}

---
'''.format(url=server_url))


class ConfluenceUnreconciledPageError(ConfluenceError):
    def __init__(self, page_name, page_id, url, ex):
        super(ConfluenceUnreconciledPageError, self).__init__('''
---
Unable to update unreconciled page: {name} (id: {id})

Unable to update the target page due to the Confluence instance
reporting an unreconciled page. This is either due to a conflict with
another instance updating the page, Confluence having trouble updating a
large page request or possibly an old Confluence version
bug [1] (pre-v7.3.3).

A possible workaround for this is to manually browse the page using a
browser which could help force Confluence to reconcile the page. A link
to the page is a follows:

   {url}pages/viewpage.action?pageId={id}

If an attempt to re-publish fails after a page refresh attempt, a user
could also try manually deleting the page and retrying again. If the
page cannot be removed, assistance from a Confluence administrator may
be needed. See also the sphinx-contrib/confluencebuilder#528 [2]
discussion on GitHub.

[1]: https://jira.atlassian.com/browse/CONFSERVER-59196
[2]: https://github.com/sphinx-contrib/confluencebuilder/issues/528

(details: {details})
---
'''.format(name=page_name, id=page_id, url=url, details=ex))
