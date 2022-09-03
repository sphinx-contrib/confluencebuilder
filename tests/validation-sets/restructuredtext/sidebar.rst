Sidebar
=======

.. only:: confluence_storage

    .. attention::

        Sidebars are not supported. Any use of this directive is ignored.

reStructuredText defines a `sidebar directive`_. Example markup is as follows:

.. code-block:: none

    .. sidebar:: Optional Sidebar Title
       :subtitle: Optional Sidebar Subtitle

       Subsequent indented lines comprise
       the body of the sidebar, and are
       interpreted as body elements.

Output
------

.. sidebar:: Optional Sidebar Title
   :subtitle: Optional Sidebar Subtitle

   Subsequent indented lines comprise
   the body of the sidebar, and are
   interpreted as body elements.


.. references ------------------------------------------------------------------

.. _sidebar directive: https://docutils.sourceforge.io/docs/ref/rst/directives.html#sidebar
