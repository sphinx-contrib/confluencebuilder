Footnote
########

reStructuredText supports defining `footnotes`_. Example markup is as
follows:

.. code-block:: none

    Footnotes can be explicit [#note]_ or anonymously [#]_.

    .. [#note] This is the footnote labeled "note".
    .. [#] This is an anonymous footnote.

Output
------

There are various types of footnote methods styles that can be applied. A
document can reference the first footnote [#note]_ using a label; and it render
as "[1]". A document can also refer to the footnote again [#note]_ and it should
again be seen as "[1]". A document can also use its label form, note_, to refer
to the footnote (i.e. as an internal hyperlink reference).

.. [#note] This is the footnote labeled "note".
.. [#] This is an anonymous footnote.

You can also reference footnotes after the fact either explicitly [#note]_ or
anonymously [#]_.

A standard way to use footnotes is in an incremental fashion. The first [#]_ and
second [#]_ footnotes should be "[3]" and "[5]" (anonymous auto-numbered).
Adding an additional line of test to help space our the footnote examples to
help visually see footnote references in play. The next anonymous auto-numbered
footnotes, [#]_ and [#]_, will actually be "[6]" and "[7]". A document can also
manually override the footnote number [4]_ (a value of "[4]"). Adding a series
of lorem ipsum to help increase spacing to help visualize footnote references:

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse eget mattis
purus, vitae dapibus ipsum. Quisque non nulla magna. Cras euismod nec ligula et
accumsan. Suspendisse ullamcorper nisi aliquet tellus tempus consectetur. Fusce
quis dolor auctor, vehicula nulla eu, sollicitudin mi. Duis auctor metus sit
amet metus rutrum, et malesuada quam dignissim. Nullam lobortis urna a tempor
mollis. In sagittis leo ut euismod tincidunt. Quisque nunc sapien, blandit sed
est et, rutrum cursus ipsum. Suspendisse aliquet lacus sit amet elit dignissim,
vitae lobortis erat pellentesque. Morbi sollicitudin tempor nibh et semper.
Curabitur sed lectus gravida, tincidunt arcu sit amet, congue velit. Interdum et
malesuada fames ac ante ipsum primis in faucibus.

.. [4] This is footnote 4.
.. [#] This is footnote 3.
.. [#] This is footnote 5.
.. [#] This is footnote 6.
.. [#] This is footnote 7.


.. references ------------------------------------------------------------------

.. _footnotes: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#footnotes
