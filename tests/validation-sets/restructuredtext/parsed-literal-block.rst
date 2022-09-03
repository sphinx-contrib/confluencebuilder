Parsed Literal Block
====================

.. only:: confluence_storage

    .. ifconfig:: confluence_editor == 'v2'

        .. attention::

            Limitations using the Fabric (``v2``) editor:

            - Confluence does not support disabling code lines.
            - Confluence does not support parsing literal content.

reStructuredText provides a `parsed literals`_ directive help render a
literal block where the text is parsed for inline markup. Example markup
is as follows:

.. code-block:: none

    .. parsed-literal::

        def main():
            **print 'Hello, world!'**

        if __name__ == '__main__':
            main()

Output
------

.. parsed-literal::

    def main():
        **print 'Hello, world!'**

    if __name__ == '__main__':
        main()


.. references ------------------------------------------------------------------

.. _parsed literals: https://docutils.sourceforge.io/docs/ref/rst/directives.html#parsed-literal-block
