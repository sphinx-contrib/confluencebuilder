directives
==========

The following outlines additional `directives`_ supported by this extension.

.. contents:: :local:

.. _confluence_metadata:

confluence_metadata
-------------------

The ``confluence_metadata`` directive allows a user to define metadata
information to be added during a publish event. At this time, this specifically
is for the adding of Confluence labels to pages. For example:

.. code-block:: rst

   .. confluence_metadata::
      :labels: label-a label-b

The above example will result in the labels ``label-a`` and ``label-b`` being
added to the document which defines this directive. This directive supports the
following options:

* ``labels`` *(optional)* -- A space-separated list of label strings to apply to
  a page.

See also ``confluence_global_labels`` (:ref:`jump<confluence_global_labels>`).

jira
----

The ``jira`` directive allows a user to build a JIRA macro to be configured with
a provided JQL query. For example:

.. code-block:: rst

   .. jira:: project = "TEST"
      :maximum-issues: 10

This directive supports the following options:

* ``columns`` *(optional)* -- A comma-separated list of columns to use when
  displaying the macro to show in the JIRA table. For example:
  ``key,summary,updated,status,resolution``
* ``count`` *(optional)* -- Whether the macro should display a table or just the
  number of issues. Valid values are ``true`` or ``false``.
* ``maximum_issues`` *(optional)* -- The maximum number of issues a ``jira``
  directive will display. By default, Confluence defaults to ``20``.
* ``server`` *(optional)* -- Indicates a named JIRA server provided via
  ``confluence_jira_servers`` (:ref:`jump<confluence_jira_servers>`). When set,
  options ``server-id`` and ``server-name`` cannot be set.
* ``server-id`` *(optional)* -- The UUID of the JIRA server to link with. When
  set, the option ``server-name`` needs to be set and the option ``server``
  cannot be set.
* ``server-name`` *(optional)* -- The name of the JIRA server to link with. When
  set, the option ``server-id`` needs to be set and the option ``server``
  cannot be set.

jira_issue
----------

The ``jira_issue`` directive allows a user to build a JIRA macro to be
configured with a provided JIRA key. For example:

.. code-block:: rst

   .. jira_issue:: TEST-123

This directive supports the following options:

* ``server`` *(optional)* -- Indicates a named JIRA server provided via
  ``confluence_jira_servers`` (:ref:`jump<confluence_jira_servers>`). When set,
  options ``server-id`` and ``server-name`` cannot be set.
* ``server-id`` *(optional)* -- The UUID of the JIRA server to link with. When
  set, the option ``server-name`` needs to be set and the option ``server``
  cannot be set.
* ``server-name`` *(optional)* -- The name of the JIRA server to link with. When
  set, the option ``server-id`` needs to be set and the option ``server``
  cannot be set.

.. references ------------------------------------------------------------------

.. _directives: https://www.sphinx-doc.org/en/stable/usage/restructuredtext/directives.html
