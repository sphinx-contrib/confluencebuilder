Extensions
==========

The Sphinx Confluence Builder is powered by Sphinx_. There are several
ways individual projects may extend their configuration or use other
extensions to improve the processing and generation of their documentation.

For users new to Sphinx, it is recommended to read Sphinx's documentation
on extensions:

    | Sphinx Extensions API
    | https://www.sphinx-doc.org/en/master/extdev/index.html

This extension does not provide any significant API capabilities beyond
what is provided by Sphinx's existing API support. Developers or advanced
users are recommended to use official Sphinx API calls for any modifications
that are applicable when using the Sphinx Confluence Builder extension.
Users are welcome to inspect this extension's code for any custom tweaks
desired for their project;. While using extension specific implementation
for customization is unsupported, this extension aims to be flexible to
support users when possible.

The following shows an example modification for a project to support a
custom node type that is not supported by this extension. Users can use
`Sphinx.add_node`_ to help register support for custom nodes. The keyword
to use for this extension is `confluence`. If another extension defines a
node `custom_node`, the following shows some example code to start supporting
this node with Sphinx Confluence Builder:

.. code-block:: python

    def setup(app):
        app.add_node(
            custom_node,
            confluence=(visit_custom_node, depart_custom_node),
        )

    def visit_custom_node(self, node):
        self.body.append('[pre]')
        self.context.append('[post]')

    def depart_custom_node(self, node):
        self.body.append(self.context.pop())

.. references ------------------------------------------------------------------

.. _Sphinx.add_node: https://www.sphinx-doc.org/en/master/extdev/appapi.html#sphinx.application.Sphinx.add_node
.. _Sphinx: https://www.sphinx-doc.org/
