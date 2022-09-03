CSV Table
=========

.. only:: confluence_storage

    .. ifconfig:: confluence_editor == 'v2'

        .. attention::

            Limitations using the Fabric (``v2``) editor:

            - Confluence does not support customizing column widths.

reStructuredText defines a `csv-table`_. Example markup is as follows:

.. code-block:: none

    .. csv-table:: Frozen Delights!
        :header: "Treat", "Quantity", "Description"
        :widths: 15, 10, 30

        "Albatross", 2.99, "On a stick!"
        "Crunchy Frog", 1.49, "If we took the bones out, it wouldn't be
        crunchy, now would it?"
        "Gannet Ripple", 1.99, "On a stick!"

Output
------

.. csv-table:: Frozen Delights!
    :header: "Treat", "Quantity", "Description"
    :widths: 15, 10, 30

    "Albatross", 2.99, "On a stick!"
    "Crunchy Frog", 1.49, "If we took the bones out, it wouldn't be
    crunchy, now would it?"
    "Gannet Ripple", 1.99, "On a stick!"


.. references ------------------------------------------------------------------

.. _csv-table: https://docutils.sourceforge.io/docs/ref/rst/directives.html#csv-table
