:orphan:

.. https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html?highlight=production%20list#directive-productionlist

production list
---------------

.. productionlist::
   try_stmt: try1_stmt | try2_stmt
   try1_stmt: "try" ":" `suite`
            : ("except" [`expression` ["," `target`]] ":" `suite`)+
            : ["else" ":" `suite`]
            : ["finally" ":" `suite`]
   try2_stmt: "try" ":" `suite`
            : "finally" ":" `suite`
