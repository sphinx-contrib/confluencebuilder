sphinx.ext.todo
===============

.. hint::

    This requires registering the ``sphinx.ext.todo`` extension in the
    documentation's configuration file.

This page shows an example of various todo_ capabilities. An example todo entry
can be created using the following directive with also the
``todo_include_todos`` configuration option set:

.. code-block:: none

    .. todo::

        This is an example message.

Output
------

The following shows an example of todo entries:

.. todo::

    This is an example message.

.. todo::

    This is a second message.

This extension also supports compiling a list of entries as follows:

.. todolist::


.. references ------------------------------------------------------------------

.. _todo: https://www.sphinx-doc.org/en/master/usage/extensions/todo.html
