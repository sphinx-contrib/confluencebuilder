configuration
=============

The following is an example of simple configuration for Confluence generation
and publishing:

.. code-block:: python

   extensions = ['sphinxcontrib.confluencebuilder']
   confluence_publish = True
   confluence_space_name = 'TEST'
   confluence_parent_page = 'Documentation'
   confluence_server_url = 'https://intranet-wiki.example.com/'
   confluence_server_user = 'username'
   confluence_server_pass = 'password'

All Atlassian Confluence Builder configurations are prefixed with
``confluence_``. View the entire list of configuration options below.

.. contents:: :local:

essential configuration
-----------------------

confluence_publish
~~~~~~~~~~~~~~~~~~

A boolean that decides whether or not to allow publishing. This option must be
explicitly set to ``True`` if one wishes to publish content. By default, the
value is set to ``False``.

.. code-block:: python

   confluence_publish = True

--------------------------------------------------------------------------------

confluence_server_pass
~~~~~~~~~~~~~~~~~~~~~~

The password value used to authenticate with the Confluence instance. If using
Confluence Cloud, it is recommended to use an API token for the configured
username value (see `API tokens`_):

.. code-block:: python

   confluence_server_pass = 'vsUsrSZ6Z4kmrQMapSXBYkJh'

If `API tokens`_ are not being used, the plain password for the configured
username value should be used:

.. code-block:: python

   confluence_server_pass = 'myawesomepassword'

.. caution::

   It is never recommended to store an API token or raw password into a
   committed/shared repository holding documentation. A documentation's
   configuration can modified various ways with Python to pull an
   authentication token for a publishing event (reading from a local file,
   acquiring a password from ``getpass``, etc.). If desired, this extension
   provides a method for prompting for a password (see
   |confluence_ask_password|_).

--------------------------------------------------------------------------------

confluence_server_url
~~~~~~~~~~~~~~~~~~~~~

The URL for Confluence. The URL should be prefixed with ``https://`` or
``http://`` (depending on the URL target). The target API folder should not be
included in the URL (i.e. excluding ``rest/api/``). For a Confluence Cloud
instance, an example URL configuration is as follows:

.. code-block:: python

   confluence_server_url = 'https://example.atlassian.net/wiki/'

For a Confluence Server instance, an example URL configuration, if the
instance's REST API is ``https://intranet-wiki.example.com/rest/api/``, should
be as follows:

.. code-block:: python

   confluence_server_url = 'https://intranet-wiki.example.com/'

--------------------------------------------------------------------------------

confluence_server_user
~~~~~~~~~~~~~~~~~~~~~~

The username value used to authenticate with the Confluence instance. If using
Confluence Cloud, this value will most likely be the account's E-mail address.
If using Confluence instance, this value will most likely be the username value.

.. code-block:: python

   confluence_server_user = 'myawesomeuser@example.com'
       (or)
   confluence_server_user = 'myawesomeuser'

--------------------------------------------------------------------------------

.. |confluence_space_name| replace:: ``confluence_space_name``
.. _confluence_space_name:

confluence_space_name
~~~~~~~~~~~~~~~~~~~~~

Key of the space in Confluence to be used to publish generated documents to.

.. code-block:: python

   confluence_space_name = 'MyAwesomeSpace'

Note that the space name can be **case-sensitive** in most (if not all) versions
of Confluence.

--------------------------------------------------------------------------------

generic configuration
---------------------

.. |confluence_add_secnumbers| replace:: ``confluence_add_secnumbers``
.. _confluence_add_secnumbers:

confluence_add_secnumbers
~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionadded:: 1.2

Add section numbers to page and section titles if ``doctree`` uses the
``:numbered:`` option. By default, this is enabled:

.. code-block:: python

    confluence_add_secnumbers = True

See also |confluence_publish_prefix|_.

--------------------------------------------------------------------------------

confluence_default_alignment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionadded:: 1.3

Explicitly set which alignment type to use when a default alignment value is
detected. As of Sphinx 2.0+, the default alignment is set to ``center``. Legacy
versions of Sphinx had a default alignment of ``left``. By default, this
extension will use a Sphinx-defined default alignment unless explicitly set by
this configuration value. Accepted values are ``left``, ``center`` or ``right``.

.. code-block:: python

    confluence_default_alignment = 'left'

--------------------------------------------------------------------------------

.. |confluence_header_file| replace:: ``confluence_header_file``
.. _confluence_header_file:

confluence_header_file
~~~~~~~~~~~~~~~~~~~~~~

The name of the file to use header data. If provided, the contents found inside
the header file will be added to the start of all generated documents. The file
path provided should be relative to the build environment's source directory.
For example:

.. code-block:: python

   confluence_header_file = 'assets/header.tpl'

See also |confluence_footer_file|_.

--------------------------------------------------------------------------------

.. |confluence_footer_file| replace:: ``confluence_footer_file``
.. _confluence_footer_file:

confluence_footer_file
~~~~~~~~~~~~~~~~~~~~~~

The name of the file to use footer data. If provided, the contents found inside
the footer file will be added at the end of all generated documents. The file
path provided should be relative to the build environment's source directory.
For example:

.. code-block:: python

   confluence_footer_file = 'assets/footer.tpl'

See also |confluence_header_file|_.

--------------------------------------------------------------------------------

confluence_max_doc_depth
~~~~~~~~~~~~~~~~~~~~~~~~

An integer value, if provided, to indicate the maximum depth permitted for a
nested child page before its contents is inlined with a parent. The root of all
pages is typically the configured master_doc_. The root page is considered to be
at a depth of zero. By defining a value of ``0``, all child pages of the root
document will be merged into a single document. By default, the maximum document
depth is disabled with a value of ``None``.

.. code-block:: python

   confluence_max_doc_depth = 2

--------------------------------------------------------------------------------

confluence_page_hierarchy
~~~~~~~~~~~~~~~~~~~~~~~~~

A boolean value to whether or not nest pages in a hierarchical ordered. The root
of all pages is typically the configured master_doc_. If a master_doc_ instance
contains a toctree_, listed documents will become child pages of the
master_doc_. This cycle continues for child pages with their own toctree_
markups. By default, the hierarchy mode is disabled with a value of ``False``.

.. code-block:: python

   confluence_page_hierarchy = False

Note that even if hierarchy mode is enabled, the configured master_doc_ page and
other published pages that are not defined in the complete toctree_, these
documents will still be published based off the configured (or unconfigured)
|confluence_parent_page|_ setting.

--------------------------------------------------------------------------------

confluence_prev_next_buttons_location
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionadded:: 1.2

A string value to where to include previous/next buttons (if any) based on the
detected order of documents to be included in processing. Values accepted are
either ``bottom``, ``both``, ``top`` or ``None``. By default, no previous/next
links are generated with a value of ``None``.

.. code-block:: python

   confluence_prev_next_buttons_location = 'top'

--------------------------------------------------------------------------------

.. |confluence_secnumber_suffix| replace:: ``confluence_secnumber_suffix``
.. _confluence_secnumber_suffix:

confluence_secnumber_suffix
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionadded:: 1.2

The suffix to put after section numbers, before section name.

.. code-block:: python

    confluence_secnumber_suffix = '. '

See also |confluence_add_secnumbers|_.

--------------------------------------------------------------------------------

publishing configuration
------------------------

.. |confluence_ask_password| replace:: ``confluence_ask_password``
.. _confluence_ask_password:

confluence_ask_password
~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

   User's running Cygwin/MinGW may need to invoke with ``winpty`` to allow this
   feature to work.

Provides an override for an interactive shell to request publishing documents
using an API key or password provided from the shell environment. While a
password is typically defined in the option ``confluence_server_pass`` (either
directly set/fetched from the project's ``config.py`` or passed via a command
line argument ``-D confluence_server_pass=password``), select environments may
wish to provide a way to provide an authentication token without needing to
modify documentation sources or having a visible password value in the
interactive session requesting the publish event. By default, this
option is disabled with a value of ``False``.

.. code-block:: python

   confluence_ask_password = False

A user can request for a password prompt by invoking build event by passing the
define through the command line:

.. code-block:: none

   sphinx-build [options] -D confluence_ask_password=1 <srcdir> <outdir>

Note that some shell sessions may not be able to pull the password value
properly from the user. For example, Cygwin/MinGW may not be able to accept a
password unless invoked with ``winpty``.

--------------------------------------------------------------------------------

confluence_ask_user
~~~~~~~~~~~~~~~~~~~

.. versionadded:: 1.2

Provides an override for an interactive shell to request publishing documents
using a user provided from the shell environment. While a
user is typically defined in the option ``confluence_server_user``, select
environments may wish to provide a way to provide a user without needing to
modify documentation sources.
By default, this option is disabled with a value of ``False``.

.. code-block:: python

   confluence_ask_user = False

--------------------------------------------------------------------------------

confluence_disable_autogen_title
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A boolean value to explicitly disable the automatic generation of titles for
documents which do not have a title set. When this extension processes a set of
documents to publish, a document needs a title value to know which Confluence
page to create/update. In the event where a title value cannot be extracted from
a document, a title value will be automatically generated for the document. For
automatically generated titles, the value will always be prefixed with
``autogen-``. For users who wish to ignore pages which have no title, this
option can be set to ``True``. By default, this option is set to ``False``.

.. code-block:: python

   confluence_disable_autogen_title = True

--------------------------------------------------------------------------------

confluence_disable_notifications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A boolean value which explicitly disable any page update notifications (i.e.
treats page updates from a publish request as minor updates). By default,
notifications are enabled with a value of ``False``.

.. code-block:: python

   confluence_disable_notifications = True

--------------------------------------------------------------------------------

.. |confluence_master_homepage| replace:: ``confluence_master_homepage``
.. _confluence_master_homepage:

confluence_master_homepage
~~~~~~~~~~~~~~~~~~~~~~~~~~

A boolean value to whether or not force the configured space's homepage to be
set to the page defined by the Sphinx configuration's master_doc_. By default,
the master_doc_ configuration is ignored with a value of ``False``.

.. code-block:: python

   confluence_master_homepage = False

--------------------------------------------------------------------------------

.. |confluence_parent_page| replace:: ``confluence_parent_page``
.. _confluence_parent_page:

confluence_parent_page
~~~~~~~~~~~~~~~~~~~~~~

The root page found inside the configured space (|confluence_space_name|_)
where published pages will be a descendant of. The parent page value is used
to match with the title of an existing page. If this option is not provided,
pages will be published to the root of the configured space. If the parent page
cannot be found, the publish attempt will stop with an error message. For
example, the following will publish documentation under the ``MyAwesomeDocs``
page:

.. code-block:: python

   confluence_parent_page = 'MyAwesomeDocs'

If a parent page is not set, consider using the |confluence_master_homepage|_
option as well. Note that the page's name can be case-sensitive in most
(if not all) versions of Confluence.

--------------------------------------------------------------------------------

.. |confluence_publish_postfix| replace:: ``confluence_publish_postfix``
.. _confluence_publish_postfix:

confluence_publish_postfix
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionadded:: 1.2

If set, the postfix value is added to the title of all published documents. In
Confluence, page names need to be unique for a space. A postfix can be set to
either:

* Add a unique naming schema to generated/published documents in a space which
  has manually created pages; or,
* Allow multiple published sets of documentation, each with their own postfix
  value.

An example publish postfix is as follows:

.. code-block:: python

   confluence_publish_postfix = '-postfix'

By default, no postfix is used. See also |confluence_publish_prefix|_.

--------------------------------------------------------------------------------

.. |confluence_publish_prefix| replace:: ``confluence_publish_prefix``
.. _confluence_publish_prefix:

confluence_publish_prefix
~~~~~~~~~~~~~~~~~~~~~~~~~

If set, the prefix value is added to the title of all published documents. In
Confluence, page names need to be unique for a space. A prefix can be set to
either:

* Add a unique naming schema to generated/published documents in a space which
  has manually created pages; or,
* Allow multiple published sets of documentation, each with their own prefix
  value.

An example publish prefix is as follows:

.. code-block:: python

   confluence_publish_prefix = 'prefix-'

By default, no prefix is used. See also |confluence_publish_postfix|_.

--------------------------------------------------------------------------------

.. |confluence_purge| replace:: ``confluence_purge``
.. _confluence_purge:

confluence_purge
~~~~~~~~~~~~~~~~

.. warning::

   Publishing individual/subset of documents with this option may lead to
   unexpected results.

A boolean value to whether or not purge legacy pages detected in a space or
parent page. By default, this value is set to ``False`` to indicate that no
pages will be removed. If this configuration is set to ``True``, detected pages
in Confluence that do not match the set of published documents will be
automatically removed. If the option |confluence_parent_page|_ is set, only
pages which are a descendant of the configured parent page can be removed;
otherwise, all pages in the configured space could be removed.

.. code-block:: python

   confluence_purge = False

While this capability is useful for updating a series of pages, it may lead to
unexpected results when attempting to publish a single-page update. The purge
operation will remove all pages that are not publish in the request. For
example, if an original request publishes ten documents and purges excess
documents, a following publish attempt with only one of the documents will purge
the other nine pages.

--------------------------------------------------------------------------------

confluence_purge_from_master
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A boolean value to which indicates that any purging attempt should be done from
the root of a published master_doc_ page (instead of a configured parent page;
i.e. |confluence_parent_page|_). In specific publishing scenarios, a user may
wish to publish multiple documentation sets based off a single parent/container
page. To prevent any purging between multiple documentation sets, this option
can be set to ``True``. When generating legacy pages to be removed, this
extension will only attempt to populate legacy pages based off the children of
the master_doc_ page. This option still requires |confluence_purge|_ to be set
to ``True`` before taking effect.

.. code-block:: python

   confluence_purge_from_master = False

--------------------------------------------------------------------------------

.. _confluence_timeout:

confluence_timeout
~~~~~~~~~~~~~~~~~~

Force a timeout (in seconds) for network interaction. The timeout used by this
extension is not explicitly configured (i.e. managed by Requests_ and other
implementations). By default, assume that any network interaction will not
timeout. Since the target Confluence instance is most likely to be found on an
external server, is it recommended to explicitly configure a timeout value based
on the environment being used. For example, to configure a timeout of ten
seconds, the following can be used:

.. code-block:: python

   confluence_timeout = 10

--------------------------------------------------------------------------------

advanced publishing configuration
---------------------------------

confluence_asset_override
~~~~~~~~~~~~~~~~~~~~~~~~~

Provides an override for asset publishing to allow a user publishing to either
force re-publishing assets or disable asset publishing. This extension will
attempt to publish assets (images, downloads, etc.) to pages via Confluence's
attachment feature. Attachments are assigned a comment value with a hash value
of a published asset. If another publishing event occurs, the hash value is
checked before attempting to re-publish an asset. In unique scenarios, are use
may wish to override this ability. By configuring this option to ``True``, this
extension will always publish asset files (whether or not an attachment with a
matching hash exists). By configuring this option to ``False``, no assets will
be published by this extension. By default, this automatic asset publishing
occurs with a value of ``None``.

.. code-block:: python

   confluence_asset_override = None

--------------------------------------------------------------------------------

confluence_ca_cert
~~~~~~~~~~~~~~~~~~

Provide a CA certificate to use for server certificate authentication. The value
for this option can either be a file of a certificate or a path pointing to an
OpenSSL-prepared directory. If configured to use REST API (default), refer to
the `Requests SSL Cert Verification`_  documentation (``verify``) for
information. If server verification is explicitly disabled (see
|confluence_disable_ssl_validation|_), this option is ignored. By default, this
option is ignored with a value of ``None``.

.. code-block:: python

   confluence_ca_cert = 'ca.crt'

--------------------------------------------------------------------------------

.. |confluence_client_cert| replace:: ``confluence_client_cert``
.. _confluence_client_cert:

confluence_client_cert
~~~~~~~~~~~~~~~~~~~~~~

Provide a client certificate to use for two-way TLS/SSL authentication. The
value for this option can either be a file (containing a certificate and private
key) or as a tuple where both certificate and private keys are explicitly
provided. If a private key is protected with a passphrase, a user publishing a
documentation set will be prompted for a password (see also
|confluence_client_cert_pass|_). By default, this option is ignored with a value
of ``None``.

.. code-block:: python

   confluence_client_cert = 'cert_and_key.pem'
   # or
   confluence_client_cert = ('client.cert', 'client.key')

--------------------------------------------------------------------------------

.. |confluence_client_cert_pass| replace:: ``confluence_client_cert_pass``
.. _confluence_client_cert_pass:

confluence_client_cert_pass
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provide a passphrase for |confluence_client_cert|_. This prevents a user from
being prompted to enter a passphrase for a private key when publishing. If a
configured private key is not protected by a passphrase, this value will be
ignored. By default, this option is ignored with a value of ``None``.

.. code-block:: python

   confluence_client_cert_pass = 'passphrase'

--------------------------------------------------------------------------------

.. |confluence_disable_ssl_validation| replace::
   ``confluence_disable_ssl_validation``
.. _confluence_disable_ssl_validation:

confluence_disable_ssl_validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

   It is not recommended to use this option.

A boolean value to explicitly disable verification of server SSL certificates
when making a publish request. By default, this option is set to ``False``.

.. code-block:: python

   confluence_disable_ssl_validation = False

--------------------------------------------------------------------------------

confluence_parent_page_id_check
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The page identifier check for |confluence_parent_page|_. By providing an
identifier of the parent page, both the parent page's name and identifier must
match before this extension will publish any content to a Confluence instance.
This serves as a sanity-check configuration for the cautious.

.. code-block:: python

   confluence_parent_page_id_check = 1

--------------------------------------------------------------------------------

confluence_proxy
~~~~~~~~~~~~~~~~

REST calls use the Requests_ library which will use system-defined proxy
configuration; however, a user can override the system-defined proxy by
providing a proxy server using this configuration.

.. code-block:: python

   confluence_proxy = 'myawesomeproxy:8080'

--------------------------------------------------------------------------------

.. _confluence_publish_subset:

confluence_publish_subset
~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    If ``confluence_publish_subset`` is configured, this option disables
    |confluence_purge|_.

Provides the ability for a publisher to explicitly list a subset of documents to
be published to a Confluence instance. When a user invokes sphinx-build_, a user
has the ability to process all documents (by default) or specifying individual
filenames which use the provide files and detected dependencies. If the
Sphinx-detected set of documents to process contain undesired documents to
publish, ``confluence_publish_subset`` can be used to override this. Defined
document names should be a relative file path without the file extension. For
example:

.. code-block:: python

   confluence_publish_subset = ['index', 'foo/bar']

A user can force a publishing subset through the command line:

.. code-block:: none

   sphinx-build [options] -D confluence_publish_subset=index,foo/bar \
       <srcdir> <outdir> index.rst foo/bar.rst

By default, this option is ignored with a value of ``[]``. See also
:ref:`manage publishing a document subset<tip_manage_publish_subset>`.

--------------------------------------------------------------------------------

confluence_server_auth
~~~~~~~~~~~~~~~~~~~~~~

An authentication handler which can be directly provided to a REST API request.
REST calls in this extension use the Requests_ library, which provide various
methods for a client to perform authentication. While this extension already
provided simple authentication support (via ``confluence_server_user`` and
``confluence_server_pass``), a publisher may need to configure an advanced
authentication handler to support a target Confluence instance.

Note that this extension does not define custom authentication handlers. This
configuration is a passthrough option only. For more details on various ways to
use authentication handlers, please consult `Requests -- Authentication`_. By
default, no custom authentication handler is provided to generated REST API
requests (if any).

.. code-block:: python

   from requests_oauthlib import OAuth1

   ...

   confluence_server_auth = OAuth1(client_key,
       client_secret=client_secret,
       resource_owner_key=resource_owner_key,
       resource_owner_secret=resource_owner_secret)

--------------------------------------------------------------------------------

confluence_server_cookies
~~~~~~~~~~~~~~~~~~~~~~~~~

A dictionary value which allows a user to pass key-value cookie information for
authentication purposes. This is useful for users who need to authenticate with
a single sign-on (SSO) provider to access a target Confluence instance. By
default, no cookies are set with a value of ``None``.

.. code-block:: python

   confluence_server_cookies = {
       'SESSION_ID': '<session id string>',
       'U_ID': '<username>'
   }

--------------------------------------------------------------------------------

advanced processing configuration
---------------------------------

.. |confluence_file_suffix| replace:: ``confluence_file_suffix``
.. _confluence_file_suffix:

confluence_file_suffix
~~~~~~~~~~~~~~~~~~~~~~

The file name suffix to use for all generated files. By default, all generated
files will use the extension ``.conf`` (see |confluence_file_transform|_).

.. code-block:: python

   confluence_file_suffix = '.conf'

--------------------------------------------------------------------------------

.. |confluence_file_transform| replace:: ``confluence_file_transform``
.. _confluence_file_transform:

confluence_file_transform
~~~~~~~~~~~~~~~~~~~~~~~~~

A function to override the translation of a document name to a filename. The
provided function is used to perform translations for both Sphinx's
get_outdated_docs_ and write_doc_ methods. The default translation will be the
combination of "``docname`` + |confluence_file_suffix|_".

--------------------------------------------------------------------------------

.. _confluence_jira_servers:

confluence_jira_servers
~~~~~~~~~~~~~~~~~~~~~~~

.. versionadded:: 1.2

Provides a dictionary of named JIRA servers to reference when using the ``jira``
or ``jira_issue`` directives. In a typical Confluence environment which is
linked with a JIRA instance, users do not need to take advantage of this
configuration -- Confluence should automatically be able to link to respectively
JIRA issues or map JIRA query languages with a configured JIRA instance. In
select cases where an instance has more than one JIRA instance attached, a user
may need to explicitly reference a JIRA instance to properly render a JIRA
macro. JIRA-related directives have the ability to reference JIRA instances,
with a combination of a UUID and name; for example:

.. code-block:: rst

    .. jira_issue:: TEST-151
        :server-id: d005bcc2-ca4e-4065-8ce8-49ff5ac5857d
        :server-name: MyAwesomeJiraServer

It may be tedious for some projects to add this information in each document. As
an alternative, a configuration can define JIRA instance information inside a
configuration option as follows:

.. code-block:: python

    confluence_jira_servers = {
        'server-1': {
            'id': '<UUID of JIRA Instance>',
            'name': '<Name of JIRA Instance>'
        }
    }

With the above option defined in a project's configuration, the following can be
used instance inside a document:

.. code-block:: rst

    .. jira_issue:: TEST-151
        :server: server-1

--------------------------------------------------------------------------------

confluence_lang_transform
~~~~~~~~~~~~~~~~~~~~~~~~~

A function to override the translation of literal block-based directive
language values to Confluence-support code block macro language values. The
default translation accepts `Pygments documented language types`_ to
`Confluence-supported syntax highlight languages`_.

.. code-block:: python

   def my_language_translation(lang):
       return 'default'

   confluence_lang_transform = my_language_translation

--------------------------------------------------------------------------------

.. |confluence_link_suffix| replace:: ``confluence_link_suffix``
.. _confluence_link_suffix:

confluence_link_suffix
~~~~~~~~~~~~~~~~~~~~~~

The suffix name to use for generated links to files. By default, all generated
links will use the value defined by |confluence_file_suffix|_ (see
|confluence_link_transform|_).

.. code-block:: python

   confluence_link_suffix = '.conf'

--------------------------------------------------------------------------------

.. |confluence_link_transform| replace:: ``confluence_link_transform``
.. _confluence_link_transform:

confluence_link_transform
~~~~~~~~~~~~~~~~~~~~~~~~~

A function to override the translation of a document name to a (partial) URI.
The provided function is used to perform translations for both Sphinx's
get_relative_uri_ method. The default translation will be the combination of
"``docname`` + |confluence_link_suffix|_".

--------------------------------------------------------------------------------

confluence_remove_title
~~~~~~~~~~~~~~~~~~~~~~~

A boolean value to whether or not automatically remove the title section from
all published pages. In Confluence, page names are already presented at the top.
With this option enabled, this reduces having two leading headers with the
document's title. In some cases, a user may wish to not remove titles when
custom prefixes or other custom modifications are in play. By default, this
option is enabled with a value of ``True``.

confluence_single_page
~~~~~~~~~~~~~~~~~~~~~~

A boolean value to whether or not generate a single confluence page. Normally,
each .rst file becomes its own confluence page. With this option enabled, every
.rst file is consolidated into a single page. By default, this option is enabled
with a value of ``False``.

.. code-block:: python

   confluence_remove_title = True


.. references ------------------------------------------------------------------

.. _API tokens: https://confluence.atlassian.com/cloud/api-tokens-938839638.html
.. _Confluence-supported syntax highlight languages: https://confluence.atlassian.com/confcloud/code-block-macro-724765175.html
.. _Pygments documented language types: http://pygments.org/docs/lexers/
.. _Requests SSL Cert Verification: http://docs.python-requests.org/en/master/user/advanced/#ssl-cert-verification
.. _Requests: https://pypi.python.org/pypi/requests
.. _Requests -- Authentication: https://2.python-requests.org/projects/3/user/authentication/
.. _TLS/SSL wrapper for socket object: https://docs.python.org/3/library/ssl.html#ssl.create_default_context
.. _api_tokens: https://confluence.atlassian.com/cloud/api-tokens-938839638.html
.. _get_outdated_docs: https://www.sphinx-doc.org/en/master/extdev/builderapi.html#sphinx.builders.Builder.get_outdated_docs
.. _get_relative_uri: https://www.sphinx-doc.org/en/master/extdev/builderapi.html#sphinx.builders.Builder.get_relative_uri
.. _master_doc: https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-master_doc
.. _toctree: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-toctree
.. _write_doc: https://www.sphinx-doc.org/en/master/extdev/builderapi.html#sphinx.builders.Builder.write_doc
.. _sphinx-build: https://www.sphinx-doc.org/en/master/man/sphinx-build.html
