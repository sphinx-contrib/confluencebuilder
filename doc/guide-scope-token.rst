.. index:: Scoped Token

Configure access for a scoped token
===================================

.. versionadded:: 2.15

.. note::

    Scoped tokens only apply to Confluence Cloud.

Setup a scoped token
--------------------

To create a scoped token, venture to a user's API token management page:

    | API Tokens
    | https://id.atlassian.com/manage-profile/security/api-tokens

On this page:

- Select the button ``Create API token with scopes``.
- Name the API token and configure a desired expiry date.
- Select the ``Confluence`` application.
- Check each of the following scopes required for this extension:

  - ``read:space:confluence``
  - ``read:content.metadata:confluence``
  - ``read:page:confluence``
  - ``write:page:confluence``
  - ``delete:page:confluence``
  - ``read:attachment:confluence``
  - ``read:content-details:confluence``
  - ``write:attachment:confluence``
  - ``delete:attachment:confluence``
  - ``write:watcher:confluence``

- Review and create.


Configuring the extension
-------------------------

Using a scoped token requires at least one of the following two configuration
changes. The easiest option is to hint to this extension that a scoped token
is being used by configuring:

.. code-block:: python

    confluence_api_token_scoped = True

This should help automatically resolve a modern API endpoint for Confluence
interaction. Alternatively, if wanting to explicitly configure the modern API
endpoint, determine a space's Cloud identifier (if not already) by venturing
to:

.. code-block:: none

    https://<SPACE>.atlassian.net/_edge/tenant_info

For example:

.. code-block:: none

    https://example.atlassian.net/_edge/tenant_info

This page should provide a GUID value which can be used in a modern Confluence
API endpoint required for scoped tokens:

.. code-block:: python

    confluence_server_url = 'https://api.atlassian.com/ex/confluence/<GUID>/'

For example:

.. code-block:: python

    confluence_server_url = 'https://api.atlassian.com/ex/confluence/550e8400-e29b-41d4-a716-446655440000/'
