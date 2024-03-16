# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from sphinx.errors import SphinxError


class ConfluenceError(SphinxError):
    category = 'sphinxcontrib.confluencebuilder error'


class ConfluenceAuthenticationFailedUrlError(ConfluenceError):
    def __init__(self):
        super().__init__('''
---
Unable to authenticate with Confluence

Unable to authenticate with the Confluence instance. Ensure the
configured username and password are correct. If credentials appear to
be correct, the user may need to be unlocked be re-logging in with above
browser or asking an administrator of the Confluence instance for help.

(code: 401)
---
''')


class ConfluenceBadApiError(ConfluenceError):
    def __init__(self, code, details):
        super().__init__(f'''
---
Unsupported Confluence API call

An unsupported Confluence API call has been made. See the following
details for more information:

{details}
---
''')
        self.status_code = code


class ConfluenceBadServerUrlError(ConfluenceError):
    def __init__(self, server_url, details):
        super().__init__(f'''
---
Invalid Confluence URL detected

An issue has been detected when trying to communicate with the
configured Confluence instance. Ensure the instance is running and
inspect that the configured Confluence URL is valid:

   {server_url}

(details: {details})
---
''')


class ConfluenceCertificateError(ConfluenceError):
    def __init__(self, details):
        super().__init__(f'''
---
SSL certificate issue

An SSL issue has been detected when trying to load the configured
certificates.

(details: {details})
---
''')


class ConfluenceMissingPageIdError(ConfluenceError):
    def __init__(self, space_key, page_id):
        super().__init__(f'''
---
Unable to find a requested page

A request to publish to a specific Confluence page identifier has failed
as the identifier could not be found.

      Space: {space_key}
    Page Id: {page_id}
---
''')


class ConfluencePermissionError(ConfluenceError):
    def __init__(self, details):
        super().__init__(f'''
---
Permission denied on Confluence ({details})

The configured user does not have permission to perform an action on the
Confluence instance. If the user should have access and this request is
using a personal access token, ensure the token is not expired/revoked.

(code: 403)
---
''')


class ConfluenceProxyPermissionError(ConfluenceError):
    def __init__(self):
        super().__init__('''
---
Unable to authenticate with the proxy server

The proxy server being used is reporting that authentication is
required. Verify that the credentials used for the system's proxy
configuration are correct (this is unrelated to the configured
Confluence username/password configurations).

(code: 407)
---
''')


class ConfluencePublishCheckError(ConfluenceError):
    pass


class ConfluencePublishAncestorError(ConfluencePublishCheckError):
    def __init__(self, page_name):
        super().__init__(f'''
---
Ancestor publish check failed for: {page_name}

A request has been made to publish a page as a nested child of itself.
This is most likely a result of an existing documentation set on a
Confluence instance where a publish attempt is trying to push new pages
into a parent page which has an ancestor with a matching name:

    {page_name} (original)
        |
         --> Configured Parent/Root
                     |
                      --> {page_name} (new update)

This extension will not reorder a configured base page from its
location. A user can either rename the page in their documentation to
prevent the page title conflict (either in the document itself or using
the `confluence_title_overrides` option), or rename/reorder the existing
page on the Confluence instance.

If the above does not appear to be related to the current use case,
please inform the maintainers of this extension.
---
''')


class ConfluencePublishSelfAncestorError(ConfluencePublishCheckError):
    def __init__(self, page_name):
        super().__init__(f'''
---
Ancestor (self) publish check failed for: {page_name}

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
''')


class ConfluenceRateLimitedError(ConfluenceError):
    def __init__(self):
        super().__init__('''
---
Request has been rate limited

The configured Confluence instance is reporting that too many requests
are being made and has instructed to client to limit the amount of
requests to make at this time.

(code: 429)
---
''')


class ConfluenceSeraphAuthenticationFailedUrlError(ConfluenceError):
    def __init__(self):
        super().__init__('''
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
    def __init__(self, server_url, details):
        super().__init__(f'''
---
SSL connection issue has been detected

An SSL issue has been detected when trying to communicate with the
configured Confluence instance. Ensure the instance is running and
inspect that the configured Confluence URL is valid:

   {server_url}

This can be common for internal/self-hosted Confluence instances which
may have been signed with an internal/corporate root authority. If the
environment is not setup in a way to verify self-signed certificates,
users may be interested in manually configure the `confluence_ca_cert`
option.

(details: {details})
---
''')


class ConfluenceTimeoutError(ConfluenceError):
    def __init__(self, server_url):
        super().__init__(f'''
---
Connection has timed out

A request to communicate with the configured Confluence instance has
timed out. Ensure the instance is running and inspect that the
configured Confluence URL is valid:

   {server_url}
---
''')


class ConfluenceUnexpectedCdataError(ConfluenceError):
    def __init__(self):
        super().__init__('''
---
Unexpected Confluence XML stream CDATA parsing error

Confluence has reported an error processing a document which contains
CDATA data (e.g. a code block using `<![CDATA[data]]>`). This is
unexpected since the data should be properly formed. There is a high
chance that this is occurring on a Confluence instance which introduced
some processing logic that incorrectly breaks the parsing of CDATA EOF
strings (as of Confluence 8.x). This should be addressed in Confluence
8.3.0 (or newer) release [1].

To workaround this issue for the configured Confluence instance, a user
can enable the `confluence_adv_quirk_cdata` inside their `conf.py`
configuration file. For example:

    confluence_adv_quirk_cdata = True

If enabling this option does not resolve the publication issue, then
this error message does not apply. Feel free to report this issue noting
the exception message above this message.

[1]: https://jira.atlassian.com/browse/CONFSERVER-82849
---
''')


class ConfluenceUnknownInstanceError(ConfluenceError):
    def __init__(self, server_url, space_key, uname, pw_set, token_set):
        uname_value = uname if uname else '(empty)'
        pw_value = '(set)' if pw_set else '(empty)'
        token_value = '(set)' if token_set else '(empty)'
        super().__init__(f'''
---
Unknown Confluence URL or invalid/restricted space detected

An issue has been detected when trying to communicate with the
configured Confluence instance. Ensure the instance is running and
inspect that the configured Confluence URL is valid:

    {server_url}

If the instance is valid, ensure the configured space key and approriate
authentication permissions are configured.

                   Space key: {space_key}
                    Username: {uname_value}
       Password or API Token: {pw_value}
 Personal Access Token (PAT): {token_value}
---
''')


class ConfluenceUnreconciledPageError(ConfluenceError):
    def __init__(self, page_name, page_id, url, details):
        super().__init__(f'''
---
Unable to update unreconciled page: {page_name} (id: {page_id})

Unable to update the target page due to the Confluence instance
reporting an unreconciled page. This is either due to a conflict with
another instance updating the page, Confluence having trouble updating a
large page request or possibly an old Confluence version
bug [1] (pre-v7.3.3).

A possible workaround for this is to manually browse the page using a
browser which could help force Confluence to reconcile the page. A link
to the page is a follows:

   {url}pages/viewpage.action?pageId={page_id}

If an attempt to re-publish fails after a page refresh attempt, a user
could also try manually deleting the page and retrying again. If the
page cannot be removed, assistance from a Confluence administrator may
be needed. See also the sphinx-contrib/confluencebuilder#528 [2]
discussion on GitHub.

[1]: https://jira.atlassian.com/browse/CONFSERVER-59196
[2]: https://github.com/sphinx-contrib/confluencebuilder/issues/528

(details: {details})
---
''')
