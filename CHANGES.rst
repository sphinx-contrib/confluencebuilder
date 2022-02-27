Development
===========

* add configuration for personal access tokens (to avoid header entry changes)
* fixed issue where confluence cloud did not update homepage on a personal space
* fixed issue where jira directives/role could not be substituted
* improve support when using the sphinx-diagrams extension
* introduce the latex directive/role
* removed informational macro styling on figures
* support rate limiting for publish requests
* support users to render math through available marketplace latex macros

1.7.1 (2021-11-30)
==================

* fixed regression where publish-root/dryrun modes would fail with an exception

1.7.0 (2021-11-21)
==================

* **(note)** ``confluence_max_doc_depth`` support is deprecated (reminder)
* ``confluence_space_name`` renamed to ``confluence_space_key``
* brackets will be wrapped around bottom footnote entries
* fixed issue where links to numbered section would not work
* fixed issue where publishing could fail without a proxy set for older requests
* fixed issue where report/wipe commands would fail in python 2.7
* fixed regression in timeout option
* improve dry-run reflecting new attachments to be published
* improve indentations for line-block content
* improve support for attached svg images with length/scaling modifiers
* improve support for non-pixel length units for images
* improve support for svg images without an xml declaration
* improve support when publishing page updates converted to a new editor
* improve support when using the sphinx-gallery extension
* improve support when using the sphinx_toolbox extension
* improve support when using the sphinxcontrib-mermaid extension
* improve support when using the sphinxcontrib-needs extension
* improve support when using the sphinxcontrib-youtube extension
* improve user feedback on ancestor page update failures (500 errors)
* improved support for dealing with unreconciled page detections
* introduce the jira role
* introduce the newline directive
* introduce the page generation notice option (notice for top of documents)
* introduce the source link option (e.g. "Edit Source" link)
* prevent issues with extension directives causing errors with other builders
* provide a configuration hook to override requests session information
* remove borders on footnote tables
* support domain indices generation/processing
* support for leaving resolved toctrees for singleconfluence
* support genindex generation/processing
* support search generation
* support strikethrough through strike role
* support the consideration of ``confluence_parent_page`` for wipe requests

1.6.0 (2021-09-26)
==================

* **(note)** ``confluence_max_doc_depth`` support is deprecated
* ``confluence_master_homepage`` renamed to ``confluence_root_homepage``
* ``confluence_purge_from_master`` renamed to ``confluence_purge_from_root``
* always publish without xsrf checks (minimize confluence instance logging)
* always strip control characters from content
* ensure publish events use legacy editor
* fixed issue where ``sphinx.ext.imgmath`` was forced for non-confluence builds
* fixed issue where rubrics were built as headers and not titled paragraphs
* handle extensions providing unicode attributes (e.g. ``sphinxcontrib.drawio``)
* improve formatting when processing markdown content
* prevent exceptions where third-party extensions provide invalid image uris
* support rendering explicit newline entries

1.5.0 (2021-05-25)
==================

* fixed issue where this extension conflicts with docutils's translator attribs
* fixed issue with ``:doc:<>`` references when using singlebuilder
* fixed issue with alignment changes in newer sphinx
* fixed issue with caption/title changes in newer docutils/sphinx
* fixed issue with singlebuilder processing assets
* fixed issue with table width hints using pixels instead of percentages
* improvements for getpass handling in msystem-environments
* support an explicit root page publishing option
* support custom headers for rest calls

1.4.0 (2021-01-17)
==================

* fixed issue where a meta node directive would fail the writer stage
* fixed issue where intersphinx would fail in python 2.7
* fixed issue where not all math directive content would be accepted
* fixed/improved handling of configuration options from command line
* support for math visual depth adjustments (line alignment)
* support for numerical figures and references to these figures
* support late image/download processing (for third-party extensions)

1.3.0 (2020-12-31)
==================

* **(note)** support for sphinx v1.[6-7] has been dropped
* **(note)** support for xml-rpc has been dropped
* conflicting titles will be automatically adjusted to prevent publishing issues
* enable page-specific title overrides via confluence_title_overrides
* ensure configured title postfix is not trimmed in long titles
* extend language mappings for supported storage format language types
* fixed a series of scenarios where titles/missing images will fail a build
* fixed indentation to consistent offset for newer confluence instances
* fixed issue when building heading which reference another document
* fixed issue when processing a download role with a url
* fixed issue where an anchor target may not generate a proper link
* fixed issue where ask options would fail in python 2.7
* fixed issue where ask options would prompt when not publishing
* fixed issue where autosummary registration may fail
* fixed issue where default alignment did not apply to a figure's legend
* fixed issue where empty pages could not be published
* fixed issue where links to headers which contain a link would fail
* fixed issue where literal-marked includes would fail to publish
* fixed issue where registering this extension caused issues with other builders
* fixed issue where todo entries would render when disabled in configuration
* fixed issue with previous-next links not generated for nested pages
* improved built references by including title (alt) data if set
* improved code macros rendering a title value when a caption is set
* improved emphasis handling for autodocs content
* improved figure/section numbering
* improved handling unknown code languages to none-styled (instead of python)
* improved previous-next button visualization
* improved publishing when dealing with changing page title casing
* introduce the expand directive
* introduce the report command line feature
* introduce the wipe command line feature
* promote ``confluence_storage`` over ``confluence`` for raw type
* support ``:stub-columns:`` option in a list-table directive
* support disabling titlefix on an index page
* support for assigning confluence labels for pages
* support for both allow and deny lists for published documents
* support for centered directive
* support for graphviz extension
* support for hlist directive
* support for inheritance-diagram extension
* support image candidate detection of extra image types for custom instances
* support publish dry runs
* support single-page builder
* support the ``:backlinks:`` option for contents directive
* support the generation of an inventory file (for intersphinx)
* support users overriding default alignment
* support users to force standalone hosting of shared assets
* support width hints for tables

1.2.0 (2020-01-03)
==================

* **(note)** sphinx v1.[6-7] support for this extension is deprecated
* **(note)** xml-rpc support for this extension is deprecated
* fixed issue when using hierarchy on sphinx 2.1+ (new citations domain)
* fixed issue with document names with path separators for windows users
* fixed issue with multi-line description signatures (e.g. c++ autodocs)
* fixed issue with processing hidden toctrees
* fixed issue with unicode paths with ``confluence_publish_subset`` and python
  2.7
* improved formatting for option list arguments
* improved handling and feedback when configured with incorrect publish instance
* improved name management for published assets
* improved reference linking for sphinx domains capability (meth, attr, etc.)
* introduce a series of jira directives
* support ``firstline`` parameter in the code block macro
* support base admonition directive
* support confluence 7 series newline management
* support default alignment in sphinx 2.1+
* support document postfixes
* support for generated image assets (asterisk marked)
* support passthrough authentication handlers for rest calls
* support previous/next navigation
* support prompting for publish username
* support ``sphinx.ext.autosummary`` extension
* support ``sphinx.ext.todo`` extension
* support the math directive
* support toctree's numbered option
* support users injecting cookie data (for authentication) into rest calls

1.1.0 (2019-03-16)
==================

* repackaged release (see `sphinx-contrib/confluencebuilder#192`_)

1.0.0 (2019-03-14)
==================

* all confluence-based macros can be restricted by the user
* block quotes with attribution are styled with confluence quotes
* citations/footnotes now have back references
* enumerated lists now support various styling types
* fixed issue with enumerated lists breaking build on older sphinx versions
* fixed issue with relative-provided header/footer assets
* fixed issues where table-of-contents may generate broken links
* improve support with interaction with other extensions
* improved paragraph indentation
* initial autodoc support
* nested tables and spanning cells are now supported
* provide option for a caller to request a password for publishing documents
* storage format support (two-pass publishing no longer needed)
* support for sass/yaml language types
* support parsed literal content
* support publishing subset of documents
* support the download directive
* support the image/figure directives
* support the manpage role

0.9.0 (2018-06-02)
==================

* fixed a series of content escaping issues
* fixed an issue when purging content would remove just-published pages
* fixed detailed configuration errors from being hidden
* improve proxy support for xml-rpc on various python versions
* improve support for various confluence url configurations
* improve support in handling literal block languages
* support automatic title generation for documents (if missing)
* support ``:linenothreshold:`` option for highlight directive
* support maximum page depth (nesting documents)
* support the raw directive
* support two-way ssl connections

0.8.0 (2017-12-05)
==================

* fix case where first-publish with ``confluence_master_homepage`` fails to
  configure the space's homepage
* support page hierarchy
* improve pypi cover notes

0.7.0 (2017-11-30)
==================

* cap headers/sections to six levels for improved visualization
* fixed rest publishing for encoding issues and python 3.x (< 3.6) issues
* improve markup for:

  * body element lists
  * citations
  * definitions
  * footnotes
  * inline literals
  * literal block (code)
  * rubric
  * seealso
  * table
  * versionmodified

* re-work generated document references/targets (reference to section names)
* sanitize output to prevent confluence errors for certain characters
* support indentations markup
* support ``master_doc`` option to configure space's homepage
* support removing document titles from page outputs
* support silent page updates

0.6.0 (2017-04-23)
==================

* cleanup module's structure, versions and other minor files
* drop ``confluence`` pypi package (embedded xml-rpc support added)
* improve hyperlink and cross-referencing arbitrary locations/documents support
* improve proxy support
* re-support python 3.x series
* support anonymous publishing
* support rest api

0.5.0 (2017-03-31)
==================

* (note) known issues with python 3.3, 3.4, 3.5 or 3.6 (see
  `sphinx-contrib/confluencebuilder#10`_)
* header/footer support
* purging support
* use macros for admonitions

0.4.0 (2017-02-21)
==================

* move from ``Confluence`` pypi package to a ``confluence`` pypi package
  (required for publishing to pypi; see `pycontribs/confluence`_)

0.3.0 (2017-01-22)
==================

* adding travis ci, tox and initial unit testing
* module now depends on ``future``
* providing initial support for python 3

0.2.0 (2016-07-13)
==================

* moved configuration to the sphinx config

0.1.1 (2016-07-12)
==================

* added table support
* fixed internal links

0.1.0 (2016-07-12)
==================

* added lists, bullets, formatted text
* added headings and titles

.. _pycontribs/confluence: https://github.com/pycontribs/confluence
.. _sphinx-contrib/confluencebuilder#10: https://github.com/sphinx-contrib/confluencebuilder/pull/10
.. _sphinx-contrib/confluencebuilder#192: https://github.com/sphinx-contrib/confluencebuilder/issues/192
