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

======================= =====
Type                    Notes
======================= =====
`admonitions`_          Supported
`bibliographic fields`_ Supported
`block quotes`_         Supported
`bullet lists`_         Supported
`citations`_            Supported
`compound paragraph`_   Supported
`container`_            Unsupported.

                        Confluence markup does not permit the use of the
                        ``class`` attribute for tags.
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
`images`_               Supported
`inline markup`_        Supported
`list-table`_           Supported
`literal blocks`_       Supported
`math`_                 Supported with additional system tools.

                        Requires a LaTeX and dvipng/dvisvgm installation.
`parsed literal block`_ Supported
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

*(note: directive options "class" and "name" are ignored as they are not
supported in a Confluence format document)*

Sphinx markup
-------------

.. only:: latex

    .. tabularcolumns:: |p{4cm}|p{12cm}|

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
                        the ``linenos`` option).
`deprecated`_           Supported
`download`_             Supported
`glossary`_             Supported
`hlist`_                Supported
`manpage`_              Supported
`production list`_      Supported
`toctree`_              Supported
`versionadded`_         Supported
`versionchanged`_       Supported
======================= =====

*(note: directive options "class" and "name" are ignored as they are not
supported in a Confluence format document)*

Miscellaneous
-------------

This extension currently does not support the generation of indexed content
(e.g. ``genindex`` or ``modindex``).

This extension does not include support for generating a "Search" document as
Confluence provides its own advanced search capabilities.

.. raw:: latex

    \newpage

Extensions
----------

.. note::

    Atlassian Confluence Builder for Sphinx does not plan to directly support
    external extensions provided outside of `Sphinx's main source repository`_.
    However, changes are considered towards this extension's processing and API
    to make it flexible for other extensions to integrate.

    Developers wishing to integrate an extension with Atlassian Confluence
    Builder can either attempt to add implementation inside the extension
    itself (if permitted and rational), or create a new extension which can bind
    both desired extensions together (e.g. `sphinx-confluence-nbsphinx-test`_).

This extension will attempt to support any extension that is integrated into
Sphinx's repository. The following extensions are currently supported:

.. only:: latex

    .. tabularcolumns:: |p{5cm}|p{11cm}|

================================= =====
Type                              Notes
================================= =====
`sphinx.ext.autodoc`_             Supported*.

                                  While support for autodocs has been included
                                  in this extension, only a limited amount of
                                  examples and testing has been done to verify
                                  its capabilities. If an issue is observed when
                                  using an autodoc feature, please confirm an
                                  expected result using an ``html`` build then
                                  report the issue.
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
                                  documentation sets. At this time, only
                                  document names and standard references are
                                  supported. A generated inventory file is not
                                  published to a Confluence instance.
`sphinx.ext.jsmath`_              Unsupported.

                                  Confluence does not support the injection of
                                  JavaScript into a page in most scenarios.
`sphinx.ext.linkcode`_            Unsupported.

                                  This extension only supports injecting
                                  references for the ``html`` builder.
`sphinx.ext.mathjax`_             Unsupported.

                                  Confluence does not support the injection of
                                  JavaScript into a page in most scenarios.
`sphinx.ext.napoleon`_            Supported
`sphinx.ext.todo`_                Supported
`sphinx.ext.viewcode`_            Unsupported.

                                  This extension only supports injecting
                                  references for the ``html`` builder.
================================= =====

Other
-----

If a feature and/or extension is not listed above, is not working as expected or
brings up another concern, feel free to bring up an issue:

    | Atlassian Confluence Builder for Confluence - Issues
    | https://github.com/sphinx-contrib/confluencebuilder/issues

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
.. _tables: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#tables
.. _toctree: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#table-of-contents
.. _transitions: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#transitions
.. _versionadded: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-versionadded
.. _versionchanged: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-versionchanged
