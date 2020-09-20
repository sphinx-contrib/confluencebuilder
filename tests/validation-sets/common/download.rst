download
========

Sphinx defines a `download directive`_ to link to non-reST documents. This
extension has the ability to publish these files as attachments under pages and
generate links to these respective attachments.

This page will host two attachment types, an example Python script as well as a
PDF file. When using the download directive without a label, the extension will
generate a link to the file via Confluence's view-file macro. For example, the
two files should appear with two view-file elements:

.. raw:: confluence

   <div style="text-align: center">

:download:`assets/example.py` :download:`assets/example.pdf`

.. raw:: confluence

   </div>

A user may have a document which links to assets using a label. When a label is
provided, only a link will be generated (instead of a view-file element). For
example, this is a
:download:`link to the example Python script<assets/example.py>` and this is a
:download:`link to the PDF file<assets/example.pdf>`.

.. _download directive: http://www.sphinx-doc.org/en/stable/markup/inline.html#role-download
