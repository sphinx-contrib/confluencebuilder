.. -*- restructuredtext -*-

=======================================
Atlassian Confluence Builder for Sphinx
=======================================

.. image:: https://img.shields.io/pypi/v/sphinxcontrib-confluencebuilder.svg
        :target: https://pypi.python.org/pypi/sphinxcontrib-confluencebuilder

.. image:: https://img.shields.io/travis/tonybaloney/sphinxcontrib-confluencebuilder.svg
        :target: https://travis-ci.org/tonybaloney/sphinxcontrib-confluencebuilder

Sphinx_ extension to build Confluence Wiki markup formatted files and optionally
publish them to a Confluence server.

Requirements
============

* Python_ 2.7, 3.3, 3.4, 3.5 or 3.6
* Requests_
* Sphinx_ 1.0 or later

If publishing:

* Confluence_ 4.0 or later

Installing
==========

Using pip
---------

    pip install sphinxcontrib-confluencebuilder

Manual
------

.. code-block:: bash

    git clone https://github.com/tonybaloney/sphinxcontrib-confluencebuilder
    cd sphinxcontrib-confluencebuilder
    python setup.py install

If you want to take a look and have a try, you can put the builder in an
extension sub-directory, and adjust ``sys.path`` to tell Sphinx where to look
for it:

- Add the extensions directory to the path in ``conf.py``. E.g.

    sys.path.append(os.path.abspath('exts'))

Usage
=====

- Set the builder as an extension in ``conf.py``:

    extensions = ['sphinxcontrib.confluencebuilder']

- Run sphinx-build with the builder ``confluence``:

    sphinx-build -b confluence -d _build/doctrees . _build/html -E -a

Configuration
=============

The following is an example of simple configuration for Confluence generation
and publishing:

.. code-block:: python

    extensions = ['sphinxcontrib.confluencebuilder']
    confluence_publish = True
    confluence_space_name = 'TEST'
    confluence_parent_page = 'Documentation'
    confluence_server_url = 'https://intranet-wiki.example.com'
    confluence_server_user = 'username'
    confluence_server_pass = 'password'

Generic Configuration
---------------------

The following can be used to configure markup generated files:

confluence_file_suffix
~~~~~~~~~~~~~~~~~~~~~~

This is the file name suffix for generated files. By default, ``.conf``.

confluence_link_suffix
~~~~~~~~~~~~~~~~~~~~~~

Suffix for generated links to files. By default, the value of
``confluence_file_suffix``.

confluence_file_transform
~~~~~~~~~~~~~~~~~~~~~~~~~

Function to translate a docname to a filename. By default, "``docname`` +
``confluence_file_suffix``".

confluence_link_transform
~~~~~~~~~~~~~~~~~~~~~~~~~

Function to translate a docname to a (partial) URI. By default, "``docname`` +
``confluence_link_suffix``".

confluence_header_file
~~~~~~~~~~~~~~~~~~~~~~

The name of the file to use header data.

confluence_footer_file
~~~~~~~~~~~~~~~~~~~~~~

The name of the file to use footer data.

Publishing Configuration
------------------------

With a Confluence URL and authentication information, the Sphinx build process
will publish pages to the configured Confluence server. By default, this
extension will attempt to publish content using Confluence's REST API (if
available). The process will fallback to using Confluence's XML-RPC API (if
enabled/available).

The following is a list of publishing configuration options:

confluence_publish
~~~~~~~~~~~~~~~~~~

Whether or not to allow publishing. This must be explicitly set to `True` if one
wishes to publish content. By default, is ``False``.

confluence_publish_prefix
~~~~~~~~~~~~~~~~~~~~~~~~~

Insert a prefix into published document's titles and their respective links.
By default, there is no prefix.

confluence_space_name
~~~~~~~~~~~~~~~~~~~~~

Key of the space in Confluence you want to publish the generated documents to.

confluence_parent_page
~~~~~~~~~~~~~~~~~~~~~~

The root page found inside the configured space (``confluence_space_name``)
where published pages will be a descendant of.

confluence_purge
~~~~~~~~~~~~~~~~

Whether or not to purge legacy pages detected in a parent page. By default, is
``False``.

confluence_server_url
~~~~~~~~~~~~~~~~~~~~~

The URL for Confluence (not including the API folder).

confluence_server_user
~~~~~~~~~~~~~~~~~~~~~~

Your username to authenticate with the Confluence server.

confluence_server_pass
~~~~~~~~~~~~~~~~~~~~~~

Your password to authenticate with the Confluence server.

Other Configuration
-------------------

The following is a list of additional configuration options that can be applied:

confluence_parent_page_id_check
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The page identifier check for ``confluence_parent_page``. By providing an
identifier of the parent page, both the parent page's name and identifier must
match before this extension will publish any content to a Confluence server.
This serves as a sanity-check configuration for the cautious.

confluence_disable_rest
~~~~~~~~~~~~~~~~~~~~~~~

Explicitly disable any REST API calls. By default, is ``False``.

confluence_disable_xmlrpc
~~~~~~~~~~~~~~~~~~~~~~~~~

Explicitly disable any XML-RPC API calls. By default, is ``False``.

confluence_proxy
~~~~~~~~~~~~~~~~

Provide your network's proxy to access the Confluence server (only applies to
XML-RPC API calls).

confluence_timeout
~~~~~~~~~~~~~~~~~~

Force a timeout (in seconds) value for network interaction.

Supported Markup
================

* Bulleted Lists
* Code Blocks
* Enumerated Lists
* Headings
* Hyperlinks
* Inline Blocks
* Paragraphs
* Tables
* TOC Tree (maximum depth of one)


.. _Confluence: https://www.atlassian.com/software/confluence
.. _Python: https://www.python.org/
.. _Requests: https://pypi.python.org/pypi/requests
.. _Sphinx: http://sphinx-doc.org/
