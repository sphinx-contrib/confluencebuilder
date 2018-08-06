:orphan:

   http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#hyperlink-references
   http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#hyperlink-targets
   http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#reference-names
   http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#standalone-hyperlinks

references
----------

.. a series of link examples ---------------------------------------------------

http://example.com/

http://www.example.com/

https://example.com/

https://www.example.com/

mailto:someone@example.com

someone@example.com

`custom name <https://example.com/>`_

`a link`_

.. _a link: https://example.com/

leading https://example.com/ trailing

leading `custom name <https://example.com/>`_ trailing

.. example of document references ----------------------------------------------

document link :doc:`references-ref`

document with :doc:`custom name <references-ref>`

.. example of a reference/label anchor -----------------------------------------

.. _my-reference-label1:

dummy content to generate above anchor

.. _my-reference-label2:

sub-section
-----------

section :ref:`my-reference-label2`.

:ref:`internal anchor <my-reference-label1>`.
