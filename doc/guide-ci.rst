.. _tip_manage_publish_subset:

.. index:: Continuous integration

Publishing with CI
==================

.. note::

    If running in a ``tox``/``virtualenv`` setup, ensure any environment
    variables used are configured to be passed through to the virtual
    environment.

.. tip::

    As of v1.9, this extension can automatically accept configuration options
    from the environment that have not been explicitly set in ``conf.py`` or
    provided by the command line. For example, to configure for
    authentication using a personal access token using the environment, do
    not add ``confluence_publish_token`` into ``conf.py`` and ensure the
    ``CONFLUENCE_PUBLISH_TOKEN`` environment variable is set.

For users performing automatic publishing through a CI system, they may wish to
authenticate their publish event with a secret key. A common approach to
applying a secret key is through an environment variable. For example, if
authenticating with an API key (see `API tokens`_), the following can be used:

.. code-block:: python

    import os

    ...

    confluence_server_user = 'api-key-uid'
    confluence_server_pass = os.getenv('SECRET_KEY')

Or, if using a personal access token (see `Using Personal Access Tokens`_),
the following can be used:

.. code-block:: python

    import os

    ...

    confluence_publish_token = os.getenv('SECRET_KEY')

Both examples above will read an environment variable ``SECRET_KEY`` prepared
in a CI environment to be used for authentication.

See ``confluence_server_pass`` (:ref:`ref<confluence_server_pass>`) and
``confluence_publish_token`` (:ref:`ref<confluence_publish_token>`) for more
information.


.. references ------------------------------------------------------------------

.. _API tokens: https://confluence.atlassian.com/cloud/api-tokens-938839638.html
.. _Using Personal Access Tokens: https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html
