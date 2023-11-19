Production list
===============

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
