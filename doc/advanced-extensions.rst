Extensions
==========

The Sphinx Confluence Builder is powered by Sphinx_. There are several
ways individual projects may extend their configuration or use other
extensions to improve the processing and generation of their documentation.

For users new to Sphinx, it is recommended to read Sphinx's documentation
on extensions:

    | Sphinx Extensions API
    | https://www.sphinx-doc.org/en/master/extdev/index.html

Developers or advanced users are recommended to use official Sphinx API
calls for any modifications that are applicable when using the Sphinx
Confluence Builder extension. Users are welcome to inspect this
extension's code for any custom tweaks desired for their project.

The following shows an example modification for a project to support a
custom node type that is not supported by this extension. Users can use
`Sphinx.add_node`_ to help register support for custom nodes. The keyword
to use for this extension is ``confluence``. If another extension defines a
node ``custom_node``, the following shows some example code to start supporting
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

.. raw:: latex

    \newpage

Confluence Storage Format Translator Helpers
--------------------------------------------

When extending this extension or adding more advanced configurations, a
series of helper calls are available for use. API calls may evolve over time
as this extension is maintained. The following methods are available for a
``ConfluenceStorageFormatTranslator`` translator.

.. Ideally, the following entries would use `:no-index-entry:` over
   `:no-index:`. However it looks like the autodocs extension does no yet
   support this capability.

.. (sorting) start off with start/end tag

.. autofunction:: sphinxcontrib.confluencebuilder.storage.translator.ConfluenceStorageFormatTranslator.start_tag
    :no-index:
.. autofunction:: sphinxcontrib.confluencebuilder.storage.translator.ConfluenceStorageFormatTranslator.end_tag
    :no-index:

.. (sorting) then sort by name with prefix order start/end pairs and specific calls

.. autofunction:: sphinxcontrib.confluencebuilder.storage.translator.ConfluenceStorageFormatTranslator.start_ac_image
    :no-index:
.. autofunction:: sphinxcontrib.confluencebuilder.storage.translator.ConfluenceStorageFormatTranslator.end_ac_image
    :no-index:
.. autofunction:: sphinxcontrib.confluencebuilder.storage.translator.ConfluenceStorageFormatTranslator.start_ac_link
    :no-index:
.. autofunction:: sphinxcontrib.confluencebuilder.storage.translator.ConfluenceStorageFormatTranslator.end_ac_link
    :no-index:
.. autofunction:: sphinxcontrib.confluencebuilder.storage.translator.ConfluenceStorageFormatTranslator.start_ac_link_body
    :no-index:
.. autofunction:: sphinxcontrib.confluencebuilder.storage.translator.ConfluenceStorageFormatTranslator.end_ac_link_body
    :no-index:
.. autofunction:: sphinxcontrib.confluencebuilder.storage.translator.ConfluenceStorageFormatTranslator.start_ac_macro
    :no-index:
.. autofunction:: sphinxcontrib.confluencebuilder.storage.translator.ConfluenceStorageFormatTranslator.build_ac_param
    :no-index:
.. autofunction:: sphinxcontrib.confluencebuilder.storage.translator.ConfluenceStorageFormatTranslator.end_ac_macro
    :no-index:
.. autofunction:: sphinxcontrib.confluencebuilder.storage.translator.ConfluenceStorageFormatTranslator.start_ac_plain_text_body_macro
    :no-index:
.. autofunction:: sphinxcontrib.confluencebuilder.storage.translator.ConfluenceStorageFormatTranslator.end_ac_plain_text_body_macro
    :no-index:
.. autofunction:: sphinxcontrib.confluencebuilder.storage.translator.ConfluenceStorageFormatTranslator.start_ac_plain_text_link_body_macro
    :no-index:
.. autofunction:: sphinxcontrib.confluencebuilder.storage.translator.ConfluenceStorageFormatTranslator.end_ac_plain_text_link_body_macro
    :no-index:
.. autofunction:: sphinxcontrib.confluencebuilder.storage.translator.ConfluenceStorageFormatTranslator.start_ac_rich_text_body_macro
    :no-index:
.. autofunction:: sphinxcontrib.confluencebuilder.storage.translator.ConfluenceStorageFormatTranslator.end_ac_rich_text_body_macro
    :no-index:
.. autofunction:: sphinxcontrib.confluencebuilder.storage.translator.ConfluenceStorageFormatTranslator.start_adf_content
    :no-index:
.. autofunction:: sphinxcontrib.confluencebuilder.storage.translator.ConfluenceStorageFormatTranslator.end_adf_content
    :no-index:
.. autofunction:: sphinxcontrib.confluencebuilder.storage.translator.ConfluenceStorageFormatTranslator.start_adf_extension
    :no-index:
.. autofunction:: sphinxcontrib.confluencebuilder.storage.translator.ConfluenceStorageFormatTranslator.build_adf_attribute
    :no-index:
.. autofunction:: sphinxcontrib.confluencebuilder.storage.translator.ConfluenceStorageFormatTranslator.end_adf_extension
    :no-index:
.. autofunction:: sphinxcontrib.confluencebuilder.storage.translator.ConfluenceStorageFormatTranslator.start_adf_node
    :no-index:
.. autofunction:: sphinxcontrib.confluencebuilder.storage.translator.ConfluenceStorageFormatTranslator.end_adf_node
    :no-index:
.. autofunction:: sphinxcontrib.confluencebuilder.storage.translator.ConfluenceStorageFormatTranslator.start_ri_attachment
    :no-index:
.. autofunction:: sphinxcontrib.confluencebuilder.storage.translator.ConfluenceStorageFormatTranslator.end_ri_attachment
    :no-index:

.. (sorting) then others

.. autofunction:: sphinxcontrib.confluencebuilder.storage.translator.ConfluenceStorageFormatTranslator.escape_cdata
    :no-index:

.. references ------------------------------------------------------------------

.. _Sphinx.add_node: https://www.sphinx-doc.org/en/master/extdev/appapi.html#sphinx.application.Sphinx.add_node
.. _Sphinx: https://www.sphinx-doc.org/
