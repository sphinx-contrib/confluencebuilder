Indentation
===========

.. only:: confluence_storage

    .. ifconfig:: confluence_editor == 'v2'

        .. attention::

            Limitations using the Fabric (``v2``) editor:

            - Confluence does not support indenting block types. For example,
              an indented paragraph with a list will always have the list rendered
              without an indentation.

reStructuredText supports the ability to `indent`_ content. The builder will
translate the indented content into respective indented paragraphs. Content that
is indented is not captured in a Confluence quote. Paragraphs should be properly
spaced with each other.

----

This is a top-level paragraph.

   This paragraph belongs to a first-level block quote

      This paragraph belongs to a second-level block quote.

Another top-level paragraph.

         This paragraph belongs to a third-level block quote.

      This paragraph belongs to a second-level block quote.

   This paragraph belongs to a first-level block quote. The second-level block
   quote above is inside this first-level block quote.

Another top-level paragraph.

   A paragraph should be able to handle other block types. For example a list:

   - First item.
   - Second item.
   - Third item.

   Content should be properly spaced.


.. references ------------------------------------------------------------------

.. _indent: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#indentation
