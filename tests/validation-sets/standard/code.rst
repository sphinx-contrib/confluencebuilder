Code
====

The following contains a series of code examples using `Sphinx's code markup`_
and reStructuredText's `literal block`_/`parsed literals`_. Example markup is
as follows:

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

The following shows an example of a `literal block`_:

::

    for a in [5,4,3,2,1]:   # this is program code, shown as-is
        print a
    print "it's..."
    # a literal block continues until the indentation ends

doctest entries should display a code markup styled in Python:

>>> print "This is a doctest block."
This is a doctest block.

Documentation may included `parsed literals`_. While parsed literals cannot take
advantage of Confluence's code macros, it is important that the content is
rendered with the document-defined inline markup:

.. parsed-literal::

    def main():
        **print 'Hello, world!'**

    if __name__ == '__main__':
        main()

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

.. references ------------------------------------------------------------------

.. _Sphinx's code markup: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-code-block
.. _literal block: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#literal-blocks
.. _parsed literals: https://docutils.sourceforge.io/docs/ref/rst/directives.html#parsed-literal-block
