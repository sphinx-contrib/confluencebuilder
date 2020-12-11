sphinx.ext.autodocs
===================

.. hint::

    This requires registering the ``sphinx.ext.autodocs`` extension in the
    documentation's configuration file.

This page shows an example of various autodoc_ capabilities.

autodocs - automodule
---------------------

The automodule_ directive:

.. automodule:: Hello
    :members:

----

The autoclass_ directive:

.. autoclass:: Hello
    :members: say_hello
    :noindex:

    .. method:: foo(arg1, arg2)
        :noindex:

        An overwritten description of the method ``foo``.

----

The autofunction_ directive:

.. currentmodule:: func

.. autofunction:: my_custom_function

.. references ------------------------------------------------------------------

.. _autoclass: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#directive-autoclass
.. _autodoc: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
.. _autofunction: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#directive-autofunction
.. _automodule: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#directive-automodule

