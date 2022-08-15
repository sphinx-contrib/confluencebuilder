Configuration
=============

The following is an example of simple configuration (``config.py``) for
Confluence generation and publishing:

.. code-block:: python

    extensions = [
        'sphinxcontrib.confluencebuilder',
    ]
    confluence_publish = True
    confluence_space_key = 'TEST'
    confluence_parent_page = 'Documentation'
    confluence_server_url = 'https://intranet-wiki.example.com/'
    confluence_server_user = 'myawesomeuser'
    confluence_ask_password = True
    confluence_page_hierarchy = True

All configurations introduced by this extension are listed below. This
extension may take advantage of a subset of `Sphinx configurations`_ as well
when preparing documents.

.. only:: latex

    .. contents::
       :depth: 1
       :local:

Essential configuration
-----------------------

.. (documentation note) Typically, configuration entries should be sorted
   alphanumerically; however, an exception is in place for the "essential"
   configuration options, where there is a stronger desire to present key
   configurations in a specific order (publish, URL, space and authentication).

.. confval:: confluence_publish

    A boolean that decides whether or not to allow publishing. This option must
    be explicitly set to ``True`` if a user wishes to publish content. By
    default, the value is set to ``False``.

    .. code-block:: python

        confluence_publish = True

.. confval:: confluence_server_url

    The URL for the Confluence instance to publish to. The URL should be
    prefixed with ``https://`` or ``http://`` (depending on the URL target). The
    target API folder should not be included in the URL (i.e. excluding
    ``rest/api/``). For a Confluence Cloud instance, an example URL
    configuration is as follows:

    .. code-block:: python

        confluence_server_url = 'https://example.atlassian.net/wiki/'

    For a Confluence Server instance, an example URL configuration, if the
    instance's REST API is ``https://intranet-wiki.example.com/rest/api/``,
    should be as follows:

    .. code-block:: python

        confluence_server_url = 'https://intranet-wiki.example.com/'

.. |confluence_space_key| replace:: ``confluence_space_key``
.. _confluence_space_key:

.. confval:: confluence_space_key

    .. versionadded:: 1.7

    .. note::

        - Use the key value for the space, not the name of the space. For
          example, ``MYAWESOMESPACE`` instead of ``My Awesome Space``.
        - The space key is **case-sensitive** (typically uppercase).

    `Key of the space`_ in Confluence to be used to publish generated documents
    to. For example:

    .. code-block:: python

        confluence_space_key = 'MYAWESOMESPACE'

    If attempting to publish to a user's personal space, the space's key will
    typically start with a tilde value followed by the space's identifier. For
    example:

    .. code-block:: python

        confluence_space_key = '~123456789'

.. |confluence_server_user| replace:: ``confluence_server_user``
.. _confluence_server_user:

.. confval:: confluence_server_user

    .. note::

        If using a personal access token (PAT), this option does not need to
        set (see |confluence_publish_token|_).

    The username value used to authenticate with the Confluence instance. If
    using Confluence Cloud, this value will most likely be the account's E-mail
    address. If using Confluence Server, this value will most likely be the
    username value.

    .. code-block:: python

        confluence_server_user = 'myawesomeuser@example.com'
         (or)
        confluence_server_user = 'myawesomeuser'

.. |confluence_server_pass| replace:: ``confluence_server_pass``
.. _confluence_server_pass:

.. confval:: confluence_server_pass

    .. caution::

        It is never recommended to store an API token or raw password into a
        committed/shared repository holding documentation.

        A documentation's configuration can modified various ways with Python
        to pull an authentication token for a publishing event such as
        :ref:`reading from an environment variable <tip_manage_publish_subset>`,
        reading from a local file or acquiring a password from ``getpass``. If
        desired, this extension provides a method for prompting for a
        password (see |confluence_ask_password|_).

    .. note::

        If attempting to use a personal access token (PAT), use the
        |confluence_publish_token|_ option instead.

    The password value used to authenticate with the Confluence instance. If
    using Confluence Cloud, it is recommended to use an API token for the
    configured username value (see `API tokens`_):

    .. code-block:: python

        confluence_server_pass = 'vsUsrSZ6Z4kmrQMapSXBYkJh'

    If `API tokens`_ are not being used, the plain password for the configured
    username value can be used:

    .. code-block:: python

        confluence_server_pass = 'myawesomepassword'

.. |confluence_publish_token| replace:: ``confluence_publish_token``
.. _confluence_publish_token:

.. confval:: confluence_publish_token

    .. versionadded:: 1.8

    .. caution::

        It is never recommended to store a personal access tokens (PAT) into a
        committed/shared repository holding documentation.

        A documentation's configuration can modified various ways with Python
        to pull an authentication token for a publishing event such as
        :ref:`reading from an environment variable <tip_manage_publish_subset>`,
        reading from a local file or acquiring a token from ``getpass``.

    .. note::

        If attempting to use an API token, use the |confluence_server_pass|_
        option instead.

    The personal access token value used to authenticate with the Confluence
    instance (see `Using Personal Access Tokens`_):

    .. code-block:: python

        confluence_publish_token = 'AbCdEfGhIjKlMnOpQrStUvWxY/z1234567890aBc'

Generic configuration
---------------------

.. |confluence_add_secnumbers| replace:: ``confluence_add_secnumbers``
.. _confluence_add_secnumbers:

.. confval:: confluence_add_secnumbers

    .. versionadded:: 1.2

    Add section numbers to page and section titles if ``toctree`` uses the
    ``:numbered:`` option. By default, this is enabled:

    .. code-block:: python

        confluence_add_secnumbers = True

    See also |confluence_publish_prefix|_.

.. confval:: confluence_default_alignment

    .. versionadded:: 1.3

    Explicitly set which alignment type to use when a default alignment value is
    detected. As of Sphinx 2.0+, the default alignment is set to ``center``.
    Legacy versions of Sphinx had a default alignment of ``left``. By default,
    this extension will use a Sphinx-defined default alignment unless explicitly
    set by this configuration value. Accepted values are ``left``, ``center`` or
    ``right``.

    .. code-block:: python

        confluence_default_alignment = 'left'

.. confval:: confluence_domain_indices

    .. versionadded:: 1.7

    A boolean or list value to configure whether or not generate domain-specific
    indices. If configured to a value of ``True``, all domain-specific indices
    generated when processing a documentation set will have a Confluence
    document created. If configured with a list of index names, any matching
    domain-index with a matching name will have a Confluence document created.
    By default, domain-specific indices are disabled with a value of ``False``.

    .. code-block:: python

        confluence_domain_indices = True
         (or)
        confluence_domain_indices = [
            'py-modindex',
        ]

.. |confluence_header_file| replace:: ``confluence_header_file``
.. _confluence_header_file:

.. confval:: confluence_header_file

    The name of the file to use header data. If provided, the raw contents found
    inside the header file will be added to the start of all generated
    documents. The file path provided should be relative to the build
    environment's source directory. For example:

    .. code-block:: python

        confluence_header_file = 'assets/header.tpl'

    See also:
    
    - |confluence_footer_file|_ 
    - |confluence_header_data|_

.. confval:: confluence_header_data

    .. versionadded:: 1.9

    Takes an optional dictionary. If this value is set then
    ``confluence_header_file`` is interpreted as a jinja2 template with these
    values passed in. If this value is not set then ``confluence_header_file``
    is included verbatim.

    See also |confluence_header_file|_.

.. |confluence_footer_file| replace:: ``confluence_footer_file``
.. _confluence_footer_file:

.. confval:: confluence_footer_file

    The name of the file to use footer data. If provided, the raw contents found
    inside the footer file will be added at the end of all generated documents.
    The file path provided should be relative to the build environment's source
    directory. For example:

    .. code-block:: python

        confluence_footer_file = 'assets/footer.tpl'

    See also:
    
    - |confluence_header_file|_ 
    - |confluence_footer_data|_

.. confval:: confluence_footer_data

    .. versionadded:: 1.9
    
    Takes an optional dictionary. If this value is set then
    ``confluence_footer_file`` is interpreted as a jinja2 template with these
    values passed in. If this value is not set then ``confluence_footer_file``
    is included verbatim.

    See also |confluence_header_file|_.

.. confval:: confluence_include_search

    .. versionadded:: 1.7

    A boolean value to configure whether or not generate a search page. If
    configured to a value of ``True``, a search page will be created with a
    search macro configured to search on the configured space. If a ``search``
    document is registered in a documentation's toctree_, a search page will be
    generated and will replace the contents of the provided ``search`` page. To
    avoid the implicit enablement of this feature, the generation of a search
    page can be explicitly disabled by setting this value to ``False``. By
    default, search page generation is automatically managed with a value of
    ``None``.

    .. code-block:: python

        confluence_include_search = True

.. confval:: confluence_max_doc_depth

    .. important::

        This feature is deprecated. If there is a desire to generate a single
        document page instead, consider using the ``singleconfluence``
        :doc:`builder <builders>` instead.

    A positive integer value, if provided, to indicate the maximum depth
    permitted for a nested child page before its contents is inlined with a
    parent. The root of all pages is typically the configured root_doc_. The
    root page is considered to be at a depth of zero. By default, the maximum
    document depth is disabled with a value of ``None``.

    .. code-block:: python

        confluence_max_doc_depth = 2

.. confval:: confluence_page_generation_notice

    .. versionadded:: 1.7

    A boolean value to whether or not to generate a message at the top of each
    document that the page has been automatically generated. By default, this
    notice is disabled with a value of ``False``.

    .. code-block:: python

        confluence_page_generation_notice = True

.. confval:: confluence_page_hierarchy

    A boolean value to whether or not nest pages in a hierarchical ordered. The
    root of all pages is typically the configured root_doc_. If a root_doc_
    instance contains a toctree_, listed documents will become child pages of
    the root_doc_. This cycle continues for child pages with their own
    toctree_ markups. By default, hierarchy mode is disabled with a value of
    ``False``.

    .. code-block:: python

        confluence_page_hierarchy = True

    Note that even if hierarchy mode is enabled, the configured root_doc_ page
    and other published pages that are not defined in the complete toctree_,
    these documents will still be published and uploaded to either the
    configured |confluence_parent_page|_ or in the root of the space.

    .. important::

        This feature will default to ``True`` in a v2.0 release. Users who do
        not want to use hierarchy mode should explicitly configure this to
        ``False`` in their configurations.

.. |confluence_prev_next_buttons_location| replace:: ``confluence_prev_next_buttons_location``
.. _confluence_prev_next_buttons_location:

.. confval:: confluence_prev_next_buttons_location

    .. versionadded:: 1.2

    A string value to where to include previous/next buttons (if any) based on
    the detected order of documents to be included in processing. Values
    accepted are either ``bottom``, ``both``, ``top`` or ``None``. By default,
    no previous/next links are generated with a value of ``None``.

    .. code-block:: python

       confluence_prev_next_buttons_location = 'top'

.. |confluence_secnumber_suffix| replace:: ``confluence_secnumber_suffix``
.. _confluence_secnumber_suffix:

.. confval:: confluence_secnumber_suffix

    .. versionadded:: 1.2

    The suffix to put after section numbers, before section name.

    .. code-block:: python

        confluence_secnumber_suffix = '. '

    See also |confluence_add_secnumbers|_.

.. confval:: confluence_use_index

    .. versionadded:: 1.7

    A boolean value to configure whether or not generate an index page. If
    configured to a value of ``True``, an index page will be created. If a
    ``genindex`` document is registered in a documentation's toctree_, index
    content will be generated and will replace the contents of the provided
    ``genindex`` page. To avoid the implicit enablement of this feature, the
    generation of an index page can be explicitly disabled by setting this value
    to ``False``. By default, index generation is automatically managed with a
    value of ``None``.

    .. code-block:: python

        confluence_use_index = True

.. confval:: singleconfluence_toctree

    .. versionadded:: 1.7

    A boolean value to configure whether or not TOC trees will remain in place
    when building with a ``singleconfluence`` builder. By default, this option
    is disabled with a value of ``False``.

    .. code-block:: python

        singleconfluence_toctree = True

Publishing configuration
------------------------

.. |confluence_ask_password| replace:: ``confluence_ask_password``
.. _confluence_ask_password:

.. confval:: confluence_ask_password

    .. warning::

        User's running Cygwin/MinGW may need to invoke with ``winpty`` to allow
        this feature to work.

    Provides an override for an interactive shell to request publishing
    documents using an API key or password provided from a shell environment.
    While a password is typically defined in the option
    ``confluence_server_pass`` (either directly set, fetched from the project's
    ``config.py`` or passed via an alternative means), select environments may
    wish to provide a way to accept an authentication token without needing to
    modify documentation sources or having a visible password value in the
    interactive session requesting the publish event. By default, this
    option is disabled with a value of ``False``.

    .. code-block:: python

        confluence_ask_password = False

    A user can request for a password prompt by invoking build event by passing
    the define through the command line:

    .. code-block:: none

        sphinx-build [options] -D confluence_ask_password=1 <srcdir> <outdir>

    Note that some shell sessions may not be able to pull the password value
    properly from the user. For example, Cygwin/MinGW may not be able to accept
    a password unless invoked with ``winpty``.

.. confval:: confluence_ask_user

    .. versionadded:: 1.2

    Provides an override for an interactive shell to request publishing
    documents using a user provided from a shell environment. While a
    user is typically defined in the option ``confluence_server_user``, select
    environments may wish to provide a way to accept a username without needing
    to modify documentation sources. By default, this option is disabled with a
    value of ``False``.

    .. code-block:: python

        confluence_ask_user = False

.. |confluence_disable_autogen_title| replace:: ``confluence_disable_autogen_title``
.. _confluence_disable_autogen_title:

.. confval:: confluence_disable_autogen_title

    A boolean value to explicitly disable the automatic generation of titles for
    documents which do not have a title set. When this extension processes a set
    of documents to publish, a document needs a title value to know which
    Confluence page to create/update. In the event where a title value cannot be
    extracted from a document, a title value will be automatically generated for
    the document. For automatically generated titles, the value will always be
    prefixed with ``autogen-``. For users who wish to ignore pages which have no
    title, this option can be set to ``True``. By default, this option is set to
    ``False``.

    .. code-block:: python

        confluence_disable_autogen_title = True

    See also:

    - |confluence_remove_title|_
    - |confluence_title_overrides|_

.. |confluence_disable_notifications| replace:: ``confluence_disable_notifications``
.. _confluence_disable_notifications:

.. confval:: confluence_disable_notifications

    A boolean value which explicitly disables any page update notifications
    (i.e. treats page updates from a publish request as minor updates). By
    default, notifications are enabled with a value of ``False``.

    .. code-block:: python

        confluence_disable_notifications = True

    Note that even if this option is set, there may be some scenarios where a
    notification will be generated for other users when a page is created or
    removed, depending on how other users may be watching a space.

    See also |confluence_watch|_.

.. |confluence_global_labels| replace:: ``confluence_global_labels``
.. _confluence_global_labels:

.. confval:: confluence_global_labels

    .. versionadded:: 1.3

    Defines a list of labels to apply to each document being published. When a
    publish event either adds a new page or updates an existing page, the labels
    defined in this option will be added/set on the page. For example:

    .. code-block:: python

        confluence_global_labels = [
            'label-a',
            'label-b',
        ]

    For per-document labels, please consult the ``confluence_metadata``
    :ref:`directive <confluence_metadata>`. See also
    |confluence_append_labels|_.

.. |confluence_root_homepage| replace:: ``confluence_root_homepage``
.. _confluence_root_homepage:

.. confval:: confluence_root_homepage

    .. versionadded:: 1.6

    A boolean value to whether or not force the configured space's homepage to
    be set to the page defined by the Sphinx configuration's root_doc_. By
    default, the root_doc_ configuration is ignored with a value of ``False``.

    .. code-block:: python

        confluence_root_homepage = False

.. |confluence_parent_page| replace:: ``confluence_parent_page``
.. _confluence_parent_page:

.. confval:: confluence_parent_page

    .. note::

        This option cannot be used with |confluence_publish_root|_.

    .. versionchanged:: 1.9 Support added for accepting a page identifier.

    The root page found inside the configured space (|confluence_space_key|_)
    where published pages will be a descendant of. The parent page value is used
    to match either the title or page identifier of an existing page. If this
    option is not provided, new pages will be published to the root of the
    configured space. If the parent page cannot be found, the publish attempt
    will stop with an error message. For example, the following will publish
    documentation under the ``MyAwesomeDocs`` page:

    .. code-block:: python

        confluence_parent_page = 'MyAwesomeDocs'

    Users wishing to publish against a parent page's identifier value can do
    so by using an integer value instead. For example:

    .. code-block:: python

        confluence_parent_page = 123456

    If a parent page is not set, consider using the
    |confluence_root_homepage|_ option as well. Note that the page's name can
    be case-sensitive in most (if not all) versions of Confluence.

    See also |confluence_publish_root|_.

.. |confluence_publish_postfix| replace:: ``confluence_publish_postfix``
.. _confluence_publish_postfix:

.. confval:: confluence_publish_postfix

    .. versionadded:: 1.2

    If set, a postfix value is added to the title of all published documents. In
    Confluence, page names need to be unique for a space. A postfix can be set
    to either:

    * Add a unique naming schema to generated/published documents in a space
      which has manually created pages; or,
    * Allow multiple published sets of documentation, each with their own
      postfix value.

    An example publish postfix is as follows:

    .. code-block:: python

       confluence_publish_postfix = '-postfix'

    Postfixes can use variable placeholders. These placeholders are filled using the
    format method so all formatting types can be used.

    The currently supported placeholders

    * {hash} - Create a reproduceable hash given the title and directory location of the file.
               Using this placeholder is an option for allowing pages with the same title to be
               pushed to the same space without needing to manually add an index to the title

    Note, pages with the same title must have different parent pages.

    By default, no postfix is used. See also:

    - |confluence_ignore_titlefix_on_index|_
    - |confluence_publish_prefix|_

.. |confluence_publish_prefix| replace:: ``confluence_publish_prefix``
.. _confluence_publish_prefix:

.. confval:: confluence_publish_prefix

    If set, a prefix value is added to the title of all published documents. In
    Confluence, page names need to be unique for a space. A prefix can be set to
    either:

    * Add a unique naming schema to generated/published documents in a space
      which has manually created pages; or,
    * Allow multiple published sets of documentation, each with their own prefix
      value.

    An example publish prefix is as follows:

    .. code-block:: python

       confluence_publish_prefix = 'prefix-'

    By default, no prefix is used. See also:

    - |confluence_ignore_titlefix_on_index|_
    - |confluence_publish_postfix|_

.. |confluence_publish_root| replace:: ``confluence_publish_root``
.. _confluence_publish_root:

.. confval:: confluence_publish_root

    .. versionadded:: 1.5

    .. note::

        This option cannot be used with |confluence_parent_page|_.

    The page identifier to publish the root document to. The root identifier
    value is used to find an existing page on the configured Confluence
    instance. When found, the root document of the documentation set being
    published will replace the content of the page found on the Confluence
    instance. If the root page cannot be found, the publish attempt will stop
    with an error message.

    .. code-block:: python

       confluence_publish_root = 123456

    See also |confluence_parent_page|_.

.. index:: Page removal; Automatically purging pages

.. |confluence_purge| replace:: ``confluence_purge``
.. _confluence_purge:

.. confval:: confluence_purge

    .. warning::

       Publishing individual/subset of documents with this option may lead to
       unexpected results.

    A boolean value to whether or not purge legacy pages detected in a space or
    parent page. By default, this value is set to ``False`` to indicate that no
    pages will be removed. If this configuration is set to ``True``, detected
    pages in Confluence that do not match the set of published documents will be
    automatically removed. If the option |confluence_parent_page|_ is set, only
    pages which are a descendant of the configured parent page can be removed;
    otherwise, all flagged pages in the configured space could be removed.

    .. code-block:: python

        confluence_purge = False

    While this capability is useful for updating a series of pages, it may lead
    to unexpected results when attempting to publish a single-page update. The
    purge operation will remove all pages that are not publish in the request.
    For example, if an original request publishes ten documents and purges
    excess documents, a following publish attempt with only one of the documents
    will purge the other nine pages.

    See also:

    - |confluence_publish_dryrun|_
    - |confluence_purge_from_root|_

.. |confluence_purge_from_root| replace:: ``confluence_purge_from_root``
.. _confluence_purge_from_root:

.. confval:: confluence_purge_from_root

    .. versionadded:: 1.6

    A boolean value to which indicates that any purging attempt should be done
    from the root of a published root_doc_ page (instead of a configured parent
    page; i.e. |confluence_parent_page|_). In specific publishing scenarios, a
    user may wish to publish multiple documentation sets based off a single
    parent/container page. To prevent any purging between multiple documentation
    sets, this option can be set to ``True``. When generating legacy pages to be
    removed, this extension will only attempt to populate legacy pages based off
    the children of the root_doc_ page. This option requires |confluence_purge|_
    to be set to ``True`` before taking effect. If |confluence_publish_root|_ is
    set, this option is implicitly enabled.

    .. code-block:: python

        confluence_purge_from_root = False

    See also |confluence_purge|_.

.. confval:: confluence_sourcelink

    .. versionadded:: 1.7

    Provides options to include a link to the documentation's sources at the top
    of each page. This can either be a generic URL or customized to link to
    individual documents in a repository.

    An example of a simple link is as follows:

    .. code-block:: python

        confluence_sourcelink = {
            'url': 'https//www.example.com/',
        }

    Templates for popular hosting services are available. Instead of defining
    a ``url`` option, the ``type`` option can instead be set to one of the
    following types:

    - ``bitbucket``
    - ``github``
    - ``gitlab``

    Options to set for these types are as follows:

    .. rst-class:: spacedtable

    +-----------------+-------------------------------------------------------+
    | Option          | Description                                           |
    +=================+=======================================================+
    | | ``owner``     | The owner (group or user) of a project.               |
    | | *(required)*  |                                                       |
    +-----------------+-------------------------------------------------------+
    | | ``repo``      | The name of the repository.                           |
    | | *(required)*  |                                                       |
    +-----------------+-------------------------------------------------------+
    | ``container``   | The folder inside the repository which is holding the |
    |                 | documentation. This will vary per project, for        |
    |                 | example, this may be ``Documentation/`` or ``doc/``.  |
    |                 | If the documentation resides in the root of the       |
    |                 | repository, this option can be omitted or set to an   |
    |                 | empty string.                                         |
    +-----------------+-------------------------------------------------------+
    | | ``version``   | The version of the sources to list. This is typically |
    | | *(required)*  | set to either a branch (e.g. ``main``) or tag value.  |
    +-----------------+-------------------------------------------------------+
    | ``view``        | The view mode to configure. By default, this value is |
    |                 | set to ``blob`` for GitHub/GitLab and ``view`` for    |
    |                 | Bitbucket.                                            |
    |                 |                                                       |
    |                 | GitHub/GitLab users may wish to change this to        |
    |                 | ``edit`` to create a link directly to the editing     |
    |                 | view for a specific document.                         |
    +-----------------+-------------------------------------------------------+
    | ``host``        | The hostname value to override.                       |
    |                 |                                                       |
    |                 | This option is useful for instances where a custom    |
    |                 | domain may be configured for an organization.         |
    +-----------------+-------------------------------------------------------+
    | ``protocol``    | The protocol value to override (defaults to           |
    |                 | ``https``).                                           |
    +-----------------+-------------------------------------------------------+

    For example, a project hosted on GitHub can use the following:

    .. code-block:: python

        confluence_sourcelink = {
            'type': 'github',
            'owner': 'sphinx-contrib',
            'repo': 'confluencebuilder',
            'container': 'doc/',
            'version': 'master',
            'view': 'edit',
        }

    For unique environments, the source URL can be customized through the
    ``url`` option. This option is treated as a format string which can be
    populated based on the configuration and individual documents being
    processed. An example is as follows:

    .. code-block:: python

        confluence_sourcelink = {
            'url': 'https://git.example.com/mydocs/{page}{suffix}',
        }

    This configures a base URL, where ``page`` and ``suffix`` will be generated
    automatically. Any option provided in the ``confluence_sourcelink``
    dictionary will be forwarded to the format option. For example:

    .. code-block:: python

        confluence_sourcelink = {
            'base': 'https://git.example.com/mydocs',
            'url': '{base}/{version}/{page}{suffix}',
            'version': 'main',
        }

    The ``text`` option can be used to override the name of the link observed
    at the top of the page:

    .. code-block:: python

        confluence_sourcelink = {
            ...
            'text': 'Edit Source',
        }

.. |confluence_title_overrides| replace:: ``confluence_title_overrides``
.. _confluence_title_overrides:

.. confval:: confluence_title_overrides

    .. versionadded:: 1.3

    Allows a user to override the title value for a specific document. When
    documents are parsed for title values, the first title element's content
    will be used as the publish page's title. Select documents may not include a
    title and are ignored; or, documents may conflict with each other but there
    is a desire to keep them the same name in reStructuredText form. With
    ``confluence_title_overrides``, a user can define a dictionary which will
    map a given docname to a title value instead of the title element (if any)
    found in the respective document. By default, documents will give assigned
    titles values based off the first detected title element with a value of
    ``None``.

    .. code-block:: python

        confluence_title_overrides = {
            'index': 'Index Override',
        }

    See also:

    - :ref:`Confluence Spaces and Unique Page Names <confluence_unique_page_names>`
    - |confluence_disable_autogen_title|_
    - |confluence_publish_postfix|_
    - |confluence_publish_prefix|_
    - |confluence_remove_title|_

.. _confluence_timeout:

.. confval:: confluence_timeout

    Force a timeout (in seconds) for network interaction. The timeout used by
    this extension is not explicitly configured (i.e. managed by Requests_). By
    default, assume that any network interaction will not timeout. Since the
    target Confluence instance is most likely to be found on an external server,
    is it recommended to explicitly configure a timeout value based on the
    environment being used. For example, to configure a timeout of ten seconds,
    the following can be used:

    .. code-block:: python

        confluence_timeout = 10

.. |confluence_watch| replace:: ``confluence_watch``
.. _confluence_watch:

.. confval:: confluence_watch

    .. versionadded:: 1.3

    Indicate whether or not the user publishing content will automatically watch
    pages for changes. In Confluence, when creating a new page or updating an
    existing page, the editing user will automatically watch the page.
    Notifications on automatically published content is typically not relevant
    to publishers through this extension, especially if the content is volatile.
    If a publisher wishes to be keep informed on notification for published
    pages, this option can be set to ``True``. By default, watching is disabled
    with a value of ``False``.

    .. code-block:: python

        confluence_watch = False

    See also |confluence_disable_notifications|_.

Advanced publishing configuration
---------------------------------

.. |confluence_append_labels| replace:: ``confluence_append_labels``
.. _confluence_append_labels:

.. confval:: confluence_append_labels

    .. versionadded:: 1.3

    Allows a user to decide how to manage labels for an updated page. When a
    page update contains new labels to set, they can either be stacked on
    existing labels or replaced. In the event that a publisher wishes to replace
    any existing labels that are set on published pages, this option can be set
    to ``False``. By default, labels are always appended with a value of
    ``True``.

    .. code-block:: python

        confluence_append_labels = True

    See also:

    - |confluence_global_labels|_
    - ``confluence_metadata`` :ref:`directive <confluence_metadata>`

.. confval:: confluence_asset_force_standalone

    .. versionadded:: 1.3

    Provides an override to always publish individual assets (images, downloads,
    etc.) on each individual document which uses them. This extension will
    attempt to minimize the amount of publishing of shared assets on multiple
    documents by only hosting an asset in a single document. For example, if two
    documents use the same image, the image will be hosted on the root document
    of a set and each document will reference the attachment on the root page. A
    user may wish to override this feature. By configuring this option to
    ``True``, this extension will publish asset files as an attachment for each
    document which may use the asset. By default, this extension will attempt to
    host shared assets on a single document with a value of ``False``.

    .. code-block:: python

        confluence_asset_force_standalone = True

.. confval:: confluence_asset_override

    Provides an override for asset publishing to allow a user publishing to
    either force re-publishing assets or disable asset publishing. This
    extension will attempt to publish assets (images, downloads, etc.) to pages
    via Confluence's attachment feature. Attachments are assigned a comment
    value with a hash value of a published asset. If another publishing event
    occurs, the hash value is checked before attempting to re-publish an asset.
    In unique scenarios, are use may wish to override this ability. By
    configuring this option to ``True``, this extension will always publish
    asset files (whether or not an attachment with a matching hash exists). By
    configuring this option to ``False``, no assets will be published by this
    extension. By default, this automatic asset publishing occurs with a value
    of ``None``.

    .. code-block:: python

        confluence_asset_override = None

.. |confluence_ca_cert| replace:: ``confluence_ca_cert``
.. _confluence_ca_cert:

.. confval:: confluence_ca_cert

    Provide a CA certificate to use for server certificate authentication. The
    value for this option can either be a file of a certificate or a path
    pointing to an OpenSSL-prepared directory. Refer to the
    `Requests SSL Cert Verification`_  documentation (``verify``) for more
    information. If server verification is explicitly disabled, this option is
    ignored. By default, this option is ignored with a value of ``None``.

    .. code-block:: python

        confluence_ca_cert = 'ca.crt'

    See also:

    - |confluence_client_cert_pass|_
    - |confluence_client_cert|_
    - |confluence_disable_ssl_validation|_

.. |confluence_client_cert| replace:: ``confluence_client_cert``
.. _confluence_client_cert:

.. confval:: confluence_client_cert

    Provide a client certificate to use for two-way TLS/SSL authentication. The
    value for this option can either be a file (containing a certificate and
    private key) or as a tuple where both certificate and private keys are
    explicitly provided. If a private key is protected with a passphrase, a user
    publishing a documentation set will be prompted for a password (see also
    |confluence_client_cert_pass|_). By default, this option is ignored with a
    value of ``None``.

    .. code-block:: python

        confluence_client_cert = 'cert_and_key.pem'
         (or)
        confluence_client_cert = ('client.cert', 'client.key')

    See also:

    - |confluence_ca_cert|_
    - |confluence_client_cert_pass|_
    - |confluence_disable_ssl_validation|_

.. |confluence_client_cert_pass| replace:: ``confluence_client_cert_pass``
.. _confluence_client_cert_pass:

.. confval:: confluence_client_cert_pass

    .. caution::

        It is never recommended to store a certificate's passphrase into a
        committed/shared repository holding documentation.

    Provide a passphrase for |confluence_client_cert|_. This prevents a user
    from being prompted to enter a passphrase for a private key when publishing.
    If a configured private key is not protected by a passphrase, this value
    will be ignored. By default, this option is ignored with a value of
    ``None``.

    .. code-block:: python

        confluence_client_cert_pass = 'passphrase'

    - |confluence_ca_cert|_
    - |confluence_client_cert|_
    - |confluence_disable_ssl_validation|_

.. |confluence_disable_ssl_validation| replace::
   ``confluence_disable_ssl_validation``
.. _confluence_disable_ssl_validation:

.. confval:: confluence_disable_ssl_validation

    .. warning::

        It is not recommended to use this option.

    A boolean value to explicitly disable verification of server SSL
    certificates when making a publish request. By default, this option is set
    to ``False``.

    .. code-block:: python

        confluence_disable_ssl_validation = False

    - |confluence_ca_cert|_
    - |confluence_client_cert|_
    - |confluence_client_cert_pass|_

.. |confluence_ignore_titlefix_on_index| replace:: ``confluence_ignore_titlefix_on_index``
.. _confluence_ignore_titlefix_on_index:

.. confval:: confluence_ignore_titlefix_on_index

    .. versionadded:: 1.3

    When configured to add a prefix or postfix onto the titles of published
    documents, a user may not want to have any title modifications on the index
    page. To prevent modifying an index page's title, this option can be set to
    ``True``. By default, this option is set to ``False``.

    .. code-block:: python

        confluence_ignore_titlefix_on_index = True

    See also:

    - |confluence_publish_postfix|_
    - |confluence_publish_prefix|_

.. confval:: confluence_proxy

    REST calls use the Requests_ library, which will use system-defined proxy
    configuration; however, a user can override the system-defined proxy by
    providing a proxy server using this configuration.

    .. code-block:: python

        confluence_proxy = 'myawesomeproxy:8080'

.. |confluence_publish_allowlist| replace:: ``confluence_publish_allowlist``
.. _confluence_publish_allowlist:

.. confval:: confluence_publish_allowlist

    .. versionadded:: 1.3

    .. note::

        Using this option will disable the |confluence_purge|_ option.

    Defines a list of documents to be published to a Confluence instance. When a
    user invokes sphinx-build_, a user has the ability to process all documents
    (by default) or specifying individual filenames which use the provide files
    and detected dependencies. If the Sphinx-detected set of documents to
    process contains undesired documents to publish,
    ``confluence_publish_allowlist`` can be used to override this. This option
    accepts either a list of relative path document names (without an extension)
    or a filename which contains a list of document names.

    For example, a user can specify documents in a list to allow for publishing:

    .. code-block:: python

        confluence_publish_allowlist = [
            'index',
            'foo/bar',
        ]

    Alternatively, a user can specify a filename such as following:

    .. code-block:: python

        confluence_publish_allowlist = 'allowed-docs.txt'

    Which could contain a list of documents to allow:

    .. code-block:: python

        index
        foo/bar

    A user can configured an allowed list of documents through the command line:

    .. code-block:: shell

        sphinx-build [options] -D confluence_publish_allowlist=index,foo/bar \
            <srcdir> <outdir> index.rst foo/bar.rst

    By default, this option is ignored with a value of ``None``.

    See also |confluence_publish_denylist|_.

.. confval:: confluence_publish_debug

    .. versionadded:: 1.8

    A boolean value to whether or not to print debug requests made to a
    Confluence instance. This can be helpful for users attempting to debug
    their connection to a Confluence instance. By default, this option is
    disabled with a value of ``False``.

    .. code-block:: python

        confluence_publish_debug = True

.. confval:: confluence_publish_delay

    .. versionadded:: 1.8

    Force a delay (in seconds) for any API calls made to a Confluence instance.
    By default, API requests will be made to a Confluence instance as soon as
    possible (or until Confluence reports that the client should be rate
    limiting). A user can use this option to reduce how fast this extension may
    attempt to interact with the Confluence instance. For example, to delay each
    API request by almost a 1/4 of a second, the following can be used:

    .. code-block:: python

        confluence_publish_delay = 0.25

.. |confluence_publish_denylist| replace:: ``confluence_publish_denylist``
.. _confluence_publish_denylist:

.. confval:: confluence_publish_denylist

    .. versionadded:: 1.3

    .. note::

        Using this option will disable the |confluence_purge|_ option.

    Defines a list of documents to not be published to a Confluence instance.
    When a user invokes sphinx-build_, a user has the ability to process all
    documents (by default) or specifying individual filenames which use the
    provide files and detected dependencies. If the Sphinx-detected set of
    documents to process contain undesired documents to publish,
    ``confluence_publish_denylist`` can be used to override this. This option
    accepts either a list of relative path document names (without an extension)
    or a filename which contains a list of document names.

    For example, a user can specify documents in a list to deny for publishing:

    .. code-block:: python

        confluence_publish_denylist = [
            'index',
            'foo/bar',
        ]

    Alternatively, a user can specify a filename such as following:

    .. code-block:: python

        confluence_publish_denylist = 'denied-docs.txt'

    Which could contain a list of documents to allow:

    .. code-block:: python

        index
        foo/bar

    A user can configured a denied list of documents through the command line:

    .. code-block:: shell

        sphinx-build [options] -D confluence_publish_denylist=index,foo/bar \
            <srcdir> <outdir> index.rst foo/bar.rst

    By default, this option is ignored with a value of ``None``.

    See also |confluence_publish_allowlist|_.

.. confval:: confluence_publish_disable_api_prefix

    A boolean value which explicitly disables the use of the ``rest/api`` in
    the Confluence publish URL. This can be useful for environments where the
    API endpoint for a Confluence instance is proxied through a non-standard
    location. By default, API prefixes are enabled with a value of ``False``.

    .. code-block:: python

        confluence_publish_disable_api_prefix = True

.. |confluence_publish_dryrun| replace:: ``confluence_publish_dryrun``
.. _confluence_publish_dryrun:

.. confval:: confluence_publish_dryrun

    .. versionadded:: 1.3

    When a user wishes to start managing a new document set for publishing,
    there maybe concerns about conflicts with existing content. When the dry run
    feature is enabled to ``True``, a publish event will not edit or remove any
    existing content. Instead, the extension will inform the user which pages
    will be created, whether or not pages will be moved and whether or not
    pages/attachments will be removed. By default, the dry run feature is
    disabled with a value of ``False``.

    .. code-block:: python

        confluence_publish_dryrun = True

    See also
    :ref:`Confluence Spaces and Unique Page Names <confluence_unique_page_names>`.

.. confval:: confluence_publish_headers

    .. versionadded:: 1.5

    A dictionary value which allows a user to pass key-value header information.
    This is useful for users who need to interact with a Confluence instance
    which expects (in a reverse proxy or the instance itself) specific header
    information to be set. By default, no custom header entries are added with a
    value of ``None``.

    .. code-block:: python

        confluence_publish_headers = {
            'CUSTOM_HEADER': '<some-value>',
        }

.. confval:: confluence_publish_onlynew

    .. versionadded:: 1.3

    A publish event will from this extension will typically upload new pages or
    update existing pages on future attempts. In select cases, a user may not
    wish to modify existing pages and only permit adding new content to a
    Confluence space. To achieve this, a user can enable an "only-new" flag
    which prevents the modification of existing content. This includes the
    restriction of updating existing pages/attachments as well as deleting
    content. By default, the only-new feature is disabled with a value of
    ``False``.

    .. code-block:: python

        confluence_publish_onlynew = True

.. confval:: confluence_request_session_override

    .. versionadded:: 1.7

    A hook to manipulate a Requests_ session prepared by this extension. Allows
    users who wish to perform advanced configuration of a session for features
    which may not be supported by this extension.

    .. code-block:: python

        def my_request_session_override(session):
            session.trust_env = False

        confluence_request_session_override = my_request_session_override

.. confval:: confluence_server_auth

    An authentication handler which can be directly provided to a REST API
    request. REST calls in this extension use the Requests_ library, which
    provide various methods for a client to perform authentication. While this
    extension provides simple authentication support (via
    |confluence_server_user|_ and |confluence_server_pass|_), a publisher may
    need to configure an advanced authentication handler to support a target
    Confluence instance.

    Note that this extension does not define custom authentication handlers.
    This configuration is a passthrough option only. For more details on various
    ways to use authentication handlers, please consult
    `Requests -- Authentication`_. By default, no custom authentication handler
    is provided to generated REST API requests. An example OAuth 1 is as
    follows:

    .. code-block:: python

        from requests_oauthlib import OAuth1

        ...

        confluence_server_auth = OAuth1(client_key,
            client_secret=client_secret,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret)

.. confval:: confluence_server_cookies

    .. versionadded:: 1.2

    A dictionary value which allows a user to pass key-value cookie information
    for authentication purposes. This is useful for users who need to
    authenticate with a single sign-on (SSO) provider to access a target
    Confluence instance. By default, no cookies are set with a value of
    ``None``.

    .. code-block:: python

        confluence_server_cookies = {
            'SESSION_ID': '<session id string>',
            'U_ID': '<username>',
        }

.. confval:: confluence_version_comment

    .. versionadded:: 1.8

    A string value to be added as a comment to Confluence's version history.

    .. code-block:: python

        confluence_version_comment = 'Automatically generated.'

Advanced processing configuration
---------------------------------

.. confval:: confluence_additional_mime_types

    .. versionadded:: 1.3

    Candidate selection for images will only support the internally managed list
    of MIME types supported by a default Confluence instance. A custom
    installation or future installations of a Confluence instance may support
    newer MIME types not explicitly managed by this extension. This
    configuration provides a user the option to register additional MIME types
    to consider for image candidates.

    .. code-block:: python

        confluence_additional_mime_types = [
            'image/tiff',
        ]

.. |confluence_file_suffix| replace:: ``confluence_file_suffix``
.. _confluence_file_suffix:

.. confval:: confluence_file_suffix

    The file name suffix to use for all generated files. By default, all
    generated files will use the extension ``.conf``.

    .. code-block:: python

        confluence_file_suffix = '.conf'

    See also |confluence_file_transform|_.

.. |confluence_file_transform| replace:: ``confluence_file_transform``
.. _confluence_file_transform:

.. confval:: confluence_file_transform

    A function to override the translation of a document name to a filename. The
    provided function is used to perform translations for both Sphinx's
    get_outdated_docs_ and write_doc_ methods. The default translation will be
    the combination of "``docname`` + |confluence_file_suffix|_".

.. index:: Jira; Configuring Jira servers

.. _confluence_jira_servers:

.. confval:: confluence_jira_servers

    .. versionadded:: 1.2

    Provides a dictionary of named Jira servers to reference when using the
    ``jira`` or ``jira_issue`` directives. In a typical Confluence environment
    which is linked with a Jira instance, users do not need to take advantage of
    this configuration -- Confluence should automatically be able to link to
    respectively Jira issues or map Jira query languages with a configured Jira
    instance. In select cases where an instance has more than one Jira instance
    attached, a user may need to explicitly reference a Jira instance to
    properly render a Jira macro. Jira-related directives have the ability to
    reference Jira instances, with a combination of a UUID and name; for
    example:

    .. code-block:: rst

        .. jira_issue:: TEST-151
            :server-id: d005bcc2-ca4e-4065-8ce8-49ff5ac5857d
            :server-name: MyAwesomeJiraServer

    It may be tedious for some projects to add this information in each
    document. As an alternative, a configuration can define Jira instance
    information inside a configuration option as follows:

    .. code-block:: python

        confluence_jira_servers = {
            'server-1': {
                'id': '<UUID of Jira Instance>',
                'name': '<Name of Jira Instance>',
            }
        }

    With the above option defined in a project's configuration, the following
    can be used instance inside a document:

    .. code-block:: rst

        .. jira_issue:: TEST-151
            :server: server-1

    See also:

    - :ref:`Jira directives <jira-directives>`
    - :ref:`Jira roles <jira-roles>`

.. confval:: confluence_lang_transform

    A function to override the translation of literal block-based directive
    language values to Confluence supported code block macro language values.
    The default translation accepts `Pygments documented language types`_ to
    `Confluence-supported syntax highlight languages`_.

    .. code-block:: python

       def my_language_translation(lang):
           return 'default'

       confluence_lang_transform = my_language_translation

.. |confluence_latex_macro| replace:: ``confluence_latex_macro``
.. _confluence_latex_macro:

.. confval:: confluence_latex_macro

    .. versionadded:: 1.8

    .. note::

        Confluence does not provide stock support for LaTeX macros.

    The name of a LaTeX macro to use when wishing to render LaTeX content on
    a Confluence instance. Stock Confluence instances do not support LaTeX
    content by default. However, if an instance has installed a marketplace
    add-on that supports LaTeX, this option can be used to hint to render LaTeX
    content (such as mathematical notation) by configuring this option.

    .. code-block:: python

        confluence_latex_macro = 'macro-name'
         (or)
        confluence_latex_macro = {
            'block-macro': 'block-macro-name',
            'inline-macro': 'inline-macro-name',
            'inline-macro-param': 'inline-macro-parameter', # (optional)
        }

    The name of a LaTeX macro will vary based on which add-on is installed.
    For a list of known macro names or steps to determine the name of a
    supported macro, consult the
    :ref:`macro table/instructions <guide_math_macro_names>`
    found in the math guide.

    If this option is not set, any LaTeX content processed in a document will
    instead be converted to images using dvipng/dvisvgm (see also
    `sphinx.ext.imgmath`_ for additional information).

    See also:

    - :ref:`LaTeX directives <latex-directives>`
    - :ref:`LaTeX roles <latex-roles>`
    - :doc:`guide-math`

.. |confluence_link_suffix| replace:: ``confluence_link_suffix``
.. _confluence_link_suffix:

.. confval:: confluence_link_suffix

    The suffix name to use for generated links to files. By default, all
    generated links will use the value defined by |confluence_file_suffix|_.

    .. code-block:: python

        confluence_link_suffix = '.conf'

    See also |confluence_link_transform|_.

.. |confluence_link_transform| replace:: ``confluence_link_transform``
.. _confluence_link_transform:

.. confval:: confluence_link_transform

    A function to override the translation of a document name to a (partial)
    URI. The provided function is used to perform translations for both Sphinx's
    get_relative_uri_ method. The default translation will be the combination of
    "``docname`` + |confluence_link_suffix|_".

.. index:: Mentions

.. _confluence_mentions:

.. confval:: confluence_mentions

    .. versionadded:: 1.9

    Provides a dictionary of key-to-value mappings which can be used with
    ``confluence_mention`` roles. When defining mentions, documents can
    reference a user's account identifier, user key or username (depending
    on the Confluence instance being published to). This configuration can
    be used to swap the value mentioned in a document with a value specified
    in configuration. For example, with the following configuration:

    .. code-block:: python

        confluence_mentions = {
            'myuser':  '3c5369:fa8b5c24-17f8-4340-b73e-50d383307c59',
        }

    With a document such as follows:

    .. code-block:: rst

        For more information, contact :confluence_mention:`myuser`:

    The value ``myuser`` will be replaced with the configured account
    identifier. This can be useful for when trying to manage multiple
    user's account identifiers when targeting a Confluence Cloud instance,
    as well as providing a quick-way to swap a generic contact role which
    may change over time.

    See also:

    - :ref:`Mention roles <mention-roles>`

.. confval:: confluence_navdocs_transform

    .. versionadded:: 1.7

    A function to override the document list used for populating navigational
    buttons generated from a |confluence_prev_next_buttons_location|_
    configuration. This can be helpful in advanced publishing cases where a user
    would like ignore or re-order select pages from navigation, or even
    reference pages outside of documentation list.

    .. code-block:: python

        def my_navdocs_transform(builder, docnames):
            # override and return a new docnames list
            return docnames

       confluence_navdocs_transform = my_navdocs_transform

    See also |confluence_prev_next_buttons_location|_.

.. |confluence_remove_title| replace:: ``confluence_remove_title``
.. _confluence_remove_title:

.. confval:: confluence_remove_title

    A boolean value to whether or not automatically remove the title section
    from all published pages. In Confluence, page names are already presented at
    the top. With this option enabled, this reduces having two leading headers
    with the document's title. In some cases, a user may wish to not remove
    titles when custom prefixes or other custom modifications are in play. By
    default, this option is enabled with a value of ``True``.

    .. code-block:: python

        confluence_remove_title = True

    See also:

    - |confluence_disable_autogen_title|_
    - |confluence_title_overrides|_

Deprecated options
------------------

.. confval:: confluence_master_homepage

    .. versionchanged:: 1.6

    This option has been renamed to |confluence_root_homepage|_.

.. confval:: confluence_parent_page_id_check

    .. versionchanged:: 1.9

        The |confluence_parent_page|_ option now accepts both a page name and
        identifier.

    The page identifier check for |confluence_parent_page|_. By providing an
    identifier of the parent page, both the parent page's name and identifier
    must match before this extension will publish any content to a Confluence
    instance. This serves as a sanity-check configuration for the cautious.

    .. code-block:: python

        confluence_parent_page_id_check = 123456

    See also |confluence_parent_page|_.

.. confval:: confluence_publish_subset

    .. versionchanged:: 1.3

    This option has been renamed to |confluence_publish_allowlist|_.

.. confval:: confluence_purge_from_master

    .. versionchanged:: 1.6

    This option has been renamed to |confluence_purge_from_root|_.

.. confval:: confluence_space_name

    .. versionchanged:: 1.7

    This option has been renamed to |confluence_space_key|_.

.. references ------------------------------------------------------------------

.. _API tokens: https://confluence.atlassian.com/cloud/api-tokens-938839638.html
.. _Confluence-supported syntax highlight languages: https://confluence.atlassian.com/confcloud/code-block-macro-724765175.html
.. _Key of the space: https://support.atlassian.com/confluence-cloud/docs/choose-a-space-key/
.. _Pygments documented language types: http://pygments.org/docs/lexers/
.. _Requests -- Authentication: https://requests.readthedocs.io/en/stable/user/authentication/
.. _Requests SSL Cert Verification: https://requests.readthedocs.io/en/stable/user/advanced/#ssl-cert-verification
.. _Requests: https://pypi.python.org/pypi/requests
.. _Sphinx configurations: https://www.sphinx-doc.org/en/master/usage/configuration.html
.. _TLS/SSL wrapper for socket object: https://docs.python.org/3/library/ssl.html#ssl.create_default_context
.. _Using Personal Access Tokens: https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html
.. _api_tokens: https://confluence.atlassian.com/cloud/api-tokens-938839638.html
.. _get_outdated_docs: https://www.sphinx-doc.org/en/master/extdev/builderapi.html#sphinx.builders.Builder.get_outdated_docs
.. _get_relative_uri: https://www.sphinx-doc.org/en/master/extdev/builderapi.html#sphinx.builders.Builder.get_relative_uri
.. _root_doc: https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-root_doc
.. _sphinx-build: https://www.sphinx-doc.org/en/master/man/sphinx-build.html
.. _sphinx.ext.imgmath: https://www.sphinx-doc.org/en/master/usage/extensions/math.html#module-sphinx.ext.imgmath
.. _toctree: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-toctree
.. _write_doc: https://www.sphinx-doc.org/en/master/extdev/builderapi.html#sphinx.builders.Builder.write_doc
