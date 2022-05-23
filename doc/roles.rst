Roles
=====

The following outlines additional `roles`_ supported by this extension.

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


.. references ------------------------------------------------------------------

.. _Confluence mentions: https://support.atlassian.com/confluence-cloud/docs/mention-a-person-or-team/
.. _roles: https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html
