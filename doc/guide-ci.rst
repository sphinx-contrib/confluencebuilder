.. raw:: latex

    \newpage

.. _tip_manage_publish_subset:

.. index:: Continuous integration

Publishing with CI
==================

.. note::

    If running in a ``tox``/``virtualenv`` setup, ensure any environment
    variables used are configured to be passed through to the virtual
    environment.

.. caution::

    It is never recommended to store an API token or raw password into a
    committed/shared repository holding documentation. This guide should
    help ensure this is not required for users.

.. only:: latex

    .. contents::
       :depth: 1
       :local:

Documentation can be published automatically through a CI system. While users
may wish to customize a publish location or tweak title postfixes for a job,
in almost all cases, the most important options to configure are specific to
authentication (i.e. how to properly use a token to publish content without
embedded the token into source). The following will focus on how to properly
forward a token into a Sphinx configuration to allow publishing. The same
approach can be used for tailoring other Confluence configuration entries in
a CI environment.

There are three approaches that can be used to help accept a CI managed
publish token:

1) Defining an environment variable to forward into the extension.
2) Override a configuration option when invoking a Sphinx build.
3) Adding the ability to fetch configuration values from the environment
   or file with tweaks to a ``conf.py`` definition.

Before demonstrating these methods, please note which type of authentication
is required for the target Confluence instance. For example, if
authenticating with an API key (Confluence Cloud; see `API tokens`_), users
will need to configure both :lref:`confluence_server_user` and
:lref:`confluence_api_token` options. However, if using a personal
access token (see `Using Personal Access Tokens`_), users will need to
configure only the :lref:`confluence_publish_token` option.

Confluence environment variables
--------------------------------

.. versionadded:: 1.9

The Confluence builder extension accepts most configuration entries from the
environment if the option is not already set in ``conf.py``.

Confluence Cloud API Key
~~~~~~~~~~~~~~~~~~~~~~~~

If using a Confluence Cloud API key, ensure the following variables are
*not set* inside ``conf.py``:

- :lref:`confluence_api_token`
- :lref:`confluence_publish_token`
- :lref:`confluence_server_pass`

The option :lref:`confluence_server_user` may be set if a user will only ever
be published with a single API token. If the environment plans to use multiple
tokens, ensure :lref:`confluence_server_user` is not set as well.

Next, if the CI environment supports defining custom CI variables, create a
new entry for ``CONFLUENCE_API_TOKEN``, holding the API token value to use
when publishing. If the API token is stored in another manner that can be
exposed when running a build, ensure the token is set into a
``CONFLUENCE_API_TOKEN`` environment variable before running Sphinx. For
example:

.. code-block:: shell-session

    $ export CONFLUENCE_API_TOKEN="<my-token-value>"
    $ sphinx-build ...
    Running Sphinx
    ...

Or, when using a Windows command line:

.. code-block:: doscon

    > set CONFLUENCE_API_TOKEN="<my-token-value>"
    > sphinx-build ...
    Running Sphinx
    ...

The same applies to ``CONFLUENCE_SERVER_USER`` if the username field needs to
be set.

Confluence Data Center PAT
~~~~~~~~~~~~~~~~~~~~~~~~~~

If using a PAT, ensure the following variables are *not set* inside
``conf.py``:

- :lref:`confluence_api_token`
- :lref:`confluence_publish_token`
- :lref:`confluence_server_pass`
- :lref:`confluence_server_user`

Next, if the CI environment supports defining custom CI variables, create a
new entry for ``CONFLUENCE_PUBLISH_TOKEN``, holding the PAT value to use
when publishing. If the PAT is stored in another manner that can be exposed
when running a build, ensure the token is set into a
``CONFLUENCE_PUBLISH_TOKEN`` environment variable before running Sphinx. For
example:

.. code-block:: shell-session

    $ export CONFLUENCE_PUBLISH_TOKEN="<my-token-value>"
    $ sphinx-build ...
    Running Sphinx
    ...

Or, when using a Windows command line:

.. code-block:: doscon

    > set CONFLUENCE_PUBLISH_TOKEN="<my-token-value>"
    > sphinx-build ...
    Running Sphinx
    ...

Configuration overrides
-----------------------

Sphinx supports providing configuration overrides from the command line.

Confluence Cloud API Key
~~~~~~~~~~~~~~~~~~~~~~~~

The following can be used to configure an API token for Confluence Cloud:

.. code-block:: shell

    sphinx-build ... -Dconfluence_api_token="<my-token-value>"

Confluence Data Center PAT
~~~~~~~~~~~~~~~~~~~~~~~~~~

For an environment using a PAT for Confluence Data Center, a PAT can be
configured as follows:

.. code-block:: shell

    sphinx-build ... -Dconfluence_publish_token="<my-token-value>"

Manual configuration processing
-------------------------------

Users are free to use custom implementation inside their ``conf.py`` file
to help manage their configuration in a CI environment. The following shows
two examples that read an environment variable ``SECRET_KEY`` prepared
in a CI environment to be used for authentication.

Confluence Cloud API Key
~~~~~~~~~~~~~~~~~~~~~~~~

If using an API token, the following can be used:

.. code-block:: python

    import os

    ...

    confluence_server_user = 'api-key-uid'
    confluence_api_token = os.getenv('SECRET_KEY')


Confluence Data Center PAT
~~~~~~~~~~~~~~~~~~~~~~~~~~

If using a personal access token, the following can be used:

.. code-block:: python

    import os

    ...

    confluence_publish_token = os.getenv('SECRET_KEY')


.. references ------------------------------------------------------------------

.. _API tokens: https://confluence.atlassian.com/cloud/api-tokens-938839638.html
.. _Using Personal Access Tokens: https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html
