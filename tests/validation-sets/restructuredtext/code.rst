Code
====

.. only:: confluence_storage

    .. ifconfig:: confluence_editor == 'v2'

        .. attention::

            Limitations using the Fabric (``v2``) editor:

            - Confluence does not support applying a code line offset.
            - Confluence does not support disabling code lines.

reStructuredText provides a `code`_ directive help render a literal block
where if a code language is specified, the content is parsed by a syntax
highlighter. Example markup is as follows:

.. code-block:: none

    .. code:: python

        def main():
            print 'Hello, world!'

        if __name__ == '__main__':
            main()

Output
------

The following is an example of a Python-styled code:

.. code:: python

    def main():
        print 'Hello, world!'

    if __name__ == '__main__':
        main()

Code blocks do not have to be Python-specific, seen with this C-styled code
block:

.. code:: c

    #include <stdio.h>

    int main(void)
    {
        printf("Hello, world!");
        return 0;
    }

Code blocks can optionally display line numbers using the ``:number-lines:``
option:

.. code:: cpp
    :number-lines:

    #include <iostream>

    int main()
    {
        std::cout << "Hello, world!";
        return 0;
    }

Line numbers can also be offset by a specified amount:

.. code:: cpp
    :number-lines: 3

    int main()
    {
        std::cout << "Hello, world!";
        return 0;
    }


.. references ------------------------------------------------------------------

.. _code: https://docutils.sourceforge.io/docs/ref/rst/directives.html#code
