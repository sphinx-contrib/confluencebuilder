sphinx.ext.graphviz
===================

.. hint::

    This requires registering the ``sphinx.ext.graphviz`` extension in the
    documentation's configuration file.

This page shows an example of various graphviz_ capabilities. An example of a
graphviz directive is as follows:

.. code-block:: none

    .. graphviz::

        digraph foo {
            "bar" -> "baz";
        }

Output
------

An example of the rendered output of a embedded graphviz code:

.. graphviz::
    :align: center

    digraph foo {
        "bar" -> "baz";
    }

A user can also take advantage of adding an embedding a single undirected graph:

.. graph:: foo
    :align: center

    "bar" -- "baz";

Single directed graphs are supported as well:

.. digraph:: foo
    :align: center

    "bar" -> "baz" -> "quux";


.. references ------------------------------------------------------------------

.. _graphviz: https://www.sphinx-doc.org/en/master/usage/extensions/graphviz.html
