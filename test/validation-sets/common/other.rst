other
=====

The follow shows a uncategorized markup defined in reStructuredText and/or
Sphinx handled by the Sphinx engine.

.. contents::
   :local:

attribution (in block quote)
----------------------------

When a reStructuredText `block quote`_ contains an attribution, the content
will be captured inside a Confluence quote block:

   "It is my business to know things.  That is my trade."

   -- Sherlock Holmes

epigraph, highlight and pull-quote
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

transition
----------

A transition (or horizontal rule) can be used to seperate content.

----

This is my content.

.. _block quote: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#block-quotes
.. _transitions: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#transitions
.. _epigraphs: http://docutils.sourceforge.net/docs/ref/rst/directives.html#epigraph
.. _highlights: http://docutils.sourceforge.net/docs/ref/rst/directives.html#highlights
.. _pull-quotes: http://docutils.sourceforge.net/docs/ref/rst/directives.html#pull-quote
