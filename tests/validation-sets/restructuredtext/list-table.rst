List Table
==========

reStructuredText defines a `list-table`_. Example markup is as follows:

.. code-block:: none

    .. list-table::
        :header-rows: 1
        :stub-columns: 1

        * - key
          - value
        * - 1
          - 2
        * - 3
          - 4
        * - 5
          - 6

Output
------

.. list-table::
    :header-rows: 1
    :stub-columns: 1

    * - key
      - value
    * - 1
      - 2
    * - 3
      - 4
    * - 5
      - 6


.. references ------------------------------------------------------------------

.. _list-table: https://docutils.sourceforge.io/docs/ref/rst/directives.html#list-table
