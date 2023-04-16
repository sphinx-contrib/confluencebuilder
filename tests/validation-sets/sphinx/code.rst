Code block
==========

.. only:: confluence_storage

    .. attention::

        Supported languages (for highlighting) are limited to the
        languages supported by Confluence's code block macro. This
        applies to a language defined in a ``code-block`` directive or
        set through a ``highlight`` directive.

        The ``code-block`` directive contain the options ``emphasize-lines``
        and ``lines`` which are not supported in the Confluence markup. The
        code block macro only supports a simple line numbers (configurable
        with the ``linenos`` option).

.. only:: confluence_storage

    .. ifconfig:: confluence_editor == 'v2'

        .. attention::

            Limitations using the Fabric (``v2``) editor:

            - Confluence does not support applying a code line offset.
            - Confluence does not support disabling code lines.

The following contains a series of code examples using `Sphinx's code markup`_.
Example markup is as follows:

.. code-block:: none

    .. code-block:: python

        def main():
            print 'Hello, world!'

        if __name__ == '__main__':
            main()

Output
------

The following is an example of a Python-styled code:

.. code-block:: python

    def main():
        print 'Hello, world!'

    if __name__ == '__main__':
        main()

Code blocks do not have to be Python-specific, seen with this C-styled code
block:

.. code-block:: c

    #include <stdio.h>

    int main(void)
    {
        printf("Hello, world!");
        return 0;
    }

Code blocks can optionally display line numbers (defined by Sphinx's code
markup ``:linenos:``):

.. code-block:: cpp
    :linenos:

    #include <iostream>

    int main()
    {
        std::cout << "Hello, world!";
        return 0;
    }

Presenting another code block which contains CDATA information (which should be
escaped to prevent publishing issues or display issues):

.. Broken in v8.2.0, v8.0.4, v8.1.1; see also: CONFSERVER-82849

.. code-block:: html

    <html>
    <head>
        <title>my-example</title>
        <script type="text/javascript">
        /* <![CDATA[ */
        alert('Hello, world!');
        /* ]]> */
        </script>
    </head>
    <body>
        Hello, world!
    </body>
    </html>

Literal includes can be used to only render parts of a file:

.. literalinclude:: assets/example.py
    :lines: 3
    :lineno-match:

Literal includes can also be used to show diff information:

.. literalinclude:: assets/example.py
    :diff: assets/example.py.orig

A code block can also include a caption:

.. code-block:: python
    :caption: this.py

    print('Explicit is better than implicit.')

Code macros can be collapsed when using the `class` option:

.. code-block:: none
    :class: collapse

    .. code-block:: python
        :class: collapse

        import example
        example.method()


.. references ------------------------------------------------------------------

.. _Sphinx's code markup: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-code-block
