Manual Page
===========

Sphinx's `manpage`_ should build off a configured ``manpages_url`` value:

.. code-block:: none
    :caption: conf.py

    manpages_url = 'https://example.org/{path}'

Example markup to reference a manpage is as follows:

.. code-block:: none

    :manpage:`ls(1)`

Output
------

:manpage:`ls(1)`


.. references ------------------------------------------------------------------

.. _manpage: https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#role-manpage
