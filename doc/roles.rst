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


.. references ------------------------------------------------------------------

.. _roles: https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html
