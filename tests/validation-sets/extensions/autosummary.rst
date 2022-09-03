sphinx.ext.autosummary
======================

.. hint::

    This requires registering the ``sphinx.ext.autosummary`` extension in the
    documentation's configuration file.

This page shows an example of various autosummary_ capabilities.

An example of a local docstring:

.. autosummary::

    Hello

An example of an external module docstring:

.. currentmodule:: sphinx

.. autosummary::

    environment.BuildEnvironment
    util.relative_uri


.. references ------------------------------------------------------------------

.. _autosummary: https://www.sphinx-doc.org/en/master/usage/extensions/autosummary.html
