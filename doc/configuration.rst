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

The password used to authenticate with the Confluence server.

.. code-block:: python

    confluence_server_pass = 'myawesomepassword'

confluence_server_url
~~~~~~~~~~~~~~~~~~~~~

The URL for Confluence. The URL should be prefixed with ``https://`` or
``http://``, depending on the URL target. The target API folder should not be
included -- for example, if the target Confluence server's REST API is
``https://intranet-wiki.example.com/rest/api/`` or XML-RPC API is at
``https://intranet-wiki.example.com/rpc/xmlrpc``, the URL configuration provided
should be as follows:

.. code-block:: python

    confluence_space_name = 'https://intranet-wiki.example.com'

confluence_server_user
~~~~~~~~~~~~~~~~~~~~~~

The username used to authenticate with the Confluence server.

.. code-block:: python

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

A boolean value to whether or not purge legacy pages detected in a space or
parent page. By default, this value is set to ``False`` to indicate that no
pages will be removed. If this configuration is set to ``True``, detected pages
in Confluence that do not match the set of published documents will be
automatically removed. If the option ``confluence_parent_page`` is set, only
pages which are a descendant of the configured parent page can be removed;
elsewise, all pages in the configured space could be removed.

.. code-block:: python

    confluence_purge = False

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

advanced configuration - publishing
-----------------------------------

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

A boolean value to explicitly disable any verification of SSL certificates when
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

.. _Requests: https://pypi.python.org/pypi/requests
.. _master_doc: http://www.sphinx-doc.org/en/stable/config.html#confval-master_doc
.. _toctree: http://www.sphinx-doc.org/en/stable/markup/toctree.html#directive-toctree
