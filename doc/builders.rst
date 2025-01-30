Builders
========

The following outlines the Sphinx builders provided by this extension.

.. builderval:: confluence

    The ``confluence`` builder allows a user to process a Sphinx supported
    documentation set to generate a Confluence supported representation. 
    Individual documents will generate Confluence supported documents, which in
    turn can be published to a configured Confluence instance:

    .. code-block:: shell

        sphinx-build -b confluence . _build/confluence -E -a

.. builderval:: singleconfluence

    The ``singleconfluence`` builder allows a user to process a Sphinx supported
    documentation set to generate a single document in a Confluence supported
    representation. The generated document can in turn be published to a 
    configured Confluence instance:

    .. code-block:: shell

        sphinx-build -b singleconfluence . _build/singleconfluence -E -a

    .. versionadded:: 1.3
