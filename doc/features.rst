Features
========

The following outlines the reStructuredText_/Sphinx_ markup, configuration
entries and more supported by this extension. The intent of this extension is to
support various standard Sphinx features that can be rendered on a Confluence
instance. Below will identify features that have been tested, planned to be
implemented in the future or is not compatible with Confluence.

.. keywords | Planned, Prospect, Supported, Unplanned, Unsupported

reStructuredText markup
-----------------------

.. only:: latex

    .. tabularcolumns:: |p{4cm}|p{12cm}|

.. rst-class:: no-wrap-links

======================= =====
Type                    Notes
======================= =====
`admonitions`_          Supported
`bibliographic fields`_ Supported
`block quotes`_         Supported
`bullet lists`_         Supported
`citations`_            Supported
`compound paragraph`_   Supported
`container`_            Supported
`csv-table`_            Supported
`definition lists`_     Supported
`enumerated lists`_     Limited support.

                        Only auto-enumerator lists (``#``) are supported. Using
                        other types of enumerated lists will be handled as
                        auto-enumerators. This is a limitation in the Confluence
                        markup.
`epigraph`_             Supported
`footnotes`_            Supported
`highlights`_           Supported
`hyperlink targets`_    Supported
`images`_               Limited support.

                        When using a Confluence v2 editor, images cannot be
                        inlined.
`inline markup`_        Supported
`list-table`_           Supported
`literal blocks`_       Supported
`math`_                 Supported with additional system tools.

                        Requires a LaTeX and dvipng/dvisvgm installation.
                        When using a Confluence v2 editor, images cannot be
                        offset to be aligned in a paragraph.
`parsed literal block`_ Limited support.

                        When using a Confluence v2 editor, literal blocks
                        cannot be parsed and the contents will be placed
                        inside a code macro.
`option lists`_         Supported
`pull-quote`_           Supported
`raw`_                  Supported.

                        Use the ``confluence_storage`` format type to inject raw
                        data into a document.
`rubric`_               Supported
`sections`_             Supported
`tables`_               Supported
`transitions`_          Supported
======================= =====

*(note: directive options "class" and "name" are mostly ignored as they are not
supported in a Confluence format document)*

Sphinx markup
-------------

.. only:: latex

    .. tabularcolumns:: |p{4cm}|p{12cm}|

.. rst-class:: no-wrap-links

======================= =====
Type                    Notes
======================= =====
`centered`_             Supported
`code`_                 Limited support.

                        Supported languages (for highlighting) are limited to
                        the languages supported by Confluence's
                        `code block macro`_. This applies to a language defined
                        in a ``code-block`` directive or set through a
                        ``highlight`` directive.

                        The ``code-block`` directive contain the options
                        ``emphasize-lines`` and ``lines`` which are not
                        supported in the Confluence markup. The code block macro
                        only supports a simple line numbers (configurable with
                        the ``linenos`` option; Confluence v1 editor only).

                        When the ``class`` attribute contains ``collapse``, the
                        macro will be configured to be collapsed.
`deprecated`_           Supported
`download`_             Supported
`glossary`_             Supported
`hlist`_                Limited support.

                        When using a Confluence v2 editor, the maximum columns
                        for an hlist is three.
`manpage`_              Supported
`production list`_      Supported
`toctree`_              Supported
`versionadded`_         Supported
`versionchanged`_       Supported
======================= =====

Markdown support
----------------

This extension can support the rendering of Markdown content with the use of
Sphinx with the `MyST Parser`_. Most content can be translated to an
applicable Confluence storage format. However, not all content produced by
MyST Parser will work with this extension. Specifically, any directives that
generate HTML content or users who add raw HTML content to documents are not
accepted by default by this extension. This includes line breaks,
strikethroughs and more. Users may attempt to use the
``confluence_permit_raw_html`` option to help workaround select use cases, but
the use of the option is unsupported. When the option is enabled, published
content may not render as expected or may not be able to be published.

Extensions
----------

This extension will attempt to support any extension that is integrated in
`Sphinx's main source repository`_. The following section shows the status of
each of these extensions:

.. only:: latex

    .. tabularcolumns:: |p{5cm}|p{11cm}|

.. rst-class:: no-wrap-links

================================= =====
Type                              Notes
================================= =====
`sphinx.ext.autodoc`_             Supported
`sphinx.ext.autosectionlabel`_    Supported
`sphinx.ext.autosummary`_         Supported
`sphinx.ext.coverage`_            N/A
`sphinx.ext.doctest`_             Supported
`sphinx.ext.duration`_            Supported
`sphinx.ext.extlinks`_            Supported
`sphinx.ext.githubpages`_         N/A
`sphinx.ext.graphviz`_            Supported
`sphinx.ext.ifconfig`_            Supported
`sphinx.ext.imgconverter`_        N/A
`sphinx.ext.imgmath`_             Supported
`sphinx.ext.inheritance_diagram`_ Supported
`sphinx.ext.intersphinx`_         Limited support.

                                  Users should have no issues when using
                                  external modules via ``intersphinx_mapping``.
                                  When building with publishing enabled, this
                                  extension will generate an ``objects.inv``
                                  inventory file which can be used by other
                                  documentation sets.
`sphinx.ext.jsmath`_              Unsupported.

                                  Confluence does not support the injection of
                                  JavaScript into a page in most scenarios.
`sphinx.ext.linkcode`_            Supported (Sphinx v8.1+)
`sphinx.ext.mathjax`_             Unsupported.

                                  Confluence does not support the injection of
                                  JavaScript into a page in most scenarios.
`sphinx.ext.napoleon`_            Supported
`sphinx.ext.todo`_                Supported
`sphinx.ext.viewcode`_            Unsupported.

                                  This extension only supports injecting
                                  references for the ``html`` builder.
================================= =====

.. _extensions_third_party:

Extensions (Third-party)
------------------------

.. note::

    Support with third-party extensions (if any) may be limited. While an
    extension may work with other builders (such as the ``html`` builder), it
    may be implemented in a way which it cannot be integrated with this
    extension. In addition, some features that an extension may use (e.g. using
    JavaScript) cannot be used with a stock Confluence instance and therefore,
    cannot be supported.

Atlassian Confluence Builder for Sphinx does not guarantee support for
third-party extensions found outside of `Sphinx's main source repository`_.
Changes are considered towards this extension's processing and API to make it
flexible for other extensions to integrate. Also, this extension *may* provide
optional support for select third-party extensions (if permitted and rational),
to help improve user experience.

Developers wishing to integrate a third-party extension with Atlassian
Confluence Builder can either attempt to add implementation inside the
third-party extension itself, propose non-intrusive changes to this extension
or create a new extension which can bind both desired extensions together
(e.g. `sphinx-confluence-nbsphinx-test`_). Any changes directly submitted to be
added into this extension's repository will be limited to the arbitrary
release/development windows of this extension.

.. raw:: latex

    \newpage

The following table shows a most recent state of various third-party extensions
interacting with this extension:

.. only:: latex

    .. tabularcolumns:: |p{5cm}|p{11cm}|

.. rst-class:: longtable no-wrap-links

================================= =====
Type                              Notes
================================= =====
`mlx.traceability`_               Limited support.

                                  Formatting of content may not be as expected.
`sphinx-data-viewer`_             Limited support.

                                  Can render JSON data inside code blocks.
                                  Content has collapse all data or expand all
                                  data, but not parts of the data.
`sphinx-design`_                  Limited support.

                                  Single card support (include header, title,
                                  body and footer). No side-by-side cards,
                                  alignment or extended capabilities such as
                                  images or clickable support. Dropdowns will
                                  function except for pre-expanded directives.
                                  Support for some badges but limited to select
                                  colors supported by Confluence. No extended
                                  support for tabs, button and inline icons.
`sphinx-diagrams`_                Supported
`sphinx-gallery`_                 Supported
`sphinx-inline-tabs`_             Limited support.

                                  Requires a Confluence instance that supports
                                  inlined tabs through the use of a third-party
                                  macro. :lref:`confluence_tab_macro` must be
                                  configured.
`sphinx-needs`_                   Limited support.

                                  Formatting of content may not be as expected.
                                  The ``needs_default_layout`` option may need
                                  to be tailored specifically for a Confluence
                                  build.
`sphinx-tabs`_                    Limited support.

                                  Requires a Confluence instance that supports
                                  inlined tabs through the use of a third-party
                                  macro. :lref:`confluence_tab_macro` must be
                                  configured.

                                  Features such as group tabs are not
                                  supported.

                                  May require an explicit registration for
                                  support with sphinx-tabs:

                                  .. code-block:: python

                                     sphinx_tabs_valid_builders = [
                                         'confluence',
                                         'singleconfluence',
                                     ]

`sphinx-toolbox`_                 Supported
`sphinxcontrib-aafig`_            Supported.

                                  May require configuration of the
                                  ``aafig_format`` option.
`sphinxcontrib-actdiag`_          Limited support.

                                  PNGs only; cannot configure for SVG at this
                                  time.
`sphinxcontrib-blockdiag`_        Limited support.

                                  PNGs only; cannot configure for SVG at this
                                  time.
`sphinxcontrib-drawio`_           Supported
`sphinxcontrib-httpdomain`_       Supported
`sphinxcontrib-kroki`_            Supported
`sphinxcontrib-mermaid`_          Limited support.

                                  Requires a PNG/SVG configuration. Raw/HTML
                                  renders can be used for environments with
                                  HTML macro support.
`sphinxcontrib-nwdiag`_           Limited support.

                                  PNGs only; cannot configure for SVG at this
                                  time.
`sphinxcontrib-openapi`_          Supported
`sphinxcontrib-plantuml`_         Supported.

                                  sphinxcontrib-plantuml provides its own
                                  support for this extension.
`sphinxcontrib-programoutput`_    Supported
`sphinxcontrib-seqdiag`_          Limited support.

                                  PNGs only; cannot configure for SVG at this
                                  time.
`sphinxcontrib-svgbob`_           Supported
`sphinxcontrib-video`_            Supported
`sphinxcontrib-youtube`_          Supported
================================= =====

Other
-----

If a feature or extension is not listed above, is not working as expected or
has another concern, feel free to bring up an issue:

    | Atlassian Confluence Builder for Confluence — Issues
    | https://github.com/sphinx-contrib/confluencebuilder/issues


.. _MyST Parser: https://myst-parser.readthedocs.io/
.. _Sphinx's main source repository: https://github.com/sphinx-doc/sphinx/tree/master/sphinx/ext
.. _Sphinx: https://www.sphinx-doc.org/
.. _admonitions: https://docutils.sourceforge.io/docs/ref/rst/directives.html#admonitions
.. _bibliographic fields: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#bibliographic-fields
.. _block quotes: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#block-quotes
.. _bullet lists: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#bullet-lists
.. _centered: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-centered
.. _citations: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#citations
.. _code block macro: https://support.atlassian.com/confluence-cloud/docs/insert-the-code-block-macro/
.. _code: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-code-block
.. _compound paragraph: https://docutils.sourceforge.io/docs/ref/rst/directives.html#compound-paragraph
.. _container: https://docutils.sourceforge.io/docs/ref/rst/directives.html#container
.. _csv-table: https://docutils.sourceforge.io/docs/ref/rst/directives.html#csv-table
.. _definition lists: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#definition-lists
.. _deprecated: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-deprecated
.. _download: https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#role-download
.. _enumerated lists: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#enumerated-lists
.. _epigraph: https://docutils.sourceforge.io/docs/ref/rst/directives.html#epigraph
.. _extension's issues: https://github.com/sphinx-contrib/confluencebuilder/issues
.. _footnotes: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#footnotes
.. _glossary: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-glossary
.. _highlights: https://docutils.sourceforge.io/docs/ref/rst/directives.html#highlights
.. _hlist: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-hlist
.. _hyperlink targets: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#hyperlink-targets
.. _images: https://docutils.sourceforge.io/docs/ref/rst/directives.html#images
.. _inline markup: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#inline-markup
.. _list-table: https://docutils.sourceforge.io/docs/ref/rst/directives.html#list-table
.. _literal blocks: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#literal-blocks
.. _manpage: https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#role-manpage
.. _manpages_url: https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-manpages_url
.. _math: https://docutils.sourceforge.io/docs/ref/rst/directives.html#math
.. _mlx.traceability: https://melexis.github.io/sphinx-traceability-extension/
.. _nbsphinx: https://nbsphinx.readthedocs.io/
.. _numfig: https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-numfig
.. _numfig_format: https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-numfig_format
.. _option lists: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#option-lists
.. _parsed literal block: https://docutils.sourceforge.io/docs/ref/rst/directives.html#parsed-literal-block
.. _production list: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-productionlist
.. _pull-quote: https://docutils.sourceforge.io/docs/ref/rst/directives.html#pull-quote
.. _raw: https://docutils.sourceforge.io/docs/ref/rst/directives.html#raw-data-pass-through
.. _reStructuredText Math: https://docutils.sourceforge.io/docs/ref/rst/directives.html#math
.. _reStructuredText: https://docutils.sourceforge.io/rst.html
.. _rubric: https://docutils.sourceforge.io/docs/ref/rst/directives.html#rubric
.. _sections: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#sections
.. _sphinx-confluence-nbsphinx-test: https://github.com/jdknight/sphinx-confluence-nbsphinx-test
.. _sphinx-data-viewer: https://sphinx-data-viewer.readthedocs.io/
.. _sphinx-design: https://sphinx-design.readthedocs.io/
.. _sphinx-diagrams: https://pypi.org/project/sphinx-diagrams/
.. _sphinx-gallery: https://sphinx-gallery.github.io/
.. _sphinx-inline-tabs: https://sphinx-inline-tabs.readthedocs.io/
.. _sphinx-needs: https://sphinxcontrib-needs.readthedocs.io/
.. _sphinx-tabs: https://sphinx-tabs.readthedocs.io/
.. _sphinx-toolbox: https://sphinx-toolbox.readthedocs.io/
.. _sphinx.ext.autodoc: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
.. _sphinx.ext.autosectionlabel: https://www.sphinx-doc.org/en/master/usage/extensions/autosectionlabel.html
.. _sphinx.ext.autosummary: https://www.sphinx-doc.org/en/master/usage/extensions/autosummary.html
.. _sphinx.ext.coverage: https://www.sphinx-doc.org/en/master/usage/extensions/coverage.html
.. _sphinx.ext.doctest: https://www.sphinx-doc.org/en/master/usage/extensions/doctest.html
.. _sphinx.ext.duration: https://www.sphinx-doc.org/en/master/usage/extensions/duration.html
.. _sphinx.ext.extlinks: https://www.sphinx-doc.org/en/master/usage/extensions/extlinks.html
.. _sphinx.ext.githubpages: https://www.sphinx-doc.org/en/master/usage/extensions/githubpages.html
.. _sphinx.ext.graphviz: https://www.sphinx-doc.org/en/master/usage/extensions/graphviz.html
.. _sphinx.ext.ifconfig: https://www.sphinx-doc.org/en/master/usage/extensions/ifconfig.html
.. _sphinx.ext.imgconverter: https://www.sphinx-doc.org/en/master/usage/extensions/imgconverter.html
.. _sphinx.ext.imgmath: https://www.sphinx-doc.org/en/master/usage/extensions/math.html#module-sphinx.ext.imgmath
.. _sphinx.ext.inheritance_diagram: https://www.sphinx-doc.org/en/master/usage/extensions/inheritance.html
.. _sphinx.ext.intersphinx: https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
.. _sphinx.ext.jsmath: https://www.sphinx-doc.org/en/master/usage/extensions/math.html#module-sphinx.ext.jsmath
.. _sphinx.ext.linkcode: https://www.sphinx-doc.org/en/master/usage/extensions/linkcode.html
.. _sphinx.ext.mathjax: https://www.sphinx-doc.org/en/master/usage/extensions/math.html#module-sphinx.ext.mathjax
.. _sphinx.ext.napoleon: https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
.. _sphinx.ext.todo: https://www.sphinx-doc.org/en/master/usage/extensions/todo.html
.. _sphinx.ext.viewcode: https://www.sphinx-doc.org/en/master/usage/extensions/viewcode.html
.. _sphinxcontrib-aafig: https://pypi.org/project/sphinxcontrib-aafig/
.. _sphinxcontrib-actdiag: https://pypi.org/project/sphinxcontrib-actdiag/
.. _sphinxcontrib-blockdiag: https://pypi.org/project/sphinxcontrib-blockdiag/
.. _sphinxcontrib-drawio: https://pypi.org/project/sphinxcontrib-drawio/
.. _sphinxcontrib-httpdomain: https://sphinxcontrib-httpdomain.readthedocs.io/
.. _sphinxcontrib-kroki: https://pypi.org/project/sphinxcontrib-kroki/
.. _sphinxcontrib-mermaid: https://pypi.org/project/sphinxcontrib-mermaid/
.. _sphinxcontrib-nwdiag: https://pypi.org/project/sphinxcontrib-nwdiag/
.. _sphinxcontrib-openapi: https://sphinxcontrib-openapi.readthedocs.io/
.. _sphinxcontrib-plantuml: https://pypi.org/project/sphinxcontrib-plantuml/
.. _sphinxcontrib-programoutput: https://sphinxcontrib-programoutput.readthedocs.io/
.. _sphinxcontrib-seqdiag: https://pypi.org/project/sphinxcontrib-seqdiag/
.. _sphinxcontrib-svgbob: https://pypi.org/project/sphinxcontrib-svgbob/
.. _sphinxcontrib-video: https://pypi.org/project/sphinxcontrib-video/
.. _sphinxcontrib-youtube: https://pypi.org/project/sphinxcontrib-youtube/
.. _tables: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#tables
.. _toctree: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#table-of-contents
.. _transitions: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#transitions
.. _versionadded: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-versionadded
.. _versionchanged: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-versionchanged
