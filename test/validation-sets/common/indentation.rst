indentation
===========

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

.. _indent: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#indentation
