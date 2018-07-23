:orphan:

references test
---------------

.. a series of link examples

http://example.com/

http://www.example.com/

https://example.com/

https://www.example.com/

`Custom Link Name <http://example.com/>`_

This is a paragraph that contains `a link`_.

.. _a link: http://example.com/

Leading text http://example.com/ with trailing text.

Leading text `Custom Link Name <http://example.com/>`_ with trailing text.


.. example of document references


A link to document :doc:`references2`.

A link to a document with a :doc:`custom name <references2>`.


.. example of a reference/label anchor


.. _my-reference-label1:

Dummy content to generate above anchor.

.. _my-reference-label2:

sub-section
-----------

It refers to the section itself, see :ref:`my-reference-label2`.

A link to the internal anchor :ref:`Link title <my-reference-label1>`.
