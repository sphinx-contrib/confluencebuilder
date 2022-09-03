Production list
===============

.. only:: confluence_storage

    .. ifconfig:: confluence_editor == 'v2'

        .. attention::

            Limitations using the Fabric (``v2``) editor:

            - Confluence does not support disabling code lines.

Sphinx defines a `production list`_. Example markup is as follows:

.. code-block:: none

    .. productionlist::
         try_stmt: try1_stmt | try2_stmt
        try1_stmt: "try" ":" `suite`
                 : ("except" [`expression` ["," `target`]] ":" `suite`)+
                 : ["else" ":" `suite`]
                 : ["finally" ":" `suite`]
        try2_stmt: "try" ":" `suite`
                 : "finally" ":" `suite`

Output
------

.. productionlist::
     try_stmt: try1_stmt | try2_stmt
    try1_stmt: "try" ":" `suite`
             : ("except" [`expression` ["," `target`]] ":" `suite`)+
             : ["else" ":" `suite`]
             : ["finally" ":" `suite`]
    try2_stmt: "try" ":" `suite`
             : "finally" ":" `suite`


.. references ------------------------------------------------------------------

.. _production list: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-productionlist
