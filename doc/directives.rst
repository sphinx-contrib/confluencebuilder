Directives
==========

The following outlines additional `directives`_ supported by this extension.

Directives listed below are only supported when using this extension. For users
with documentation that is built with multiple builders, the following can be
used to restrict these directives to supported builders by using the
`:only: <only_>`_ directive. For example:

.. code-block:: rst

    .. only:: builder_confluence or builder_singleconfluence

        .. confluence_metadata::
            :labels: label-test

Alternatively, users may be interested in a third-party extension which can
help support the use of Confluence directives in other builders:

    | sphinx-confluencebuilder-bridge
    | https://github.com/adamtheturtle/sphinx-confluencebuilder-bridge

Common
------

.. index:: Macros; Excerpt Macro (directive)
.. index:: Excerpt Macro

.. rst:directive:: confluence_excerpt

    The ``confluence_excerpt`` directive allows a user to define a Confluence
    `Excerpt Macro`_ to help build snippets of content to be shared for
    other pages. For example:

    .. code-block:: rst

        .. confluence_excerpt::

            This content is reusable.

    This directive supports the following options:

    .. rst:directive:option:: atlassian-macro-output-type: output type
        :type: block, inline

        When this option is configured to ``inline`` (default), the
        rendered excerpt macro will be presented inlined with other content
        in the page (no additional line breaks). The ``block`` type can
        be used to help render an excerpt macro as a block-level element.

        .. code-block:: rst

            .. confluence_excerpt::
                :atlassian-macro-output-type: block

                This content is reusable.

    .. rst:directive:option:: hidden: flag
        :type: boolean

        Whether the macro's content should be rendered on the page that
        defines it. Valid values are ``true`` or ``false`` (default).

        .. code-block:: rst

            .. confluence_excerpt::
                :hidden: true

                This content is reusable.

    .. rst:directive:option:: name: value
        :type: string

        A name value to apply to the macros "name" field. This can be used
        to name a specific excerpt on a page, which can be explicitly mapped
        to with an excerpt-include when attempting to define multiple excerpts
        on the same page. If only a single excerpt is created, an
        excerpt-include will implicitly use the first excerpt on a page.

        .. code-block:: rst

            .. confluence_excerpt::
                :name: my-excerpt

                This content is reusable.

    .. versionadded:: 2.0

.. index:: Macros; Excerpt Include Macro (directive)
.. index:: Excerpt Include Macro

.. rst:directive:: .. confluence_excerpt_include:: [ref]

    The ``confluence_excerpt_include`` directive allows a user to define a
    Confluence `Excerpt Include Macro`_ to help include snippets of content
    provided by excerpt macro definitions. An include macro requires an
    explicit reference to the page which holds the excerpt content to load.
    Users can specify an exclamation-prefixed document name, referring to a
    local Sphinx documentation file to load an excerpt from. For example:

    .. code-block:: rst

        .. confluence_excerpt_include:: !my-excerpt-docname

    Users may also specify a known document title name that may be managed
    outside their Sphinx project set. For example:

    .. code-block:: rst

        .. confluence_excerpt_include:: Custom excerpt

    To target a page on a different space, the space name can be prefixed
    before the document title:

    .. code-block:: rst

        .. confluence_excerpt_include:: MYSPACE:Custom excerpt

    This directive supports the following options:

    .. rst:directive:option:: name: value
        :type: string

        The explicit name of the excerpt to use for a given page. If no name
        is provided, the excerpt-include macro will use the first available
        excerpt on the target page.

        .. code-block:: rst

            .. confluence_excerpt_include:: !my-excerpt-docname
                :name: my-excerpt

    .. rst:directive:option:: nopanel: flag
        :type: boolean

        Whether the macro's content should remove the panel around the
        excerpted content. Valid values are ``true`` or ``false`` (default).

        .. code-block:: rst

            .. confluence_excerpt_include:: !my-excerpt-docname
                :nopanel: true

    .. versionadded:: 2.0

.. index:: Macros; Expand Macro (directive)
.. index:: Expand Macro
.. _confluence_expand-directive:

.. rst:directive:: confluence_expand

    The ``confluence_expand`` directive allows a user to define a Confluence
    `Expand Macro`_ to help manage the visibility of content on a page. For
    example:

    .. code-block:: rst

        .. confluence_expand::

            This content is captured inside the expand macro.

    This directive supports the following options:

    .. rst:directive:option:: title: value
        :type: string

        A string value to apply to the macros "title" field.

        .. code-block:: rst

            .. confluence_expand::
                :title: View more details...

                This content is captured inside the expand macro.

    See also :doc:`guide-collapse`.

    .. versionadded:: 1.3

.. _confluence_html:

.. rst:directive:: confluence_html

    .. warning::

        The `HTML Macro`_ is disabled by default on Confluence instances.
        Using this directive is only useful for users that have instances
        where a system administrator has enabled their use.

    The ``confluence_html`` directive allows a user to define a Confluence
    `HTML Macro`_ to render HTML content on a page. For example:

    .. code-block:: rst

        .. confluence_html::

            <h1>Header</h1>

            This is an <strong>example</strong>.

    See also :lref:`confluence_permit_raw_html`.

    .. versionadded:: 2.7

.. _confluence_metadata:

.. rst:directive:: confluence_metadata

    The ``confluence_metadata`` directive allows a user to define metadata
    information to be added during a publish event. This directive supports the
    following options:

    .. rst:directive:option:: editor: value
        :type: v1, v2

        .. deprecated:: 2.14

            Support for page-specific editor overrides will be removed in 2026
            as Confluence Cloud removes support for the ``v1`` editor.

        Pages are publish with the editor type configured through the
        :lref:`confluence_editor` option. However, users can override the
        editor for a specific page using the ``editor`` metadata option.

        .. code-block:: rst

            .. confluence_metadata::
                :editor: v2

        See also :lref:`confluence_editor`.

    .. rst:directive:option:: full-width: flag
        :type: boolean

        Pages are publish with the full-width appearance configured through the
        :lref:`confluence_full_width` option. However, users can override the
        appearance for a specific page using the ``full-width`` metadata
        option.

        .. code-block:: rst

            .. confluence_metadata::
                :full-width: false

        See also :lref:`confluence_full_width`.

    .. rst:directive:option:: guid: value
        :type: string

        Assign a user-managed GUID value for a page. This value can be
        shared in a subset of :doc:`events <events>` generated by this
        extension.

    .. rst:directive:option:: labels: value
        :type: space separated strings

        A space-separated list of label strings to apply to a page. The
        following example will result in the labels ``label-a`` and ``label-b``
        being added to the document which defines this directive.

        .. code-block:: rst

            .. confluence_metadata::
                :labels: label-a label-b

        See also :lref:`confluence_global_labels`.

    .. versionadded:: 1.3
    .. versionchanged:: 2.2 Added ``editor`` and ``full-width`` support.
    .. versionchanged:: 2.8 Added ``guid`` support.

.. rst:directive:: confluence_newline

    The ``confluence_newline`` directive supports the injection of a newline
    in a document where separation may be desired between inlined elements.

    .. code-block:: rst

        .. confluence_newline::

    .. versionadded:: 1.7

.. index:: Macros; Panel Macro (directive)
.. index:: Panel Macro
.. _confluence_panel-directive:

.. rst:directive:: confluence_panel

    The ``confluence_panel`` directive allows a user to define a Confluence
    `Panel Macro`_ to help format content in a customizable colored panel
    on a page. For example:

    .. code-block:: rst

        .. confluence_panel::

            This content is captured inside the panel macro.

    This directive supports the following options:

    .. rst:directive:option:: bg-color: value
        :type: string

        A string value to apply to the macros "bgColor" field.

        .. code-block:: rst

            .. confluence_panel::
                :bg-color: #00ff00

                This content is captured inside the panel macro.

    .. rst:directive:option:: border-color: value
        :type: string

        A string value to apply to the macros "borderColor" field.

        .. code-block:: rst

            .. confluence_panel::
                :border-color: #ff0000

                This content is captured inside the panel macro.

    .. rst:directive:option:: border-style: value
        :type: string

        A string value to apply to the macros "borderStyle" field.

        .. code-block:: rst

            .. confluence_panel::
                :border-style: solid

                This content is captured inside the panel macro.

    .. rst:directive:option:: border-width: value
        :type: string

        A string value to apply to the macros "borderWidth" field.

        .. code-block:: rst

            .. confluence_panel::
                :border-width: 42

                This content is captured inside the panel macro.

    .. rst:directive:option:: title: value
        :type: string

        A string value to apply to the macros "title" field.

        .. code-block:: rst

            .. confluence_panel::
                :title: This is my title

                This content is captured inside the panel macro.

    .. rst:directive:option:: title-bg-color: value
        :type: string

        A string value to apply to the macros "titleBGColor" field.

        .. code-block:: rst

            .. confluence_panel::
                :title: my title
                :title-bg-color: #0000ff

                This content is captured inside the panel macro.

    .. rst:directive:option:: title-color: value
        :type: string

        A string value to apply to the macros "titleColor" field.

        .. code-block:: rst

            .. confluence_panel::
                :title: my title
                :title-color: #ff00ff

                This content is captured inside the panel macro.

    .. versionadded:: 2.13

.. rst:directive:: confluence_toc

    The ``confluence_toc`` directive allows a user to define a Confluence
    `Table of Contents Macro`_. Users are typically recommended to use
    `reStructuredText's Table of Contents`_ directive when generating local
    table of contents; and Confluence's Table of Contents macro is typically
    not a replacement of `Sphinx's toctree directive`_. However, if a user
    wishes to take advantage of Confluence's TOC-specific macro capabilities,
    the following can be used:

    .. code-block:: rst

        .. confluence_toc::

    This directive supports the following options:

    .. rst:directive:option:: absolute-url: flag
        :type: boolean

        Whether the macro should generate full URLs for TOC entry links.
        Valid values are ``true`` or ``false`` (default).

        .. code-block:: rst

            .. confluence_toc::
                :absolute-url: true

    .. rst:directive:option:: exclude: value
        :type: string

        Filter heading to exclude entries matching the provided value. The
        value should support a regular expressions string.

    .. rst:directive:option:: include: value
        :type: string

        Filter heading to include entries matching the provided value. The
        value should support a regular expressions string.

    .. rst:directive:option:: indent: value
        :type: string

        The indent to apply for header entries.

        .. code-block:: rst

            .. confluence_toc::
                :indent: 15px

    .. rst:directive:option:: max-level: count
        :type: number

        Defines the lowest heading level to include in the table of contents.

        .. code-block:: rst

            .. confluence_toc::
                :max-level: 10

    .. rst:directive:option:: min-level: count
        :type: number

        Defines the highest heading level to include in the table of contents.

        .. code-block:: rst

            .. confluence_toc::
                :min-level: 1

    .. rst:directive:option:: outline: flag
        :type: boolean

        Whether the macro should include outline numbering for entries.
        Valid values are ``true`` or ``false`` (default).

        .. code-block:: rst

            .. confluence_toc::
                :outline: true

    .. rst:directive:option:: printable: flag
        :type: boolean

        Whether the macro should render when a user prints a Confluence page.
        Valid values are ``true`` (default) or ``false``.

        .. code-block:: rst

            .. confluence_toc::
                :printable: true

    .. rst:directive:option:: separator: separator style type of the toc
        :type: brackets, braces, parens, <user-defined>

        When the ``type`` option is configured to ``flat``, this option can
        configure the separator type applied between header entries. By
        default, the separator type is set to ``brackets``.

        .. code-block:: rst

            .. confluence_toc::
                :separator: braces

    .. rst:directive:option:: style: list style type of the toc
        :type: default, none, disc, circle, square, decimal, lower-alpha,
               lower-roman, upper-roman

        Configures how the table of contents will be style its list type. By
        default, the style type is set to ``default``.

        .. code-block:: rst

            .. confluence_toc::
                :style: square

    .. rst:directive:option:: type: outline type of the toc
        :type: flat or list

        Configures how the table of contents will be style its structure.
        Valid values are ``flat`` or ``list`` (default).

        .. code-block:: rst

            .. confluence_toc::
                :type: flat

    .. versionadded:: 1.9

.. index:: Macros; PDF Macro (directive)
.. index:: PDF Macro
.. _confluence_viewpdf-directive:

.. rst:directive:: confluence_viewpdf

    The ``confluence_viewpdf`` directive allows a user to define a Confluence
    `PDF Macro`_ to help inline PDF files in a page. For example:

    .. code-block:: rst

        .. confluence_viewpdf:: example.pdf

    .. versionadded:: 2.14

.. index:: Macros; Jira Macro (directive)
.. _jira-directives:

Jira
----

The following directives can be used to help include Jira macros into generated
Confluence documents.

.. index:: Jira; Adding a Jira table

.. rst:directive:: .. jira:: [jql]

    The ``jira`` directive allows a user to build a Jira macro to be configured
    with a provided JQL query. For example:

    .. code-block:: rst

        .. jira:: project = "TEST"

    This directive supports the following options:

    .. rst:directive:option:: columns: value
        :type: comma separated numbers

        A comma-separated list of columns to use when displaying the macro to
        show in the Jira table.

        .. code-block:: rst

            .. jira:: project = "TEST"
                :columns: key,summary,updated,status,resolution

    .. rst:directive:option:: count: flag
        :type: boolean

        Whether the macro should display a table or just the number of issues.
        Valid values are ``true`` or ``false``.

        .. code-block:: rst

            .. jira:: project = "TEST"
                :count: true

    .. rst:directive:option:: maximum_issues: count
        :type: number

        The maximum number of issues a ``jira`` directive will display. By
        default, Confluence defaults to ``20``.

        .. code-block:: rst

            .. jira:: project = "TEST"
                :maximum_issues: 10

    .. rst:directive:option:: server: instance
        :type: string

        Indicates a named Jira server provided via
        :lref:`confluence_jira_servers`. When set, options ``server-id``
        and ``server-name`` cannot be set.

        .. code-block:: rst

            .. jira:: project = "TEST"
                :server: server-1

    .. rst:directive:option:: server-id: uuid
        :type: string

        The UUID of the Jira server to link with. When set, the option
        ``server-name`` needs to be set and the option ``server`` cannot be set.

        .. code-block:: rst
            :emphasize-lines: 2

            .. jira:: project = "TEST"
                :server-id: d005bcc2-ca4e-4065-8ce8-49ff5ac5857d
                :server-name: MyAwesomeJiraServer

    .. rst:directive:option:: server-name: name
        :type: string

        The name of the Jira server to link with. When set, the option
        ``server-id`` needs to be set and the option ``server`` cannot be set.

        .. code-block:: rst
            :emphasize-lines: 3

            .. jira:: project = "TEST"
                :server-id: d005bcc2-ca4e-4065-8ce8-49ff5ac5857d
                :server-name: MyAwesomeJiraServer

    .. versionadded:: 1.2

.. index:: Jira; Adding a single Jira link (directive)

.. rst:directive:: .. jira_issue:: [issue-id]

    The ``jira_issue`` directive allows a user to build a Jira macro to be
    configured with a provided Jira key. For example:

    .. code-block:: rst

        .. jira_issue:: TEST-123

    This directive supports the following options:

    .. rst:directive:option:: server: instance
        :type: string

        Indicates a named Jira server provided via
        :lref:`confluence_jira_servers`. When set, options ``server-id``
        and ``server-name`` cannot be set.

        .. code-block:: rst

            .. jira_issue:: TEST-123
                :server: server-1

    .. rst:directive:option:: server-id: uuid
        :type: string

        The UUID of the Jira server to link with. When set, the option
        ``server-name`` needs to be set and the option ``server`` cannot be set.

        .. code-block:: rst
            :emphasize-lines: 2

            .. jira_issue:: TEST-123
                :server-id: d005bcc2-ca4e-4065-8ce8-49ff5ac5857d
                :server-name: MyAwesomeJiraServer

    .. rst:directive:option:: server-name: name
        :type: string

        The name of the Jira server to link with. When set, the option
        ``server-id`` needs to be set and the option ``server`` cannot be set.

        .. code-block:: rst
            :emphasize-lines: 3

            .. jira_issue:: TEST-123
                :server-id: d005bcc2-ca4e-4065-8ce8-49ff5ac5857d
                :server-name: MyAwesomeJiraServer

    .. versionadded:: 1.2

See also :ref:`Jira roles <jira-roles>`.

.. index:: Macros; LaTeX Macro (directive)
.. index:: LaTeX Macro; Adding a LaTeX block (directive)
.. _latex-directives:

LaTeX
-----

.. note::

    LaTeX support requires dvipng/dvisvgm to be installed on system; however,
    if a Confluence instance supports a LaTeX macro, the
    :lref:`confluence_latex_macro` option can be used instead. For more
    information, please read :doc:`guide-math`.

The following directive can be used to help add LaTeX content into a
Confluence page.

.. rst:directive:: .. confluence_latex::

    The ``confluence_latex`` directive allows a user to add LaTeX content into
    a document. For example:

    .. code-block:: rst

        .. confluence_latex::

            $\mathfrak{H}$ello world!

    This directive supports the following options:

    .. rst:directive:option:: align: "left", "center", or "right"
        :type: string

        The alignment to apply on the LaTeX content. By default, the value is
        set to ``center``.

        .. code-block:: rst

            .. confluence_latex::
                :align: left

                $\mathfrak{H}$ello world!

    .. versionadded:: 1.8

See also :ref:`LaTeX roles <latex-roles>`.

.. index:: Smart links; Directives
.. _smart-link-directives:

Smart links
-----------

.. note::

    Smart links will only render when using the v2 editor
    (see :lref:`confluence_editor`).

.. rst:directive:: confluence_doc

    The ``confluence_doc`` directive allows a user to define a link to a
    document that is styled with a card appearance. The directive accepts the
    name of a document in an absolute or relative fashion (in the same manner
    as Sphinx's `:doc: <role-doc_>`_ role). For example:

    .. code-block:: rst

        .. confluence_doc:: my-other-page

    This directive supports the following options:

    .. rst:directive:option:: card: card type
        :type: block, embed

        When using ``block``, a smart link card is generated for the document
        link. The card will provide a summary of the target document. When
        using ``embed``, the contents of the document will rendered on the
        page.

        .. code-block:: rst

            .. confluence_doc:: my-other-page
                :card: block

    .. rst:directive:option:: layout: layout type
        :type: align-start, align-end, center, wrap-left, wrap-right

        .. note:: This option is only applicable when using an ``embed`` card.

        Specifies how an embedded card will be laid out on a page. Embedded
        cards will default to 100% width. Therefore, to take advantage of
        certain layout capabilities, users should also assign an appropriate
        width as well.

        .. code-block:: rst

            .. confluence_doc:: my-other-page
                :card: embed
                :layout: align-end
                :width: 20

    .. rst:directive:option:: width: value
        :type: integer

        .. note:: This option is only applicable when using an ``embed`` card.

        Specifies the width to apply for an embedded card. The width is a value
        from 0 to 100 (e.g. a value of ``80`` for 80% of the page).

        .. code-block:: rst

            .. confluence_doc:: my-other-page
                :card: embed
                :width: 50

    .. versionadded:: 2.1

.. rst:directive:: confluence_link

    The ``confluence_link`` directive allows a user to define a link to a
    page that is styled with a card appearance. The directive accepts a URL.
    How Confluence renders the context of a link card will vary based on
    which link targets Confluence supports. For example:

    .. code-block:: rst

        .. confluence_link:: https://example.com

    This directive supports the following options:

    .. rst:directive:option:: card: card type
        :type: block, embed

        When using ``block``, a smart link card is generated for the link.
        The card will provide a summary of the target link. When using
        ``embed``, the contents of the link will rendered on the page.

        .. code-block:: rst

            .. confluence_link:: https://example.com
                :card: block

    .. rst:directive:option:: layout: layout type
        :type: align-start, align-end, center, wrap-left, wrap-right

        .. note:: This option is only applicable when using an ``embed`` card.

        Specifies how an embedded card will be laid out on a page. Embedded
        cards will default to 100% width. Therefore, to take advantage of
        certain layout capabilities, users should also assign an appropriate
        width as well.

        .. code-block:: rst

            .. confluence_link:: https://example.com
                :card: embed
                :layout: align-end
                :width: 20

    .. rst:directive:option:: width: value
        :type: integer

        .. note:: This option is only applicable when using an ``embed`` card.

        Specifies the width to apply for an embedded card. The width is a value
        from 0 to 100 (e.g. a value of ``80`` for 80% of the page).

        .. code-block:: rst

            .. confluence_link:: https://example.com
                :card: embed
                :width: 50

    .. versionadded:: 2.1

See also :ref:`smart link roles <smart-link-roles>`.


.. references ------------------------------------------------------------------

.. _Excerpt Include Macro: https://confluence.atlassian.com/doc/excerpt-include-macro-148067.html
.. _Excerpt Macro: https://confluence.atlassian.com/doc/excerpt-macro-148062.html
.. _Expand Macro: https://confluence.atlassian.com/doc/expand-macro-223222352.html
.. _HTML Macro: https://confluence.atlassian.com/doc/html-macro-38273085.html
.. _Panel Macro: https://confluence.atlassian.com/doc/panel-macro-51872380.html
.. _PDF Macro: https://confluence.atlassian.com/doc/pdf-macro-375849180.html
.. _Sphinx's toctree directive: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#table-of-contents
.. _Table of Contents Macro: https://support.atlassian.com/confluence-cloud/docs/insert-the-table-of-contents-macro/
.. _directives: https://www.sphinx-doc.org/en/stable/usage/restructuredtext/directives.html
.. _only: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-only
.. _reStructuredText's Table of Contents: https://docutils.sourceforge.io/docs/ref/rst/directives.html#table-of-contents
.. _role-doc: https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#role-doc