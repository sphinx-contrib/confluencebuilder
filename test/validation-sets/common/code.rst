code
====

The following contains a series of code examples using `Sphinx's code markup`_.
The first code block is an example of Python-styled code:

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

.. _Sphinx's code markup: http://www.sphinx-doc.org/en/stable/markup/code.html
.. _parsed literals: http://docutils.sourceforge.net/docs/ref/rst/directives.html#parsed-literal-block
