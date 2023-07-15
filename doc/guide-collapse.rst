.. index:: Collapsed

Collapsed content
=================

There are a series of collapsed element capabilities supported by the
Confluence builder extension. This guide will cover the available options that
can be used.

Expand directive
----------------

.. versionadded:: 1.3

This extension provides a ``confluence_expand`` directive to help collapse
content. For example:

.. code-block:: rst

    .. confluence_expand::

        This content is captured inside the expand macro.

This directive will only work when using the Confluence builder. See also the
:ref:`Confluence expand directive <confluence_expand-directive>`.

.. _confluence_collapsed_ch:

Class hints
-----------

.. versionadded:: 2.1 Support added for containers.
.. versionadded:: 2.0 Support added for code blocks.

This extension provides support for managing collapsed elements when a
``collapse`` class hint is provided. If a container is defined with the
style configured, the contents of the directive will be collapsed:

.. code-block:: rst

    .. container:: collapse

        This paragraph should be collapsed.

When using the code block directive, providing a collapse style hint will
also collapse the code block:

.. code-block:: rst

    .. code-block:: python
        :class: collapse

        import example
        example.method()

sphinx-toolbox's collapse directive
-----------------------------------

.. versionadded:: 1.7

When using the `sphinx-toolbox`_ extension, the ``collapse`` directive
should be able to manage collapsed content. For example:

.. code-block:: rst

    .. collapse:: Details

        This paragraph should be collapsed.

For more details, please see sphinx-toolbox's documentation on the
`collapse directive <directive-collapse_>`_.

.. references ------------------------------------------------------------------

.. _directive-collapse: https://sphinx-toolbox.readthedocs.io/en/latest/extensions/collapse.html#directive-collapse
.. _sphinx-toolbox: https://sphinx-toolbox.readthedocs.io/
