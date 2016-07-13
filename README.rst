.. -*- restructuredtext -*-

=======================================
Atlassian Confluence Builder for Sphinx
=======================================

Sphinx_ extension to build Confluence Wiki markup formatted files and optionally publish them to a Confluence server.


Requirements
============

* Sphinx_ 1.0 or later
* Python 2.7 or later
* 'Confluence' PyPi package, 0.1 or later (if publishing')

Installing
==========

Using pip
---------

    pip install sphinxcontrib-confluencebuilder

Manual
------

    git clone https://github.com/tonybaloney/sphinxcontrib-confluencebuilder
    cd sphinxcontrib-confluencebuilder
    python setup.py install

If you want to take a look and have a try, you can put the builder in
an extension subdirectory, and adjust ``sys.path`` to tell Sphinx where to
look for it:

- Add the extensions directory to the path in ``conf.py``. E.g.

    sys.path.append(os.path.abspath('exts'))

Usage
=====

- Set the builder as a extension in ``conf.py``:

    extensions = ['sphinxcontrib.confluencebuilder']

- Run sphinx-build with target ``confluence``:

    sphinx-build -b confluence -d _build/doctrees   . _build/html -E -a

Configuration
=============

The following four configuration variables are defined by sphinxcontrib.confluencebuilder:

confluence_file_suffix
----------------------

This is the file name suffix for generated files.  The default is
``".conf"``.

confluence_link_suffix
----------------------

Suffix for generated links to files.  The default is whatever
:confval:`confluence_file_suffix` is set to.

confluence_file_transform
-------------------------

Function to translate a docname to a filename. 
By default, returns `docname` + :confval:`confluence_file_suffix`.

confluence_link_transform
-------------------------

Function to translate a docname to a (partial) URI. 
By default, returns `docname` + :confval:`confluence_link_suffix`.

Publishing to Confluence
========================

After installing the `confluence` pip module, you can publish to a confluence server as part of the Sphinx build. Configure `conf.py`, with the URL of your confluence server, the username and password.
You will need to enable the Remote XMLRPC API in Confluence.

In `conf.py` update the following values

confluence_publish
------------------

Function to translate a docname to a (partial) URI. 
By default, is False.

confluence_space_name
---------------------

key of the space in confluence you want to publish the docs to

You can also publish to a page within a space by using the `confluence_parent_page` configuration value with the name of the root page.

confluence_parent_page
----------------------

The root page to put the generated pages under
   
confluence_server_url
---------------------

The URL for confluence (not including the API folder)

confluence_server_user
----------------------

Your username for confluence

confluence_server_pass
----------------------

Your password for confluence

Example `conf.py`

.. code-block:: python

    extensions = ['sphinxcontrib.confluencebuilder']
    confluence_publish = True
    confluence_space_name = 'TEST'
    confluence_parent_page = 'Documentation'
    confluence_server_url = 'https://me.docs.com'
    confluence_server_user = 'anthony.shaw'
    confluence_server_pass = 'NotMyPassword!'

Supported meta types
====================

* Headings
* Paragraphs
* Enumerated lists
* Bulletted lists
* Code blocks (uses the Confluence code macro)
* Hyperlinks
* Inline blocks
* TOC Tree - But only with a Max Depth of 1, sub anchors will not be valid links.
* Tables

Unsupported meta types
======================

* Images (will get around to this!)

Credit
======

Original credit to Freek Dijkstra <software@macfreek.nl> for the ReSTBuilder module.

Further Reading
===============

.. _Sphinx: http://sphinx-doc.org/
