:orphan:

.. reStructuredText references and related documentation:
   http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#citations
   http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#footnotes
   http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#hyperlink-references
   http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#hyperlink-targets
   http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#reference-names
   http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#standalone-hyperlinks

   Confluence Wiki Markup - Links
   https://confluence.atlassian.com/doc/confluence-wiki-markup-251003035.html#ConfluenceWikiMarkup-Links

references and related
======================

This page provides example of references and related markup:

* Generic References
* Hyperlinks
* Hyperlink References
* Hyperlink Targets
* Citations
* Footnotes

generic references
------------------

| The most common method reference with Sphinx is a "phrase-reference";
  consider the example of `this phrase being a link`_. Pphrase-reference links
  can be on `two lines`_ or `various lines`_.

.. _this phrase being a link: http://www.example.com

.. _two lines: https://
   www.example.com

.. _various lines:
   http://www.example.com
   /home
   /index

hyperlinks
----------

| Hyperlinks are handled automatically. We can create a link using with an
  various protocols, such as http://www.example.com,
  https://www.example.com/subsection/another-page.html or even
  ftp://www.example.com.

| Emails links can be formed as well using the mailto prefix such as
  mailto:someone@example.com or without the prefix (someone@example.com).

hyperlink references
--------------------

| Hyperlink references are another method to form hyperlinks in a document. We
  can create `in-line links <http://www.example.com/custom>`_ to your targets.
  We can also link to pages anonymously; for example, using `link a`__ and
  `link b`__. The syntax choice is up to you.

__ http://www.example.com/static/doc-a.txt
__ http://www.example.com/static/doc-b.txt

hyperlink targets
-----------------

| Hyperlink target can be built. Clicking on this internal hyperlink (targeta_)
  with being us to an anchor above the following paragraph. We can also jump to
  the lower paragraph with this internal hyperlink (targetb_) or internal
  hyperlink (targetc_).

.. _targeta:

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus leo nunc, commodo et risus ac, hendrerit aliquet est. Phasellus volutpat arcu at eros tempus, sed sodales eros vehicula. Fusce dictum eros augue, eget iaculis ligula sollicitudin nec. Sed dignissim quam leo, a imperdiet magna pharetra sed. In in viverra libero. Maecenas mattis maximus condimentum. Integer ornare mauris nec urna rutrum, eu iaculis augue molestie. Vivamus ultrices mattis quam id condimentum. Phasellus tellus lacus, gravida sed porttitor ut, sodales at risus. Phasellus mollis justo sed orci consectetur lacinia. Integer molestie lacinia risus, et iaculis justo tristique ac. Nullam luctus ante sapien, in tristique magna interdum ut. Vestibulum hendrerit tellus arcu, quis volutpat ligula auctor nec. Maecenas sit amet justo orci.

.. _targetb:
.. _targetc:

Integer blandit interdum erat, sed interdum sapien varius et. Maecenas at tortor quis velit mattis ultricies. Vivamus nisl leo, finibus ac tincidunt vitae, pharetra quis orci. Maecenas lobortis neque ipsum, quis ultricies velit auctor eu. Quisque pellentesque suscipit sodales. In sapien massa, tincidunt vel nisl id, sodales bibendum dui. Pellentesque consectetur a risus sed aliquam.

citations
---------

| A page can have multiple citations [CIT2001]_, and it does not matter on the
  order which they are used [CIT2002]_. Wherever the citations are defined, a
  Confluence table will be built [CIT2003]_.

.. [CIT2001] This is an example citation.
.. [CIT2002] It's true, a does not matter the order of citation's used, the \
   respective citation point will be referenced.
.. [CIT2003] Another citation example.

footnotes
---------

| There are various types of footnote methods styles that can be applied. We
  can reference the first footnote [#note]_; and it show up as "[1]". We can
  also refer to the footnote again [#note]_ and it should again be seen as
  "[1]". We can also use its label form, note_ or
  :ref:`custom note label <note>`, to refer to the footnote (i.e. as an internal
  hyperlink reference).

.. [#note] This is the footnote labeled "note".
.. [#] This is the footnote labeled "note".

| You can also reference footnotes after the fact either explicitly [#note]_ or
  anonymously [#]_.

| A standard way to use footnotes is in an incremental fashion. The first [#]_
  and second [#]_ footnotes should be "[3]" and "[5]" (anonymous auto-numbered).
  The next anonymous auto-numbered footnotes, [#]_ and [#]_, will actually be
  "[6]" and "[7]". We can also manually override the footnote number [4]_ (a
  value of "[4]").

.. [4] This is footnote 4.
.. [#] This is footnote 3.
.. [#] This is footnote 5.
.. [#] This is footnote 6.
.. [#] This is footnote 7.

