sphinx.ext.linkcode
===================

.. hint::

    This requires registering the ``sphinx.ext.linkcode`` extension in the
    documentation's configuration file.

This page shows an example of the linkcode_ extension's capabilities. A
project configuration defines a ``linkcode_resolve`` function:

.. code-block:: python

    def linkcode_resolve(domain, info):
        name = info.get('fullname', None)
        if not name:
            return None
        return "https://example.org/src/%s" % name

When documents include object descriptions such as the following, source
links should be included:

.. code-block:: none

    .. class:: ExampleModule

       This is an example.

Output
------

The following shows an example of linkcode:

.. module:: linkcode_example

.. class:: ExampleModule

   This is an example.


.. references ------------------------------------------------------------------

.. _linkcode: https://www.sphinx-doc.org/en/master/usage/extensions/linkcode.html
