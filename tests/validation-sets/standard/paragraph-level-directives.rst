Paragraph-level directives
==========================

The following contains a series of paragraph related directives:

* `deprecated directive`_
* `rubric directive`_
* `seealso directive`_
* `versionadded directive`_
* `versionchanged directive`_

Example markup is as follows:

.. code-block:: none

    .. deprecated:: 3.1
       Use :func:`spam` instead.

Output
------

The following shows an example of version modification-related markup:

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

.. references ------------------------------------------------------------------

.. _deprecated directive: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-deprecated
.. _rubric directive: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-rubric
.. _seealso directive: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-seealso
.. _versionadded directive: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-versionadded
.. _versionchanged directive: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-versionchanged
