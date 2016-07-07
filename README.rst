.. -*- restructuredtext -*-

=======================================
Atlassian Confluence Builder for Sphinx
=======================================

Sphinx_ extension to build Confluence Wiki markup formatted files.


Requirements
============

* Sphinx_ 1.0 or later
* Python 2.6 or later

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

    sphinx-build -b confluence -c . build/confluence

Configuration
=============

The following four configuration variables are defined by sphinxcontrib.restbuilder:

.. confval:: confluence_file_suffix

   This is the file name suffix for generated files.  The default is
   ``".conf"``.

.. confval:: confluence_link_suffix

   Suffix for generated links to files.  The default is whatever
   :confval:`confluence_file_suffix` is set to.

.. confval:: confluence_file_transform

   Function to translate a docname to a filename. 
   By default, returns `docname` + :confval:`confluence_file_suffix`.

.. confval:: confluence_link_transform

   Function to translate a docname to a (partial) URI. 
   By default, returns `docname` + :confval:`confluence_link_suffix`.

Credit
======

Original credit to Freek Dijkstra <software@macfreek.nl> for the ReSTBuilder module.

Further Reading
===============

.. _Sphinx: http://sphinx-doc.org/
