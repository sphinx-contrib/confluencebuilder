configuration
=============

The following is an example of simple configuration for Confluence generation
and publishing:

.. code-block:: python

    extensions = ['sphinxcontrib.confluencebuilder']
    confluence_publish = True
    confluence_space_name = 'TEST'
    confluence_parent_page = 'Documentation'
    confluence_server_url = 'https://intranet-wiki.example.com'
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

confluence_server_pass
~~~~~~~~~~~~~~~~~~~~~~

The password value used to authenticate with the Confluence instance. If using
Confluence Cloud, it is recommended to use an API token (if supported) for the
configured username value (see api_tokens_). If API tokens are not being used,
the plain password for the configured username value should be used.

.. code-block:: python

    confluence_server_pass = 'vsUsrSZ6Z4kmrQMapSXBYkJh'
        (or)
    confluence_server_pass = 'myawesomepassword'

confluence_server_url
~~~~~~~~~~~~~~~~~~~~~

The URL for Confluence. The URL should be prefixed with ``https://`` or
``http://`` (depending on the URL target). The target API folder should not be
included in the URL (for example, excluding ``/rest/api/`` or ``/rpc/xmlrpc/``).
For a Confluence Cloud instance, an example URL configuration is as follows:

.. code-block:: python

    confluence_server_url = 'https://example.atlassian.net/wiki'

For a Confluence Server instance, an example URL configuration, if the
instance's REST API is ``https://intranet-wiki.example.com/rest/api/`` or
XML-RPC API is at ``https://intranet-wiki.example.com/rpc/xmlrpc``, should be as
follows:

.. code-block:: python

    confluence_server_url = 'https://intranet-wiki.example.com'


confluence_server_user
~~~~~~~~~~~~~~~~~~~~~~

The username value used to authenticate with the Confluence instance. If using
Confluence Cloud, this value will most likely be the account's E-mail address.
If using Confluence server, this value will most likely be the username value.

.. code-block:: python

    confluence_server_user = 'myawesomeuser@example.com'
        (or)
    confluence_server_user = 'myawesomeuser'

confluence_space_name
~~~~~~~~~~~~~~~~~~~~~

Key of the space in Confluence to be used to publish generated documents to.

.. code-block:: python

    confluence_space_name = 'MyAwesomeSpace'


general configuration
---------------------

confluence_disable_notifications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A boolean value which explicitly disable any page update notifications (i.e.
treats page updates from a publish request as minor updates). By default,
notifications are enabled with a value of ``False``.

.. code-block:: python

    confluence_disable_notifications = True

confluence_header_file
~~~~~~~~~~~~~~~~~~~~~~

The name of the file to use header data. If provided, the contents found inside
the header file will be added to the start of all generated documents. The file
path provided should be relative to the build environment's source directory.
For example:

.. code-block:: python

    confluence_header_file = 'assets/header.tpl'

confluence_footer_file
~~~~~~~~~~~~~~~~~~~~~~

The name of the file to use footer data. If provided, the contents found inside
the footer file will be added at the end of all generated documents. The file
path provided should be relative to the build environment's source directory.
For example:

.. code-block:: python

    confluence_footer_file = 'assets/footer.tpl'

confluence_master_homepage
~~~~~~~~~~~~~~~~~~~~~~~~~~

A boolean value to whether or not force the configured space's homepage to be
set to the page defined by the Sphinx configuration's master_doc_. By default,
the master_doc_ configuration is ignored with a value of ``False``.

.. code-block:: python

    confluence_master_homepage = False

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
``confluence_parent_page`` setting.

confluence_parent_page
~~~~~~~~~~~~~~~~~~~~~~

The root page found inside the configured space (``confluence_space_name``)
where published pages will be a descendant of. The parent page value is used
to match with the title of an existing page. If this option is not provided,
pages will be published to the root of the configured space. If the parent page
cannot be found, the publish attempt will stop with an error message. For
example, the following will publish documentation under the ``MyAwesomeDocs``
page:

.. code-block:: python

    confluence_parent_page = 'MyAwesomeDocs'

If a parent page is not set, consider using the ``confluence_master_homepage``
option as well.

confluence_publish_prefix
~~~~~~~~~~~~~~~~~~~~~~~~~

If set, the prefix value is added to the title of all published document. In
Confluence, page names need to be unique for a space. A prefix can be set to
either:

* Add a unique naming schema to generated/published documents in a space which
  has manually created pages; or,
* Allow multiple published sets of documentation, each each with their own
  prefix value.

An example publish prefix is as follows:

.. code-block:: python

    confluence_publish_prefix = 'prefix-'

confluence_purge
~~~~~~~~~~~~~~~~

.. warning::

    Publishing individual/subset of documents with this option may lead to
    unexpected results.

A boolean value to whether or not purge legacy pages detected in a space or
parent page. By default, this value is set to ``False`` to indicate that no
pages will be removed. If this configuration is set to ``True``, detected pages
in Confluence that do not match the set of published documents will be
automatically removed. If the option ``confluence_parent_page`` is set, only
pages which are a descendant of the configured parent page can be removed;
elsewise, all pages in the configured space could be removed.

.. code-block:: python

    confluence_purge = False

While this capability is useful for updating a series of pages, it may lead to
unexpected results when attempting to publish a single-page update. The purge
operation will remove all pages that are not publish in the request. For
example, if an original request publishes ten documents and purges excess
documents, a following publish attempt with only one of the documents will purge
the other nine pages.

confluence_purge_from_master
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A boolean value to which indicates that any purging attempt should be done from
the root of a published master_doc_ page (instead of a configured parent page;
i.e. ``confluence_parent_page``). In specific publishing scenarios, a user may
wish to publish multiple documentation sets based off a single parent/container
page. To prevent any purging between multiple documentation sets, this option
can be set to ``True``. When generating legacy pages to be removed, this
extension will only attempt to populate legacy pages based off the children of
the master_doc_ page. This option still requires ``confluence_purge`` to be set
to ``True`` before taking effect.

.. code-block:: python

    confluence_purge_from_master = False

advanced configuration - processing
-----------------------------------

confluence_file_suffix
~~~~~~~~~~~~~~~~~~~~~~

The file name suffix to use for all generated files. By default, all generated
files will use the extension ``.conf`` (see ``confluence_file_transform``).

.. code-block:: python

    confluence_file_suffix = '.conf'

confluence_file_transform
~~~~~~~~~~~~~~~~~~~~~~~~~

A function to override the translation of a document name to a filename. The
provided function is used to perform translations for both Sphinx's
get_outdated_docs_ and write_doc_ methods. The default translation will be the
combination of "``docname`` + ``confluence_file_suffix``".

.. _get_outdated_docs: http://www.sphinx-doc.org/en/stable/extdev/builderapi.html#sphinx.builders.Builder.get_outdated_docs
.. _write_doc: http://www.sphinx-doc.org/en/stable/extdev/builderapi.html#sphinx.builders.Builder.write_doc

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

.. _Confluence-supported syntax highlight languages: https://confluence.atlassian.com/confcloud/code-block-macro-724765175.html
.. _Pygments documented language types: http://pygments.org/docs/lexers/

confluence_link_suffix
~~~~~~~~~~~~~~~~~~~~~~

The suffix name to use for for generated links to files. By default, all
generated links will use the value defined by ``confluence_file_suffix`` (see
``confluence_link_transform``).

.. code-block:: python

    confluence_link_suffix = '.conf'

confluence_link_transform
~~~~~~~~~~~~~~~~~~~~~~~~~

A function to override the translation of a document name to a (partial) URI.
The provided function is used to perform translations for both Sphinx's
get_relative_uri_ method. The default translation will be the combination of
"``docname`` + ``confluence_link_suffix``".

.. _get_relative_uri: http://www.sphinx-doc.org/en/stable/extdev/builderapi.html#sphinx.builders.Builder.get_relative_uri

confluence_remove_title
~~~~~~~~~~~~~~~~~~~~~~~

A boolean value to whether or not automatically remove the title section from
all published pages. In Confluence, page names are already presented at the top.
With this option enabled, this reduces having two leading headers with the
document's title. In some cases, a user may wish to not remove titles when
custom prefixes or other custom modifications are in play. By default, this
option is enabled with a value of ``True``.

.. code-block:: python

    confluence_remove_title = True

advanced configuration - publishing
-----------------------------------

confluence_ca_cert
~~~~~~~~~~~~~~~~~~

Provide a CA certificate to use for server cert authentication. Can either be a
file or a path. If you are using the rest interface, refer to the `Requests CA
docs`_ for information on what is supported. If you are using the XML-RPC
interface, refer to the `SSL CA docs`_. By default, verification is turned on
and can be turned off with the ``confluence_disable_ssl_validation`` config
option. If it is turned off, this option is ignored.

.. code-block:: python

    confluence_ca_cert = os.path.join('path', 'to', 'ca.crt')

confluence_client_cert
~~~~~~~~~~~~~~~~~~~~~~

Provide a client certificate to use for two-way TLS/SSL authentication. Can
either be a single file (containing the private key and the certificate) or
as a tuple of both file's paths. If the certificate is encrypted, you
will be prompted for a password during the publishing step.

.. code-block:: python

    confluence_client_cert = os.path.join('path', 'to', 'cert_and_key.pem')
    # or
    confluence_client_cert = ('client.cert', 'client.key')

confluence_client_cert_pass
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provide a password for the ``confluence_client_cert``. This prevents a prompt
from requesting your client certificate password. If your client certificate
is unencrypted, this value will be ignored.

.. code-block:: python

    confluence_client_cert_pass = 'password'

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

confluence_disable_rest
~~~~~~~~~~~~~~~~~~~~~~~

A boolean value to explicitly disable any REST API calls. This extension has the
ability to publish using either Confluence's REST or XML-RPC API calls. When
publishing, this extension will first attempt to publish using REST and fallback
to using XML-RPC. If the target Confluence instance cannot use REST for
publishing, it is recommended to set the option to ``True`` to always use
XML-RPC instead. By default, this option is set to ``False``.

.. code-block:: python

    confluence_disable_rest = False

confluence_disable_ssl_validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A boolean value to explicitly disable verification of server SSL certificates when
making a publish request. By default, this option is set to ``False``.

.. code-block:: python

    confluence_disable_ssl_validation = False

confluence_disable_xmlrpc
~~~~~~~~~~~~~~~~~~~~~~~~~

A boolean value to explicitly disable any XML-RPC API calls. This extension has
the ability to publish using either Confluence's REST or XML-RPC API calls. When
publishing, this extension will first attempt to publish using REST and fallback
to using XML-RPC. If the target Confluence instance supports REST or has XML-RPC
explicitly disabled, it is recommended to set this option to ``True``. By
default, this option is set to ``False``.

.. code-block:: python

    confluence_disable_xmlrpc = False

confluence_parent_page_id_check
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The page identifier check for ``confluence_parent_page``. By providing an
identifier of the parent page, both the parent page's name and identifier must
match before this extension will publish any content to a Confluence server.
This serves as a sanity-check configuration for the cautious.

.. code-block:: python

    confluence_parent_page_id_check = 1

confluence_proxy
~~~~~~~~~~~~~~~~

Provide the proxy needed to be used to interact with the Confluence server over
the network. At this time, the proxy configuration only applies to XML-RPC calls
(REST calls use the Requests_ library which will use system-defined proxy
configuration).

.. code-block:: python

    confluence_proxy = 'myawesomeproxy:8080'

confluence_timeout
~~~~~~~~~~~~~~~~~~

Force a timeout (in seconds) for network interaction. The timeout used by this
extension is not explicitly configured (i.e. managed by Requests_ and other
implementations). By default, assume that any network interaction will not
timeout. Since the target Confluence server is most likely to be found on an
external server, is it recommended to explicitly configure a timeout value based
on the environment being used. For example, to configure a timeout of ten
seconds, the following can be used:

.. code-block:: python

    confluence_timeout = 10

confluence_fmt_glossary_term, confluence_fmt_glossary_desc
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Formatting for the term and the description of the term within a Glossary_.
Basic `Confluence Wiki Markup`_ text formatting is supported and the markup
should be defined without the followin period and space:

.. code-block:: python

    confluence_fmt_glossary_term = 'h6' (default '')
    confluenct_fmt_glossary_desc = '' (default 'bg')

The empty string, `''` can be given to indicate that no formatting should be
applied.


.. _Requests: https://pypi.python.org/pypi/requests
.. _api_tokens: https://confluence.atlassian.com/cloud/api-tokens-938839638.html
.. _master_doc: http://www.sphinx-doc.org/en/stable/config.html#confval-master_doc
.. _toctree: http://www.sphinx-doc.org/en/stable/markup/toctree.html#directive-toctree
.. _Requests CA docs: http://docs.python-requests.org/en/master/user/advanced/#ssl-cert-verification
.. _SSL CA docs: https://docs.python.org/3/library/ssl.html#ssl.create_default_context
.. _Glossary: http://www.sphinx-doc.org/en/master/glossary.html
.. _Confluence Wiki Markup: https://confluence.atlassian.com/doc/confluence-wiki-markup-251003035.html
