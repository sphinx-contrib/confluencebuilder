master
======

* support for sphinx v1.[6-7] has been dropped
* support for xml-rpc has been dropped
* Added support for confluence_single_page

1.2.0 (2020-01-03)
==================

* (note) sphinx v1.[6-7] support for this extension is deprecated
* (note) xml-rpc support for this extension is deprecated
* fixed issue when using hierarchy on sphinx 2.1+ (new citations domain)
* fixed issue with document names with path separators for windows users
* fixed issue with multi-line description signatures (e.g. c++ autodocs)
* fixed issue with processing hidden toctrees
* fixed issue with unicode paths with confluence_publish_subset and python 2.7
* improved formatting for option list arguments
* improved handling and feedback when configured with incorrect publish instance
* improved name management for published assets
* improved reference linking for sphinx domains capability (meth, attr, etc.)
* introduce a series of jira directives
* support 'firstline' parameter in the code block macro
* support base admonition directive
* support confluence 7 series newline management
* support default alignment in sphinx 2.1+
* support document postfixes
* support for generated image assets (asterisk marked)
* support passthrough authentication handlers for rest calls
* support previous/next navigation
* support prompting for publish username
* support sphinx.ext.autosummary extension
* support sphinx.ext.todo extension
* support the math directive
* support toctree's numbered option
* support users injecting cookie data (for authentication) into rest calls

1.1.0 (2019-03-16)
==================

* repackaged release (see sphinx-contrib/confluencebuilder#192)

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
* support linenothreshold option for hightlight directive
* support maximum page depth (nesting documents)
* support the raw directive
* support two-way ssl connections

0.8.0 (2017-12-05)
==================

* fix case where first-publish with 'confluence_master_homepage' fails to
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
* support master_doc option to configure space's homepage
* support removing document titles from page outputs
* support silent page updates

0.6.0 (2017-04-23)
==================

* cleanup module's structure, versions and other minor files
* drop 'confluence' pypi package (embedded xml-rpc support added)
* improve hyperlink and cross-referencing arbitrary locations/documents support
* improve proxy support
* re-support python 3.x series
* support anonymous publishing
* support rest api

0.5.0 (2017-03-31)
==================

* header/footer support
* purging support
* use macros for admonitions
* (note) known issues with python 3.3, 3.4, 3.5 or 3.6 (see
  sphinx-contrib/confluencebuilder#10)

0.4.0 (2017-02-21)
==================

* move from 'confluence' pypi package to 'confluence' pypi package (required for
  publishing). see: https://github.com/pycontribs/confluence

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
