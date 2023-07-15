.. index:: Class hints

.. _confluence_class_hints:

Class hints
===========

The following outlines all available class-related hints supported by the
Confluence builder extension.

``collapse``
------------

See :ref:`Collapsed content <confluence_collapsed_ch>` for more details.

``confluence-theme-<theme>``
----------------------------

.. versionadded:: 2.2

When this class hint is applied to a literal/code block, this provides the
ability to override the theme configured for an individual code-block macro.
For example:

.. code-block:: none

    .. code-block:: python
        :class: confluence-theme-FadeToGrey

        def main():
            print 'Hello, world!'

        if __name__ == '__main__':
            main()

See also :ref:`confluence_code_block_theme <confluence_code_block_theme>`.

``strike``
----------

.. versionadded:: 1.7

When this class hint is applied to inlined text, the text will be styled
with a strikethrough style. Sphinx projects may define the following in
a document to support the strikethrough of text in both the ``html`` and
``confluence`` builders (assuming the HTML documents are also prepared to
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


.. references ------------------------------------------------------------------

.. _myst-parser: https://myst-parser.readthedocs.io/
.. _rst_prolog: https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-rst_prolog
