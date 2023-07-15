.. index:: Class hints

.. _confluence_class_hints:

Class hints
===========

The following outlines all available class-related hints supported by the
Confluence builder extension.

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
