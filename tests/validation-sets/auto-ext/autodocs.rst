autodocs
========

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

   .. method:: foo(arg1, arg2)

      An overwritten description of the method ``foo``.

----

The autofunction_ directive:

.. currentmodule:: func

.. autofunction:: my_custom_function

.. _autoclass: http://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#directive-autoclass
.. _autodoc: http://www.sphinx-doc.org/en/master/ext/autodoc.html
.. _autofunction: http://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#directive-autofunction
.. _automodule: http://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#directive-automodule
