tutorial
========

After :doc:`installing <install>` Atlassian Confluence Builder for Sphinx, a
Sphinx project can be configured to support the ``confluence`` builder. The
following tutorial will provide a series of steps which will:

* Enables a builder to generate Confluence-compatible markup documentation.
* Enables a builder to publish to a Confluence instance.

----

.. contents:: :local:

new documentation
-----------------

If starting without an existing Sphinx-based documentation, one can create a
minimalistic Sphinx configuration or use Sphinx's quick-start utility.

quick-start
^^^^^^^^^^^

If opting for the quick-start utility, open a terminal to the location where
documentation should be generated and invoke the following:

   .. code-block:: shell

       sphinx-quickstart
           (or)
       python -m sphinx.quickstart

After completing the quick-start, ``conf.py`` can be tweaked as desired.
Continue preparing this project's configuration by consulting the
`existing documentation`_ steps (below).

minimalistic
^^^^^^^^^^^^

For a minimalistic setup, create a new folder for the new documentation and
configuration to be used. Create a document named ``contents.rst`` with the
following content:

.. code-block:: rst

   my documentation
   ================

   This is a test document.

Next, create a configuration file with the following information:

.. code-block:: python

   # -*- coding: utf-8 -*-

   extensions = ['sphinxcontrib.confluencebuilder']

After preparing these assets, consult the `existing documentation`_ steps
(below) to complete the configuration.

existing documentation
----------------------

Enable this extension's builder by adding the extension to the target project's
Sphinx configuration (``conf.py``):

.. code-block:: python

   extensions = ['sphinxcontrib.confluencebuilder']

Next, include a series of publish-related settings to the configuration file:

.. code-block:: python

   confluence_publish = True
   confluence_space_name = 'TEST'
   # (for confluence cloud)
   confluence_server_url = 'https://example.atlassian.net/wiki'
   confluence_server_user = 'myawesomeuser@example.com'
   confluence_server_pass = 'myapikey'
   # (or for confluence server)
   confluence_server_url = 'https://intranet-wiki.example.com'
   confluence_server_user = 'myawesomeuser'
   confluence_server_pass = 'mypassword'

Make appropriate changes to the above configuration for the environment being
targeted.

.. tip::

   For more information on the above or additional configuration options,
   consult :doc:`all configuration options <configuration>`.

If one wishes to publish documents as children of a parent page inside a space,
the configuration ``confluence_parent_page``
(:ref:`jump<confluence_parent_page>`) should be supplied with the name of the
page to append published documents. If omitted, the builder will publish
documents in the root of the space. For example:

.. code-block:: python

   confluence_parent_page = 'MyDocumentation'

To process and publish the documentation set, invoke Sphinx with the
``confluence`` builder to perform building/publishing:

   .. code-block:: shell

       make confluence
           (or)
       sphinx-build -b confluence . _build/confluence
           (or)
       python -m sphinx -b confluence . _build/confluence

Documentation of the project should now be published to the Confluence site.
