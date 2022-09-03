Download
========

Sphinx defines a `download directive`_ to link to non-reStructuredText
documents. This extension has the ability to publish these files as attachments
under pages and generate links to these respective attachments. Example markup
is as follows:

.. code-block:: none

    :download:`assets/example.py`

Output
------

This page will host two attachment types, an example Python script as well as a
PDF file. When using the download directive without a label, the extension will
generate a link to the file via Confluence's view-file macro. For example, the
two files should appear with two view-file elements:

:download:`assets/example.py`

:download:`assets/example.pdf`

A user may have a document which links to assets using a label. When a label is
provided, only a link will be generated (instead of a view-file element). For
example, this is a
:download:`link to the example Python script<assets/example.py>` and this is a
:download:`link to the PDF file<assets/example.pdf>`.


.. references ------------------------------------------------------------------

.. _download directive: https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#role-download
