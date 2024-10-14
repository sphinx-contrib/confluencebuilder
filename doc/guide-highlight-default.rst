Configuring the default highlighter
===================================

Sphinx's default highlight language is ``python``. For any documentation
processed by this extension that does not have an explicit language type
provided will fallback to Sphinx's default.

Users wishing to override the default highlight language can use the
:lref:`confluence_lang_overrides` configuration. For example, adding the
following option inside a project's ``conf.py`` file:

.. code-block:: python

    confluence_lang_overrides = {
        'default': 'none',
    }
