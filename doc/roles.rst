Roles
=====

The following outlines additional `roles`_ supported by this extension.

.. index:: Macros; Emoticon Macro (role)
.. index:: Emoticon Macro

Emoticon Macro
--------------

The following role can be used to help include Confluence emoticon macros into
generated Confluence documents.

.. rst:role:: confluence_emoticon

    .. versionadded:: 1.9

    The ``confluence_emoticon`` role allows a user to build inlined emoticon
    macros. For example:

    .. code-block:: rst

        :confluence_emoticon:`tick`: This is done.

        :confluence_emoticon:`cross`: This is incomplete.

.. index:: Macros; Jira Macro (role)
.. _jira-roles:

Jira
----

The following role can be used to help include Jira macros into generated
Confluence documents.

.. index:: Jira; Adding a single Jira link (role)

.. rst:role:: jira

    .. versionadded:: 1.7

    The ``jira`` role allows a user to build an inlined Jira macro to be
    configured with a provided Jira key. For example:

    .. code-block:: rst

        See :jira:`TEST-123` for more details.

See also :ref:`Jira directives <jira-directives>`.

.. index:: Macros; LaTeX Macro (role)
.. index:: LaTeX Macro; Adding inlined LaTeX (role)
.. _latex-roles:

LaTeX
-----

.. note::

    LaTeX support requires dvipng/dvisvgm to be installed on system; however,
    if a Confluence instance supports a LaTeX macro, the
    ``confluence_latex_macro`` (:ref:`ref<confluence_latex_macro>`) option can
    be used instead. For more information, please read :doc:`guide-math`.

The following role can be used to help include LaTeX content into generated
Confluence documents.

.. rst:role:: confluence_latex

    .. versionadded:: 1.8

    The ``confluence_latex`` role allows a user to build inlined LaTeX
    content. For example:

    .. code-block:: rst

        This is a :confluence_latex:`$\\mathfrak{t}$est`.

See also :ref:`LaTeX directives <latex-directives>`.

.. index:: Macros; Mentions Macro (role)
.. index:: Mentions; Macro (role)
.. _mention-roles:

Mentions
--------

The following role can be used to help include `Confluence mentions`_ into
generated Confluence documents.

.. rst:role:: confluence_mention

    .. versionadded:: 1.9

    .. warning::

        Confluence Cloud mentions should always use account identifiers; where
        Confluence Server mentions should use either usernames or user keys.
        Attempting to use Confluence Cloud account identifiers when
        publishing to a Confluence server will most likely result in an
        "Unsupported Confluence API call" error (500).

    The ``confluence_mention`` role allows a user to build inlined mentions.
    For Confluence Cloud instances, a mention to a specific user's account
    identifier would be defined as follows:

    .. code-block:: rst

        See :confluence_mention:`3c5369:fa8b5c24-17f8-4340-b73e-50d383307c59`.

    For Confluence Server instances, a mention to a specific user can either
    be set to the username value, or a user's key value:

    .. code-block:: rst

        For more information, contact :confluence_mention:`myuser`.
         (or)
        Contact :confluence_mention:`b9aaf35e80441f415c3a3d3c53695d0e` for help.

    A user mapping table can also be configured using the
    ``confluence_mentions`` (:ref:`ref<confluence_mentions>`) option.

.. index:: Smart links; Roles
.. _smart-link-roles:

Smart links
-----------

.. note::

    Smart links will only render when using the v2 editor
    (see ``confluence_editor``; :ref:`ref<confluence_editor>`).

Support for inlined smart links can be created using the following roles.

.. rst:role:: confluence_doc

    .. versionadded:: 2.1

    The ``confluence_doc`` role allows a user to define an inlined link to a
    document that is styled with a card appearance. The role accepts the
    name of a document in an absolute or relative fashion (in the same manner
    as Sphinx's `:doc: <role-doc_>`_ role). For example:

    .. code-block:: rst

        See :confluence_doc:`my-other-page`.

.. rst:role:: confluence_link

    .. versionadded:: 2.1

    The ``confluence_link`` role allows a user to define an inlined link to a
    page that is styled with a card appearance. The role accepts a URL.
    How Confluence renders the context of a link card will vary based on
    which link targets Confluence supports. For example:

    .. code-block:: rst

        See :confluence_link:`https://example.com`.

See also :ref:`smart link directives <smart-link-directives>`.

.. index:: Macros; Status Macro (role)
.. index:: Status Macro

Status Macro
------------

The following role can be used to help include `Confluence status macro`_ into
generated Confluence documents.

.. rst:role:: confluence_status

    .. versionadded:: 1.9

    The ``confluence_status`` role allows a user to build inlined status
    macros. For example:

    .. code-block:: rst

        :confluence_status:`My Status`

    The color of a status macro can be configured to a value supported by
    Confluence's status macro. For example, to adjust the status value to
    a yellow color, the following can be used:

    .. code-block:: rst

        :confluence_status:`WARNING <yellow>`

    To tweak the style of a status macro to an outlined variant (if supported
    by the configured Confluence editor), adjust the color enclosure to
    square brackets:

    .. code-block:: rst

        :confluence_status:`PASSED [green]`

.. index:: Strikethrough (role)

Strikethrough
-------------

.. note::

    This role can be used to help a user observe the ability to strikethrough
    text on a Confluence page; however, this role only applies to Confluence
    builders. Users attempting to support multiple builders (such as the
    ``html`` builder), are recommended to use a ``class`` hint instead. This
    extension supports an applied ``strike`` class on text as an indication
    that the text should have a strikethrough format. For example:

    .. code-block:: rst

        .. role:: strike
            :class: strike

        This is a :strike:`strikeme` example.

The following role can be used to explicitly define strikethrough text into
generated Confluence documents.

.. rst:role:: confluence_strike

    .. versionadded:: 2.1

    The ``confluence_strike`` role allows a user to build inlined text that has
    been styled with a strikethrough. For example:

    .. code-block:: rst

        :confluence_strike:`My text`


.. references ------------------------------------------------------------------

.. _Confluence mentions: https://support.atlassian.com/confluence-cloud/docs/mention-a-person-or-team/
.. _Confluence status macro: https://support.atlassian.com/confluence-cloud/docs/insert-the-status-macro/
.. _role-doc: https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#role-doc
.. _roles: https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html
