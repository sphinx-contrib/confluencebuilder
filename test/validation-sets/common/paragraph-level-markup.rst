paragraph-level markup
======================

The following contains a series of `paragraph-level markup`_ examples (``note``
and ``warning`` directives are covered in :doc:`admonitions <admonitions>`.

First, the following shows an example of version modification-related markup
(``versionadded``, ``versionchanged`` and ``deprecated``):

.. versionadded:: 2.5
   The *spam* parameter.

.. versionchanged:: 2.5
   The *spam* parameter.

.. deprecated:: 3.1
   Use :func:`spam` instead.

Sphinx also defines a ``seealso`` markup:

.. seealso::
   Module `other`
      Documentation of the `other` module.

   `Other Manual <https://www.example.com/manual>`_
      Manual for another reference related to this content.

.. rubric:: Rubric

The above paragraph heading is hidden from the table of contents.

.. _paragraph-level markup: http://www.sphinx-doc.org/en/stable/markup/para.html
