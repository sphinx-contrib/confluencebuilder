Roles
=====

The following outlines additional `roles`_ supported by this extension.

.. _jira-roles:

Jira
----

The following roles can be used to help include Jira macros into generated
Confluence documents.

.. index:: Jira; Adding a single Jira link (role)

.. rst:role:: jira

    .. versionadded:: 1.7

    The ``jira`` role allows a user to build an inlined Jira macro to be
    configured with a provided Jira key. For example:

    .. code-block:: rst

        See :jira:`TEST-123` for more details.

    See also :ref:`Jira directives <jira-directives>`.

.. references ------------------------------------------------------------------

.. _roles: https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html
