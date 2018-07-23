.. Sphinx Code documentation:
   http://www.sphinx-doc.org/en/stable/markup/code.html

   Confluence Wiki Markup - Code Block Macro
   https://confluence.atlassian.com/doc/code-block-macro-139390.html

code
====

The following contains a series of code examples:

.. code-block:: python

   def main():
       print 'Hello, world!'

   if __name__ == '__main__':
       main()

.. code-block:: c

   #include <stdio.h>

   int main(void)
   {
       printf("Hello, world!");
       return 0;
   }

.. code-block:: cpp
   :linenos:

   #include <iostream>

   int main()
   {
       std::cout << "Hello, world!";
       return 0;
   }

.. code-block:: html

    <html>
    <header>
        <title>my-example</title>
        <script type="text/javascript">
        /* <![CDATA[ */
        alert('Hello, world!');
        /* ]]> */
        </script>
    </header>
    <body>
        Hello, world!
    </body>
    </html>

>>> print "This is a doctest block."
This is a doctest block.
