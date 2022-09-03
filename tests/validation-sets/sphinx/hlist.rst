Horizontal list
===============

.. only:: confluence_storage

    .. ifconfig:: confluence_editor == 'v2'

        .. attention::

            Limitations using the Fabric (``v2``) editor:

            - Maximum number of columns (``:columns:``) supported is
              three (``3``).

Sphinx defines an `hlist`_. Example markup is as follows:

.. code-block:: none

    .. hlist::
       :columns: 3

       * A list of
       * short items
       * that should be
       * displayed
       * horizontally

Output
------

.. hlist::
   :columns: 3

   * A list of
   * short items
   * that should be
   * displayed
   * horizontally


.. references ------------------------------------------------------------------

.. _hlist: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-hlist
