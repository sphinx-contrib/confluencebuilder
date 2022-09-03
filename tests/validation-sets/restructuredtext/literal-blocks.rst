Literal Blocks
==============

.. only:: confluence_storage

    .. ifconfig:: confluence_editor == 'v2'

        .. attention::

            Limitations using the Fabric (``v2``) editor:

            - Confluence does not support disabling code lines.

reStructuredText provides a `literal block`_ directive help render a block
of content in a monospaced typeface. Example markup is as follows:

.. code-block:: none

    ::

        for a in [5,4,3,2,1]:   # this is program code, shown as-is
            print a
        print "it's..."
        # a literal block continues until the indentation ends

Output
------

::

    for a in [5,4,3,2,1]:   # this is program code, shown as-is
        print a
    print "it's..."
    # a literal block continues until the indentation ends


.. references ------------------------------------------------------------------

.. _literal block: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#literal-blocks
