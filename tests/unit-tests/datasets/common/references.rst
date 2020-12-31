:orphan:

.. https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#hyperlink-references
.. https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#hyperlink-targets
.. https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#reference-names
.. https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#standalone-hyperlinks

references
----------

.. basic links -----------------------------------------------------------------

https://www.example.com/

someone@example.com

`custom name <https://example.com/>`_

`a link`_

.. _a link: https://example.com/

.. escaped check --- > should be escaped ---------------------------------------

`> <https://example.org/>`_

.. inline markup should work inside (most) references --------------------------

.. |a link| replace:: **a bolded link**

|a link|_

.. example of document references ----------------------------------------------

document link :doc:`references-ref`

document with :doc:`custom name <references-ref>`

.. example of a reference/label anchor -----------------------------------------

.. _my-reference-label1:

dummy content to generate above anchor

.. _my-reference-label2:

sub-section
-----------

:ref:`my-reference-label2`

:ref:`internal anchor <my-reference-label1>`
