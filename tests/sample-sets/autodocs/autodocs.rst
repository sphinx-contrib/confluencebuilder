sphinx.ext.autodocs
===================

This page shows an example of various autodoc capabilities.

autodocs - automodule
---------------------

The automodule directive:

.. automodule:: Hello
    :members:

----

The autoclass directive:

.. autoclass:: Hello
    :members: say_hello
    :noindex:

    .. method:: foo(arg1, arg2)
        :noindex:

        An overwritten description of the method ``foo``.

----

The autofunction directive:

.. currentmodule:: func

.. autofunction:: my_custom_function
