Other
=====

The follow shows a uncategorized markup defined in reStructuredText and/or
Sphinx handled by the Sphinx engine.

.. contents::
    :local:

Attribution (in block quote)
----------------------------

When a reStructuredText `block quote`_ contains an attribution, the content
will be captured inside a Confluence quote block:

    "It is my business to know things.  That is my trade."

    -- Sherlock Holmes

Epigraph, highlight and pull-quote
----------------------------------

reStructuredText's `epigraphs`_, `highlights`_ and `pull-quotes`_ should be
captured inside a Confluence quote block:

.. epigraph::

    No matter where you go, there you are.

    -- Buckaroo Banzai

.. highlights::

    No matter where you go, there you are.

    -- Buckaroo Banzai

.. pull-quote::

    No matter where you go, there you are.

    -- Buckaroo Banzai

Manual Page
-----------

Sphinx's `manpage`_ should build off the configured ``manpages_url`` value:

:manpage:`ls(1)`

Transition
----------

A `transition`_ (or horizontal rule) can be used to seperate content.

----

This is more content.

.. references ------------------------------------------------------------------

.. _block quote: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#block-quotes
.. _epigraphs: https://docutils.sourceforge.io/docs/ref/rst/directives.html#epigraph
.. _highlights: https://docutils.sourceforge.io/docs/ref/rst/directives.html#highlights
.. _manpage: https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#role-manpage
.. _pull-quotes: https://docutils.sourceforge.io/docs/ref/rst/directives.html#pull-quote
.. _transition: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#transitions
