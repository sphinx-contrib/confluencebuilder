Tutorial
========

.. note::

    Advanced users of Sphinx can skip this section and view
    :doc:`configuration options <configuration>` available to prepare their
    documentation.

After :doc:`installing <install>` Atlassian Confluence Builder for Sphinx, a
Sphinx project can be configured to use supported :doc:`builders <builders>`.
The following tutorial will provide a series of steps which will:

* Enables a user to generate Confluence-compatible markup documentation.
* Enables a user to publish to a Confluence instance.

New documentation
-----------------

If a user is starting a new Sphinx-based documentation, the following steps can
be used to create a new minimalistic Sphinx configuration or use Sphinx's
quick-start utility. If attempting to use this extension for existing
documentation, start `configuring for this extension <configure_extension_>`_.

Quick-start
^^^^^^^^^^^

If opting for the quick-start utility, open a terminal to the location where
documentation should be generated (typically, an empty directory) and invoke the
following:

.. code-block:: shell

    sphinx-quickstart
     (or)
    python -m sphinx.cmd.quickstart
     (or)
    python -m sphinx.quickstart

After completing the quick-start, ``conf.py`` can be tweaked as desired.
Continue preparing the documentation by
`configuring for this extension <configure_extension_>`_.

Minimalistic
^^^^^^^^^^^^

For a minimalistic setup, create a new folder for the new documentation and
configuration to be used. This is done by first creating a document named
``index.rst`` with the following content:

.. code-block:: rst

    My documentation
    ================

    This is a test document.

Next, create a configuration file ``conf.py`` with the following information:

.. code-block:: python

    # -*- coding: utf-8 -*-

    extensions = []

After preparing these files, continue by
`configuring for this extension <configure_extension_>`_ as follows.

.. _configure_extension:

Configuring to use this extension
---------------------------------

Enable this extension by registering the extension in the target project's
Sphinx configuration (``conf.py``):

.. code-block:: python

    extensions = [
        'sphinxcontrib.confluencebuilder',
    ]

Next, include a series of publish-related settings to the configuration file:

.. code-block:: python

    confluence_publish = True
    confluence_space_name = 'TEST'
    confluence_ask_password = True
    # (for Confluence Cloud)
    confluence_server_url = 'https://example.atlassian.net/wiki/'
    confluence_server_user = 'myawesomeuser@example.com'
    # (or, for Confluence Server)
    confluence_server_url = 'https://intranet-wiki.example.com/'
    confluence_server_user = 'myawesomeuser'

Make appropriate changes to the above configuration for the environment being
targeted.

.. note::

    The configuration of the space name (``confluence_space_name``) is
    case-sensitive. Ensure the value matches the case found on the Confluence
    instances (typically, uppercase).

Recommended configurations
--------------------------

By default, this extension will publish any documents to the root of a
configured space. It can be common for most users to want to publish a
documentation set as children of an already existing page. To take advantage of
this feature, a user will want to define a ``confluence_parent_page`` option in
their configuration file. For example:

.. code-block:: python

    confluence_parent_page = 'MyDocumentation'

When publishing a documentation set, the above configuration will tell this
extension to publish all documents under the ``MyDocumentation`` page.

By default, all documents published to a Confluence instance will be stored
either in the root of the space or a configured parent space (as mentioned
above). For larger documentation sets which include multiple nested documents,
it may be desired to have individual documents published as children of other
published documents. Configuring the ``confluence_page_hierarchy`` option will
allow a user to enable hierarchy support. For example:

.. code-block:: python

    confluence_page_hierarchy = True

For first time users, they may wish to sanity check what content will be
published before publishing for the first time to a Confluence instance. A user
can perform a dryrun by configuring the ``confluence_publish_dryrun`` option in
the project's configuration file. For example:

.. code-block:: python

    confluence_publish_dryrun = True

For more information on the above or additional configuration options, see
:doc:`all configuration options <configuration>`.

Building/publishing documentation
---------------------------------

To process and publish the documentation set, invoke Sphinx with the
``confluence`` builder (or a desired :doc:`builder <builders>`) to perform
building/publishing:

.. code-block:: shell

    make confluence
     (or)
    sphinx-build -b confluence . _build/confluence -E -a
     (or)
    python -m sphinx -b confluence . _build/confluence -E -a

Documentation of the project should now be published to the Confluence site.

For users who set the dryrun option above (``confluence_publish_dryrun``), they
may inspect the output of the run to confirm what the publish event will
perform. If the desired result is observed, a user can remove the dryrun option
and re-invoke the build/publish command to publish onto the configured
Confluence instance.
