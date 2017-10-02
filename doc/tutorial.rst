tutorial
========

After :doc:`installing <install>` Atlassian Confluence Builder for Sphinx, a
Sphinx project can be configured to support a ``confluence`` builder. The
following tutorial will provide a series of steps which will:

* Allow a builder to generate Confluence-compatible markup documentation.
* Allow a builder to publish to a Confluence instance.

.. tip::

    If starting without an existing Sphinx-based documentation, open a terminal
    to the location where documentation should be generated and invoke the
    following to generate a new documentation project:

    .. code-block:: shell

        sphinx-quickstart
            (or)
        python -m sphinx.quickstart

Enable the new builder by adding the new extension to the target project's
Sphinx configuration (``conf.py``):

.. code-block:: python

    extensions = ['sphinxcontrib.confluencebuilder']

Next, include a series of publish-related settings to the configuration file:

.. code-block:: python

    confluence_publish = True
    confluence_space_name = 'TEST'
    confluence_parent_page = 'Documentation'
    confluence_server_url = 'https://intranet-wiki.example.com'
    confluence_server_user = 'username'
    confluence_server_pass = 'password'

Make appropriate changes to the above configuration for the environment being
prepared. The configuration ``confluence_parent_page`` should be supplied with
the name of the page to append published documents. If omitted, the builder will
publish documents in the root of the space.

.. tip::

    For additional configuration options, consult
    :doc:`all configuration options <configuration>`.

Invoke Sphinx with the ``confluence`` builder to perform building/publishing:

    .. code-block:: shell

        make confluence
            (or)
        sphinx-build -b confluence . _build/confluence
            (or)
        python -m sphinx -b confluence . _build/confluence

Documentation of the project should now be published to the Confluence site.
