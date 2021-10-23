Tips
====

.. _confluence_unique_page_names:

Confluence spaces and unique page names
---------------------------------------

An important consideration when using this extension is that Confluence has a
requirement to having unique page names for a given space. When this extension
parses a document's title value, the title is used as either a creation point or
an update point (i.e. if the page name does not exist, it will be created; if
the page name does exist, it will be updated).

A user must be cautious when mixing a space with manually prepared content and
published content from this extension. Consider the following use case.

A space ``MYAWESOMESPACE`` already exists with the following content:

* MyHome
* About
* Tutorials
* See Also

A user may desire to publish a series of Sphinx documentation into a
"container" page, so the page "Documentation" is made:

- MyHome
- About
- **Documentation**
- Tutorials
- See Also

If the Sphinx documentation contains a page named "About", an unexpected event
may occur for new users after publishing for the first time. A user might expect
the following to be published:

- MyHome
- About
- Documentation

  - About (new)
  - Installing (new)
  - User Guide (new)
  - Other (new)

- Tutorials
- See Also

However, since Confluence only supports a single "About" page for a space, the
original "About" page is updated with new content from the documentation set and
is moved as a child of the container page:

- MyHome
- Documentation

  - About (**updated and moved**)
  - Installing (new)
  - User Guide (new)
  - Other (new)

- Tutorials
- See Also

Users needing to restrict the extension from possibly mangling manually prepared
content can use the ``confluence_publish_prefix``
(:ref:`ref<confluence_publish_prefix>`) or ``confluence_publish_postfix``
(:ref:`ref<confluence_publish_postfix>`) options.

See also the :ref:`dry run capability <confluence_publish_dryrun>` and the
:ref:`title overrides capability <confluence_title_overrides>`.

Recommended options for math
----------------------------

The following are recommended options to use when using `sphinx.ext.imgmath`_:

.. code-block:: python

    imgmath_font_size = 14
    imgmath_use_preview = True
    imgmath_image_format = 'svg'

Setting a publishing timeout
----------------------------

By default, this extension does not define any timeouts for a publish event. It
is recommended to provide a timeout value based on the environment being used
(see ``confluence_timeout``; :ref:`ref<confluence_timeout>`).

.. _tip_manage_publish_subset:

Publishing with a CI secret key
-------------------------------

.. note::

    If running in a ``tox``/``virtualenv`` setup, ensure any environment
    variables used are configured to be passed through to the virtual
    environment.

For users performing automatic publishing through a CI system, they may wish to
authenticate their publish event with a secret key. A common approach to
applying a secret key is through an environment variable. For example:

.. code-block:: python

    import os

    ...

    confluence_server_pass = os.getenv('SECRET_KEY')

The above will read an environment variable ``SECRET_KEY`` prepared by a CI
script which will be set on the ``confluence_server_pass``
(:ref:`ref<confluence_server_pass>`) configuration.

Asking for help
---------------

Having trouble or concerns using this extension? Do not hesitate to bring up an
issue:

    | Atlassian Confluence Builder for Confluence - Issues
    | https://github.com/sphinx-contrib/confluencebuilder/issues

For issues when using this extension, generating a report and including this
content in an issue may be helpful towards finding a solution. To generate a
report, run the following command from the documentation directory:

.. code-block:: shell-session

    $ python -m sphinxcontrib.confluencebuilder report
    ...
    Confluence builder report has been generated.
    Please copy the following text for the GitHub issue:

    ------------[ cut here ]------------
    (system)
    ...

    (configuration)
    ...

    (confluence instance)
     ...
    ------------[ cut here ]------------

.. references ------------------------------------------------------------------

.. _sphinx.ext.imgmath: https://www.sphinx-doc.org/en/master/usage/extensions/math.html#module-sphinx.ext.imgmath
