.. -*- restructuredtext -*-

=======================================
Atlassian Confluence Builder for Sphinx
=======================================

.. image:: https://img.shields.io/pypi/v/sphinxcontrib-confluencebuilder.svg
    :target: https://pypi.python.org/pypi/sphinxcontrib-confluencebuilder
    :alt: pip Version

.. image:: https://img.shields.io/travis/tonybaloney/sphinxcontrib-confluencebuilder.svg
    :target: https://travis-ci.org/tonybaloney/sphinxcontrib-confluencebuilder
    :alt: Build Status

.. image:: https://readthedocs.org/projects/sphinxcontrib-confluencebuilder/badge/?version=latest
    :target: http://sphinxcontrib-confluencebuilder.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

Sphinx_ extension to build Confluence Wiki markup formatted files and optionally
publish them to a Confluence server.

Requirements
============

* Python_ 2.7 or 3.3+
* Requests_
* Sphinx_ 1.0+

If publishing:

* Confluence_ 4.0+

Installing
==========

The recommended method to installing this extension is using pip_:

.. code-block:: shell

    pip install sphinxcontrib-confluencebuilder

For a more in-depth installation information, see also:

 | Atlassian Confluence Builder for Sphinx - Installation
 | https://sphinxcontrib-confluencebuilder.readthedocs.io/en/latest/install.html

Usage
=====

- Set the builder ``sphinxcontrib.confluencebuilder`` in the as an extension in
  ``conf.py``:

.. code-block:: python

    extensions = ['sphinxcontrib.confluencebuilder']

- Run sphinx-build with the builder ``confluence``:

.. code-block:: shell

    sphinx-build -b confluence _build/confluence -E -a
        (or)
    python -m sphinx -b confluence . _build/confluence -E -a

For more information on the usage of this extension, see also:

 | Atlassian Confluence Builder for Sphinx - Tutorial
 | https://sphinxcontrib-confluencebuilder.readthedocs.io/en/latest/tutorial.html

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

For a complete list of configuration changes, see also:

 | Atlassian Confluence Builder for Sphinx - Configuration
 | https://sphinxcontrib-confluencebuilder.readthedocs.io/en/latest/configuration.html

Demonstration
=============

The set of example documents used to assist in validation/testing can be found
here:

 | Atlassian Confluence Builder for Sphinx - Validation Set
 | https://github.com/tonybaloney/sphinxcontrib-confluencebuilder/tree/master/test/validation-set

The active and older versions of published validation documents can be found
here:

 | Atlassian Confluence Builder for Sphinx - Online Demo on Confluence Cloud
 | https://jdknight.atlassian.net/wiki/spaces/confluencebuilder/

Supported Markup
================

* Bulleted Lists
* Citations
* Code Blocks
* Definitions
* Enumerated Lists
* Footnotes
* Headings
* Hyperlinks
* Indentations
* Inline Blocks/Literals
* Paragraphs
* Tables
* TOC Tree

.. _Confluence: https://www.atlassian.com/software/confluence
.. _Python: https://www.python.org/
.. _Requests: https://pypi.python.org/pypi/requests
.. _Sphinx: http://sphinx-doc.org/
.. _pip: https://pip.pypa.io/
