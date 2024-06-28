.. index:: Strike

Strike content
==============

There are a series of strike element capabilities supported by the
Confluence builder extension. This guide will cover the available options
that can be used.

Strike role
-----------

.. versionadded:: 2.1

This extension provides a ``confluence_strike`` role to help strike
content. For example:

.. code-block:: rst

    :confluence_strike:`My text`

This role will only work when using the Confluence builder. See also the
:ref:`Confluence Strikethrough role <confluence_strike-role>`.

.. _confluence_strike_ch:

Class hints
-----------

.. versionadded:: 1.7

When this class hint is applied to inlined text, the text will be styled
with a strikethrough style. Sphinx projects may define the following in
a document to support the strikethrough of text in both the ``html`` and
``confluence`` builders (assuming HTML documents are also prepared to
support the ``strike`` class):

.. code-block:: none

    .. role:: strike
        :class: strike

    This is an :strike:`example`.

Projects may also move the role definition inside the project's ``conf.py``
inside `rst_prolog <rst_prolog_>`_ as follows:

.. code-block:: python

    rst_prolog = """

    .. role:: strike
        :class: strike

    """

Projects using `Markedly Structured Text - Parser <myst-parser_>`_ can also
take advantage of the role defined in ``rst_prolog`` (above) and use the
role as follows:

.. code-block:: md

    This is an {strike}`example`.

sphinxnotes-strike's strike role
--------------------------------

.. versionadded:: 2.2

When using the `sphinxnotes-strike`_ extension, a ``strike`` role should
be able to manage striked content. For example:

.. code-block:: rst

    :strike:`My text`

.. references ------------------------------------------------------------------

.. _myst-parser: https://myst-parser.readthedocs.io/
.. _rst_prolog: https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-rst_prolog
.. _sphinxnotes-strike: https://sphinx.silverrainz.me/strike/
