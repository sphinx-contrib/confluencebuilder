.. -*- restructuredtext -*-

=======================================
Atlassian Confluence Builder for Sphinx
=======================================

.. image:: https://img.shields.io/pypi/v/sphinxcontrib-confluencebuilder.svg
   :target: https://pypi.python.org/pypi/sphinxcontrib-confluencebuilder
   :alt: pip Version

.. image:: https://travis-ci.com/sphinx-contrib/confluencebuilder.svg?branch=master
   :target: https://travis-ci.com/sphinx-contrib/confluencebuilder
   :alt: Build Status

.. image:: https://readthedocs.org/projects/sphinxcontrib-confluencebuilder/badge/?version=latest
   :target: https://sphinxcontrib-confluencebuilder.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://img.shields.io/pypi/dm/sphinxcontrib-confluencebuilder.svg
   :target: https://pypi.python.org/pypi/sphinxcontrib-confluencebuilder/
   :alt: PyPI download month

Sphinx_ extension to build Confluence storage format files and optionally
publish them to a Confluence instance.

Requirements
============

* Python_ 2.7 or 3.5+
* Requests_ 2.14.0+
* Sphinx_ 1.8+

If publishing:

* Confluence_ Cloud or Server 6.7+

Installing
==========

The recommended method to installing this extension is using pip_:

.. code-block:: shell

   pip install sphinxcontrib-confluencebuilder
    (or)
   python -m pip install sphinxcontrib-confluencebuilder

For a more in-depth installation information, see also:

 | Atlassian Confluence Builder for Sphinx - Installation
 | https://sphinxcontrib-confluencebuilder.readthedocs.io/en/latest/install.html

Usage
=====

- Register the extension ``sphinxcontrib.confluencebuilder`` in the project's
  configuration script (``conf.py``):

.. code-block:: python

   extensions = ['sphinxcontrib.confluencebuilder']

- Run sphinx-build with the builder ``confluence``:

.. code-block:: shell

   sphinx-build -b confluence . _build/confluence -E -a
    (or)
   python -m sphinx -b confluence . _build/confluence -E -a

For more information on the usage of this extension, see also:

 | Atlassian Confluence Builder for Sphinx - Tutorial
 | https://sphinxcontrib-confluencebuilder.readthedocs.io/en/latest/tutorial.html

Configuration
=============

The following is an example of a simple configuration for Confluence generation
and publishing:

.. code-block:: python

   extensions = ['sphinxcontrib.confluencebuilder']
   confluence_publish = True
   confluence_space_name = 'TEST'
   confluence_parent_page = 'Documentation'
   confluence_server_url = 'https://intranet-wiki.example.com/'
   confluence_server_user = 'username'
   confluence_server_pass = 'api-key-or-password'

For a complete list of configuration options, see also:

 | Atlassian Confluence Builder for Sphinx - Configuration
 | https://sphinxcontrib-confluencebuilder.readthedocs.io/en/latest/configuration.html

Directives
==========

For a complete list of directives supported by this extension, please consult:

 | Atlassian Confluence Builder for Sphinx - Directives
 | https://sphinxcontrib-confluencebuilder.readthedocs.io/en/latest/directives.html

Demonstration
=============

The set of example documents used to assist in validation/testing can be found
here:

 | Atlassian Confluence Builder for Sphinx - Validation Set
 | https://github.com/sphinx-contrib/confluencebuilder/tree/master/test/validation-sets

The active and older versions of published validation documents can be found
here:

 | Atlassian Confluence Builder for Sphinx - Online Demo on Confluence Cloud
 | https://jdknight.atlassian.net/wiki/spaces/confluencebuilder/

Supported Markup
================

For a complete list of supported markup, consult the following:

 | Atlassian Confluence Builder for Sphinx - Markup
 | https://sphinxcontrib-confluencebuilder.readthedocs.io/en/latest/markup.html

.. _Confluence: https://www.atlassian.com/software/confluence
.. _Python: https://www.python.org/
.. _Requests: https://pypi.python.org/pypi/requests
.. _Sphinx: https://www.sphinx-doc.org/
.. _pip: https://pip.pypa.io/
