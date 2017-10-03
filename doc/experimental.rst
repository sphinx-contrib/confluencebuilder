experimental
============

confluence_experimental_page_hierarchy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set this to True to convert any .rst pages in a toctree into children of the published confluence page.
*Note: you emust also set `master_doc` for this to work*

confluence_experimental_max_depth
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set `confluence_experimental_max_depth` render all toctree imports beyond the supplied depth inline in the page.
For example `confluence_experimental_max_depth=0` will have similar behavior to the 'singlehtml' builder in sphinx.
