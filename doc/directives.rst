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

Common
------

.. index:: Macros; Expand Macro (directive)
.. index:: Expand Macro

.. rst:directive:: confluence_expand

    .. versionadded:: 1.3

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

.. _confluence_metadata:

.. rst:directive:: confluence_metadata

    .. versionadded:: 1.3

    The ``confluence_metadata`` directive allows a user to define metadata
    information to be added during a publish event. This directive supports the
    following options:

    .. rst:directive:option:: labels: value
        :type: space separated strings

        A space-separated list of label strings to apply to a page. The
        following example will result in the labels ``label-a`` and ``label-b``
        being added to the document which defines this directive.

        .. code-block:: rst

            .. confluence_metadata::
                :labels: label-a label-b

    See also ``confluence_global_labels``
    (:ref:`ref<confluence_global_labels>`).

.. rst:directive:: confluence_newline

    .. versionadded:: 1.7

    The ``confluence_newline`` directive supports the injection of a newline
    in a document where seperation may be desired between inlined elements.

    .. code-block:: rst

        .. confluence_newline::

.. rst:directive:: confluence_toc

    .. versionadded:: 1.9

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

.. index:: Macros; Jira Macro (directive)
.. _jira-directives:

Jira
----

The following directives can be used to help include Jira macros into generated
Confluence documents.

.. index:: Jira; Adding a Jira table

.. rst:directive:: .. jira:: [jql]

    .. versionadded:: 1.2

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

        Indicates a named Jira server provided via ``confluence_jira_servers``
        (:ref:`ref<confluence_jira_servers>`). When set, options ``server-id``
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


.. index:: Jira; Adding a single Jira link (directive)

.. rst:directive:: .. jira_issue:: [issue-id]

    .. versionadded:: 1.2

    The ``jira_issue`` directive allows a user to build a Jira macro to be
    configured with a provided Jira key. For example:

    .. code-block:: rst

        .. jira_issue:: TEST-123

    This directive supports the following options:

    .. rst:directive:option:: server: instance
        :type: string

        Indicates a named Jira server provided via ``confluence_jira_servers``
        (:ref:`ref<confluence_jira_servers>`). When set, options ``server-id``
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

See also :ref:`Jira roles <jira-roles>`.

.. index:: Macros; LaTeX Macro (directive)
.. index:: LaTeX Macro; Adding a LaTeX block (directive)
.. _latex-directives:

LaTeX
-----

.. note::

    LaTeX support requires dvipng/dvisvgm to be installed on system; however,
    if a Confluence instance supports a LaTeX macro, the
    ``confluence_latex_macro`` (:ref:`ref<confluence_latex_macro>`) option can
    be used instead. For more information, please read :doc:`guide-math`.

The following directive can be used to help add LaTeX content into a
Confluence page.

.. rst:directive:: .. confluence_latex::

    .. versionadded:: 1.8

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

See also :ref:`LaTeX roles <latex-roles>`.


.. references ------------------------------------------------------------------

.. _Expand Macro: https://confluence.atlassian.com/doc/expand-macro-223222352.html
.. _Sphinx's toctree directive: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#table-of-contents
.. _Table of Contents Macro: https://support.atlassian.com/confluence-cloud/docs/insert-the-table-of-contents-macro/
.. _directives: https://www.sphinx-doc.org/en/stable/usage/restructuredtext/directives.html
.. _reStructuredText's Table of Contents: https://docutils.sourceforge.io/docs/ref/rst/directives.html#table-of-contents
.. _only: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-only
