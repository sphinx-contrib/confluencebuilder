Definition list
===============

reStructuredText supports defining `definition lists`_. Users should be
able to see terms and an associated description for the term. Classifiers
may also exist for a term and should be presented along side it. Example
markup is as follows:

.. code-block:: none

    term 1
       Lorem ipsum dolor sit amet, consectetur adipiscing elit.

    term 2
       Maecenas at leo eget metus cursus tempor.

       Pellentesque egestas orci id purus facilisis, eu vestibulum dolor feugiat.

    term 3 : classifier
       Nunc ac quam lacinia, viverra orci vel, varius dui.

    term 4 : classifier one : classifier two
       Vivamus vel dolor eget mauris mollis dictum.

Output
------

term 1
   Lorem ipsum dolor sit amet, consectetur adipiscing elit.

term 2
   Maecenas at leo eget metus cursus tempor.

   Pellentesque egestas orci id purus facilisis, eu vestibulum dolor feugiat.

term 3 : classifier
   Nunc ac quam lacinia, viverra orci vel, varius dui.

term 4 : classifier one : classifier two
   Vivamus vel dolor eget mauris mollis dictum.


.. references ------------------------------------------------------------------

.. _definition lists: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#definition-lists
