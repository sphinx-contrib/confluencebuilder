Single Sign-On (SSO) and OAuth Environments
===========================================

A percentage of extension users may be trying to operate with a
Confluence instance which deploys some sort of single sign-on (SSO) or
OAuth capability. How an instance is configured and the means to interact
can vary per organization, even per instance. There are no definitive steps
for configuring this extension to guarantee a graceful setup. That being
said, there should be a means to allow interaction when using this extension.
This guide may be useful for users configuring this extension for the first
time in a corporate environment.

Confluence Authentication Token
-------------------------------

Users should be using either an API token (Confluence Cloud) or personal access
token (PAT; Confluence Data Center) for authenticating with Confluence.
This means that :lref:`confluence_api_token` (along with
:lref:`confluence_server_user`) should be used in a Confluence Cloud
setting, and :lref:`confluence_publish_token` should be used in a Confluence
Data Center setting (e.g. corporate/self-hosted).

Initial Test
------------

Once a token has been configured, it is recommended to perform a connection
attempt. This is to help ensure a project configuration and extension is
ready to perform interaction with a Confluence instance, as well as to
perform a sanity check that additional SSO/OAuth configuration is required.

From the working directory of a project, perform a
:ref:`connection test <confluence_connection_troubleshooting>`:

.. code-block:: shell-session

    $ python -m sphinxcontrib.confluencebuilder connection-test
    Fetching configuration information...
    ...

Configuring for Identity or Authorization Instance
--------------------------------------------------

This extension uses Requests_ for HTTP requests. Options are available to
help allow a user tailor requests. These options can be used to inject
additional token/session information in a request required for a front-end
of a Confluence instance.

The following options may help:

- :lref:`confluence_publish_headers`: Used to set HTTP headers for
  requests made to a Confluence instance.
- :lref:`confluence_server_cookies`: Used to provide cookie data for
  requests made to a Confluence instance.
- :lref:`confluence_server_auth`: Used to provide a custom Requests-capable
  authentication handler for requests made to a Confluence instance.

Which option and values to use will vary. It is recommended, if available,
to refer to any documentation provided by the Confluence instance about
what setup is used and what header/cookie data they expect. If no such
information is available, it is recommended to either create a ticket with
the service desk associated with the Confluence instance or talk with a
system administrator for the Confluence instance.

Additional information
----------------------

- To help debug the network traffic between this extension and a Confluence
  instance, the :lref:`confluence_publish_debug` option may be used.
- Refer to `connection-issused issues`_ reported by users.

.. references ------------------------------------------------------------------

.. _Requests: https://requests.readthedocs.io/
.. _connection-issused issues: https://github.com/sphinx-contrib/confluencebuilder/issues?q=label%3Aconnection-issues
