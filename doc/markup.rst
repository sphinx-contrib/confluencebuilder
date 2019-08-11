markup
======

The following outlines the reStructuredText_/Sphinx_ markup supported by this
extension. The intent of this extension is to support as much markup as possible
that can be rendered on a Confluence instance. Below will identify markup that
has been tested, planned to be implemented in the future or is not compatible
with Confluence.

standard
--------

.. keywords | planned, prospect, supported, unplanned, unsupported

====================== ============= =====
type                   status        notes
====================== ============= =====
admonitions            supported     - `reStructuredText Admonitions`_
bibliographic fields   supported     - `reStructuredText Bibliographic Fields`_
block quotes           supported     - `reStructuredText Block Quotes`_
bullet lists           supported     - `reStructuredText Bullet Lists`_
centered               unsupported   - `Sphinx Centered`_
citations              supported     - `reStructuredText Citations`_
code                   supported     - `Sphinx Code Markup`_
                                     - code-block options ``emphasize-lines``
                                       and ``lines`` as well as highlight option
                                       ``linenothreshold`` are ignored due to
                                       incompatibilities with Confluence's code
                                       block macro.
                                     - Highlighting is limited to languages
                                       defined by the Confluence instance (see
                                       `code block macro`_).
                                     - Pending work to validate/improve code
                                       block options ``caption``, ``encoding``
                                       and ``pyobject``.
compound paragraph     supported     - `reStructuredText Compound Paragraph`_
container              prospect      - `reStructuredText Container`_
definition lists       supported     - `reStructuredText Definition Lists`_
deprecated             supported     - `Sphinx Deprecated`_
download               supported     - `Sphinx Download`_
enumerated lists       supported     - `reStructuredText Enumerated Lists`_
                                     - Only auto-enumerator lists (``#``) are
                                       supported.
epigraph               supported     - `reStructuredText Epigraph`_
footnotes              supported     - `reStructuredText Footnotes`_
glossary               supported     - `Sphinx Glossary`_
highlights             supported     - `reStructuredText Highlights`_
hlist                  unsupported   - `Sphinx Horizontal List`_
hyperlink targets      supported     - `reStructuredText Hyperlink Targets`_
images                 supported     - `reStructuredText Images`_
list table             supported     - `reStructuredText List Table`_
                                     - Argument ``title`` not yet supported.
                                     - Options not supported: ``align``,
                                       ``header-rows``, ``stub-columns`` and
                                       ``widths``.
literal blocks         supported     - `reStructuredText Literal Blocks`_
manpage                supported     - `Sphinx Manpage`_
math                   unplanned     - `reStructuredText Math`_
parsed literal block   supported     - `reStructuredText Parsed Literal Block`_
option lists           supported     - `reStructuredText Option Lists`_
production list        supported     - `Sphinx Production List`_
pull-quote             supported     - `reStructuredText Pull-Quote`_
raw                    supported     - `reStructuredText Raw Data Pass-Through`_
rubric                 supported     - `Sphinx Rubric`_
sections               supported     - `reStructuredText Sections`_
tables                 supported     - `reStructuredText Tables`_
toctree                supported     - `Sphinx TOC Tree Markup`_
                                     - Pending work to validate/improve toctree
                                       options ``caption`` and ``numbered``.
transitions            supported     - `reStructuredText Transitions`_
versionadded           supported     - `Sphinx Version Added`_
versionchanged         supported     - `Sphinx Version Changed`_
====================== ============= =====

*(note: directive options "class" and "name" are ignored)*

extensions
----------

The following extensions are supported:

 - `sphinx.ext.autodoc`_
 - `sphinx.ext.todo`_

other
-----

If a markup type and/or extension is not listed in the above, is not working as
expected or brings up another concern, feel free to bring up an issue:

   | Atlassian Confluence Builder for Confluence - Issues
   | https://github.com/sphinx-contrib/confluencebuilder/issues

.. _code block macro: https://confluence.atlassian.com/confcloud/code-block-macro-724765175.html
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _reStructuredText Admonitions: http://docutils.sourceforge.net/docs/ref/rst/directives.html#admonitions
.. _reStructuredText Bibliographic Fields: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#bibliographic-fields
.. _reStructuredText Block Quotes: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#block-quotes
.. _reStructuredText Bullet Lists: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#bullet-lists
.. _reStructuredText Citations: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#citations
.. _reStructuredText Compound Paragraph: http://docutils.sourceforge.net/docs/ref/rst/directives.html#compound-paragraph
.. _reStructuredText Container: http://docutils.sourceforge.net/docs/ref/rst/directives.html#container
.. _reStructuredText Definition Lists: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#definition-lists
.. _reStructuredText Enumerated Lists: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#enumerated-lists
.. _reStructuredText Footnotes: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#footnotes
.. _reStructuredText Epigraph: http://docutils.sourceforge.net/docs/ref/rst/directives.html#epigraph
.. _reStructuredText Highlights: http://docutils.sourceforge.net/docs/ref/rst/directives.html#highlights
.. _reStructuredText Hyperlink Targets: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#hyperlink-targets
.. _reStructuredText Images: http://docutils.sourceforge.net/docs/ref/rst/directives.html#images
.. _reStructuredText List Table: http://docutils.sourceforge.net/docs/ref/rst/directives.html#list-table
.. _reStructuredText Literal Blocks: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#literal-blocks
.. _reStructuredText Math: http://docutils.sourceforge.net/docs/ref/rst/directives.html#math
.. _reStructuredText Option Lists: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#option-lists
.. _reStructuredText Parsed Literal Block: http://docutils.sourceforge.net/docs/ref/rst/directives.html#parsed-literal-block
.. _reStructuredText Pull-Quote: http://docutils.sourceforge.net/docs/ref/rst/directives.html#pull-quote
.. _reStructuredText Raw Data Pass-Through: http://docutils.sourceforge.net/docs/ref/rst/directives.html#raw-data-pass-through
.. _reStructuredText Sections: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#sections
.. _reStructuredText Tables: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#tables
.. _reStructuredText Transitions: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#transitions
.. _Sphinx: http://www.sphinx-doc.org/
.. _Sphinx Centered: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-centered
.. _Sphinx Code Markup: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-code-block
.. _Sphinx Deprecated: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-deprecated
.. _Sphinx Download: https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#role-download
.. _Sphinx Glossary: https://www.sphinx-doc.org/en/master/glossary.html
.. _Sphinx Paragraph-level Markup: https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
.. _Sphinx Production List: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-productionlist
.. _Sphinx Horizontal List: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-hlist
.. _Sphinx Manpage: https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#role-manpage
.. _Sphinx Rubric: http://docutils.sourceforge.net/docs/ref/rst/directives.html#rubric
.. _Sphinx TOC Tree Markup: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#table-of-contents
.. _Sphinx Version Added: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-versionadded
.. _Sphinx Version Changed: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-versionchanged
.. _sphinx.ext.autodoc: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
.. _sphinx.ext.todo: https://www.sphinx-doc.org/en/master/usage/extensions/todo.html
