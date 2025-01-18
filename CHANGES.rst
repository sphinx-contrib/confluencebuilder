Development
===========

* Disable use of inlined images for v2 editor pages

2.9.0 (2024-11-11)
==================

* Fixed issue with env-relative assets in sub-folders (e.g. download role)
* Fixed some section references between pages for v2 editor pages

2.8.0 (2024-10-14)
==================

* Fixed issues where various links were broken with singleconfluence
* Improve support with Sphinx v8.1 ``--fail-on-warning`` changes
* Improve support with Sphinx v8.1 ``sphinx.ext.linkcode`` changes
* Introduce the ``confluence-publish-attachment`` event
* Introduce the ``confluence-publish-override-pageid`` event
* Introduce the ``confluence-publish-page`` event

2.7.1 (2024-08-26)
==================

* Fixed project dependency for Sphinx 7.1

2.7.0 (2024-08-25)
==================

* **(note)** ``confluence_file_transform`` support is dropped
* **(note)** ``confluence_link_transform`` support is dropped
* Improve support when using the sphinx_toolbox extension
* Improved support for newer Confluence Cloud code formats
* Introduce the Confluence HTML directive
* Introduce the ``confluence_disable_env_conf`` option
* Support inlined images for v2 editor pages
* Update publisher's user agent to ``SphinxConfluenceBuilder/<version>``

2.6.1 (2024-07-27)
==================

* Support Sphinx's 8.x switch to pathlib

2.6.0 (2024-07-14)
==================

* **(note)** ``confluence_disable_notifications`` is now enabled by default
* **(note)** ``confluence_file_transform`` support is deprecated
* **(note)** ``confluence_link_transform`` support is deprecated
* Fixed inconsistencies with page-meta editor/full-width with singleconfluence
* Fixed issue in Confluence REST v2 API usage (Cloud) where page updates
  may fail when a page has no metadata
* Fixed issue using cleanup modes with Confluence Cloud with large
  attachment/page sets (250+) could block publishing
* Fixed issues where various links were broken with singleconfluence
* Fixed support when using the sphinxcontrib-video extension (v0.2.1+)
* Improve support when using the sphinx-designs extension
* Improve user feedback when operating with a cleaning option enabled
* Introduce the ``confluence-publish-point`` event
* Introduce the ``confluence_api_token`` option
* Introduce the ``confluence_page_search_mode`` option
* REST API calls will retry on select error events (e.g. 5xx errors)
* Replacing ``confluence_lang_transform`` with a new option
  ``confluence_lang_overrides``
* Translator helpers are now public for advanced configurations/extensions

2.5.2 (2024-05-12)
==================

* Fixed issue in Confluence REST v2 API usage (Cloud) where page updates
  may fail when a page has no metadata

2.5.1 (2024-04-06)
==================

* Fixed issue in Confluence REST v2 API usage (Cloud) where edited pages on
  Confluence prevented this extension from publishing updates

2.5.0 (2024-03-31)
==================

* Confluence card directives/roles can be processed with ``linkcheck``
* Fixed issue where an exception could throw without cleanup options set
* Fixed issue where anchor links may fail to work for v2 editor pages
* Fixed issue where generated pages would use incorrect template with an
  explicit v1 editor
* Fixed issue where index/search pages on v1 do not respect width configuration
* Fixed regression where math label anchors would not be created in v1 editor
* Fixed regression where search pages would not be set with a proper space key
* Improve search box alignment on generated search pages
* Initial support for using Confluence REST v2 API (Cloud)
* Provide extended debugging options for publish events
* Replacing ``confluence_publish_disable_api_prefix`` with a new option
  ``confluence_publish_override_api_prefix``
* Simplify autodocs rendering in v2 to make it somewhat usable
* Support custom page notice via ``confluence_page_generation_notice``

2.4.0 (2023-12-14)
==================

* Fixed anchor links between various editor versions and when using MyST
* Fixed issue when using markup in captions when using the v2 editor
* Fixed issue with an editor metadata override may led to unexpected page styles
* Fixed issue with dry-run reporting pages when configure root does not exist
* Fixed regression in processing metadata directives on a page
* Prevent undesired spacing when adding targets in paragraphs with v2 editor
* Support width hints in v2 editor for CSV tables

2.3.0 (2023-09-09)
==================

* **(note)** Final release supporting Python 3.7 (EOL)
* Fixed issue when a project defines a relative CA certificate path
* Fixed issue when a project defines relative publish list files
* Fixed issue where cleanup would remove up-to-date pages on rebuilds
* Fixed triggering rebuilds when select configuration options change
* Fixed select directive/role issues with Sphinx 7.2.x

2.2.0 (2023-07-22)
==================

* Fixed ``confluence_full_width`` issues on Confluence server/DC
* Fixed issue where using ``confluence_full_width`` breaks an editor selection
* Fixed re-publishing issues when certain options change (e.g. parent page)
* Improve support when using the sphinxcontrib-video extension
* Introduce the ``confluence_permit_raw_html`` option
* Provide quirk for CDATA issues on Confluence 8.0.x to 8.2.x
* Support configuring the theme on generated code block macros
* Support page-specific editor and full-width overrides
* Support page-specific parent identifier overrides when publishing

2.1.1 (2023-05-19)
==================

* Ensure source distribution includes the ``LICENSE`` document
* Fixed issue where v2 editor may fail with ``object has no attribute`` error

2.1.0 (2023-05-15)
==================

* Allow users to configure legacy page search mode for cleanup
* Fixed anchor page links with v2 editor
* Fixed document processing issues with Sphinx 6.1.x
* Improve rendering when using sphinxcontrib-needs extension
* Introduce Confluence Smart link directives/roles
* Introduce the Confluence strike role
* Perform an attachment re-upload attempt on an unexpected Confluence 503 error
* Provide fallback styling for code languages with a similar style
* Support Codeberg helper for source links
* Support ``confluence_full_width`` with v1 editor
* Support default-fallback when using ``confluence_lang_transform``
* Support deployment with Python 3.12
* Support publishing only pages with content changes
* Support suppressing extension warnings using Sphinx's ``suppress_warnings``
* Support the ability to configure where orphan pages are stored
* Support the ability to not publish orphan pages

2.0.0 (2023-01-02)
==================

* Fixed issue publishing orphan pages when a publish root is configured
* Fixed issue where captioned code blocks may not be numbered with ``numfig``
* Fixed issue where captioned tables were not be numbered with ``numfig``
* Hierarchy mode is now enabled by default
* Improve look of quote-like directives
* Introduce the Confluence excerpt (macro) directives
* Support Confluence Cloud's "Fabric" (v2) editor
* Support collapsible code blocks
* Support for Python 2.7 has been dropped
* Support for ``confluence_max_doc_depth`` has been dropped
* Support no publishing with an empty ``confluence_publish_allowlist``

1.9.0 (2022-08-21)
==================

* **(note)** Final release supporting Python 2.7
* Allow ``confluence_ca_cert`` to accept a CA-bundle path
* Default publish Intersphinx databases to root documents
* Fixed issue where code blocks may not properly render captions
* Fixed issue where dry-runs may fail with a non-existent root page
* Fixed issue where external references with ampersands would fail to publish
* Fixed issue where labels are missing on first-publish on Confluence server
* Fixed issue where title length limits were not properly enforced
* Improve support for loading local windows CA/root certificates for requests
* Introduce the Confluence emoticon (macro) role
* Introduce the Confluence status (macro) role
* Introduce the Confluence toc (macro) directive
* Introduce the Confluence user mention (macro) role
* Relax domain restrictions for Intersphinx generation
* Support ``confluence_parent_page`` to accept a page identifier
* Support archiving legacy pages (alternative to purging)
* Support configuring configuration options from environment
* Support document-specific reproducible hash injection in a postfix
* Support jinja2 templating on header/footer templates
* Support the ability to disable injecting ``rest/api`` in API endpoint url

1.8.0 (2022-03-27)
==================

* **(note)** ``confluence_max_doc_depth`` support is deprecated (reminder)
* **(note)** (advanced mode) Macro disabling is deprecated
* Add configuration for personal access tokens (to avoid header entry changes)
* Fixed issue where Confluence cloud did not update homepage on a personal space
* Fixed issue where inline internal targets would create an empty link label
* Fixed issue where Jira directives/role could not be substituted
* Improve formatting when processing autodoc content (containers)
* Improve support when using the sphinx-diagrams extension
* Improve table-alignment for markdown
* Introduce the latex directive/role
* removed informational macro styling on figures
* Support rate limiting for publish requests
* Support setting the comment field in page update events
* Support users to render math through available marketplace latex macros

1.7.1 (2021-11-30)
==================

* Fixed regression where publish-root/dryrun modes would fail with an exception

1.7.0 (2021-11-21)
==================

* **(note)** ``confluence_max_doc_depth`` support is deprecated (reminder)
* ``confluence_space_name`` renamed to ``confluence_space_key``
* Brackets will be wrapped around bottom footnote entries
* Fixed issue where links to numbered section would not work
* Fixed issue where publishing could fail without a proxy set for older requests
* Fixed issue where report/wipe commands would fail in Python 2.7
* Fixed regression in timeout option
* Improve dry-run reflecting new attachments to be published
* Improve indentations for line-block content
* Improve support for attached SVG images with length/scaling modifiers
* Improve support for non-pixel length units for images
* Improve support for SVG images without an XML declaration
* Improve support when publishing page updates converted to a new editor
* Improve support when using the sphinx-gallery extension
* Improve support when using the sphinx_toolbox extension
* Improve support when using the sphinxcontrib-mermaid extension
* Improve support when using the sphinxcontrib-needs extension
* Improve support when using the sphinxcontrib-youtube extension
* Improve user feedback on ancestor page update failures (500 errors)
* Improved support for dealing with unreconciled page detections
* Introduce the Jira role
* Introduce the newline directive
* Introduce the page generation notice option (notice for top of documents)
* Introduce the source link option (e.g. "Edit Source" link)
* Prevent issues with extension directives causing errors with other builders
* Provide a configuration hook to override requests session information
* Remove borders on footnote tables
* Support domain indices generation/processing
* Support for leaving resolved toctrees for singleconfluence
* Support genindex generation/processing
* Support search generation
* Support strikethrough through strike role
* Support the consideration of ``confluence_parent_page`` for wipe requests

1.6.0 (2021-09-26)
==================

* **(note)** ``confluence_max_doc_depth`` support is deprecated
* ``confluence_master_homepage`` renamed to ``confluence_root_homepage``
* ``confluence_purge_from_master`` renamed to ``confluence_purge_from_root``
* Always publish without XSRF checks (minimize Confluence instance logging)
* Always strip control characters from content
* Ensure publish events use legacy editor
* Fixed issue where ``sphinx.ext.imgmath`` was forced for non-Confluence builds
* Fixed issue where rubrics were built as headers and not titled paragraphs
* Handle extensions providing Unicode attributes (e.g. ``sphinxcontrib.drawio``)
* Improve formatting when processing markdown content
* Prevent exceptions where third-party extensions provide invalid image uris
* Support rendering explicit newline entries

1.5.0 (2021-05-25)
==================

* Fixed issue where this extension conflicts with docutils's translator attribs
* Fixed issue with ``:doc:<>`` references when using singlebuilder
* Fixed issue with alignment changes in newer Sphinx
* Fixed issue with caption/title changes in newer docutils/Sphinx
* Fixed issue with singlebuilder processing assets
* Fixed issue with table width hints using pixels instead of percentages
* Improvements for getpass handling in msystem-environments
* Support an explicit root page publishing option
* Support custom headers for REST calls

1.4.0 (2021-01-17)
==================

* Fixed issue where a meta node directive would fail the writer stage
* Fixed issue where intersphinx would fail in Python 2.7
* Fixed issue where not all math directive content would be accepted
* Fixed/improved handling of configuration options from command line
* Support for math visual depth adjustments (line alignment)
* Support for numerical figures and references to these figures
* Support late image/download processing (for third-party extensions)

1.3.0 (2020-12-31)
==================

* **(note)** Support for Sphinx v1.[6-7] has been dropped
* **(note)** Support for XML-RPC has been dropped
* Conflicting titles will be automatically adjusted to prevent publishing issues
* Enable page-specific title overrides via confluence_title_overrides
* Ensure configured title postfix is not trimmed in long titles
* Extend language mappings for supported storage format language types
* Fixed a series of scenarios where titles/missing images will fail a build
* Fixed indentation to consistent offset for newer Confluence instances
* Fixed issue when building heading which reference another document
* Fixed issue when processing a download role with a url
* Fixed issue where an anchor target may not generate a proper link
* Fixed issue where ask options would fail in Python 2.7
* Fixed issue where ask options would prompt when not publishing
* Fixed issue where autosummary registration may fail
* Fixed issue where default alignment did not apply to a figure's legend
* Fixed issue where empty pages could not be published
* Fixed issue where links to headers which contain a link would fail
* Fixed issue where literal-marked includes would fail to publish
* Fixed issue where registering this extension caused issues with other builders
* Fixed issue where todo entries would render when disabled in configuration
* Fixed issue with previous-next links not generated for nested pages
* Improved built references by including title (alt) data if set
* Improved code macros rendering a title value when a caption is set
* Improved emphasis handling for autodocs content
* Improved figure/section numbering
* Improved handling unknown code languages to none-styled (instead of Python)
* Improved previous-next button visualization
* Improved publishing when dealing with changing page title casing
* Introduce the expand directive
* Introduce the report command line feature
* Introduce the wipe command line feature
* Promote ``confluence_storage`` over ``confluence`` for raw type
* Support ``:stub-columns:`` option in a list-table directive
* Support disabling titlefix on an index page
* Support for assigning Confluence labels for pages
* Support for both allow and deny lists for published documents
* Support for centered directive
* Support for graphviz extension
* Support for hlist directive
* Support for inheritance-diagram extension
* Support image candidate detection of extra image types for custom instances
* Support publish dry runs
* Support single-page builder
* Support the ``:backlinks:`` option for contents directive
* Support the generation of an inventory file (for intersphinx)
* Support users overriding default alignment
* Support users to force standalone hosting of shared assets
* Support width hints for tables

1.2.0 (2020-01-03)
==================

* **(note)** Sphinx v1.[6-7] support for this extension is deprecated
* **(note)** XML-RPC support for this extension is deprecated
* Fixed issue when using hierarchy on Sphinx 2.1+ (new citations domain)
* Fixed issue with document names with path separators for windows users
* Fixed issue with multi-line description signatures (e.g. C++ autodocs)
* Fixed issue with processing hidden toctrees
* Fixed issue with Unicode paths with ``confluence_publish_subset`` and Python
  2.7
* Improved formatting for option list arguments
* Improved handling and feedback when configured with incorrect publish instance
* Improved name management for published assets
* Improved reference linking for Sphinx domains capability (meth, attr, etc.)
* Introduce a series of Jira directives
* Support ``firstline`` parameter in the code block macro
* Support base admonition directive
* Support Confluence 7 series newline management
* Support default alignment in Sphinx 2.1+
* Support document postfixes
* Support for generated image assets (asterisk marked)
* Support passthrough authentication handlers for REST calls
* Support previous/next navigation
* Support prompting for publish username
* Support ``sphinx.ext.autosummary`` extension
* Support ``sphinx.ext.todo`` extension
* Support the math directive
* Support toctree's numbered option
* Support users injecting cookie data (for authentication) into REST calls

1.1.0 (2019-03-16)
==================

* Repackaged release (see `sphinx-contrib/confluencebuilder#192`_)

1.0.0 (2019-03-14)
==================

* All Confluence-based macros can be restricted by the user
* Block quotes with attribution are styled with Confluence quotes
* Citations/footnotes now have back references
* Enumerated lists now support various styling types
* Fixed issue with enumerated lists breaking build on older Sphinx versions
* Fixed issue with relative-provided header/footer assets
* Fixed issues where table-of-contents may generate broken links
* Improve support with interaction with other extensions
* Improved paragraph indentation
* Initial autodoc support
* Nested tables and spanning cells are now supported
* Provide option for a caller to request a password for publishing documents
* Storage format support (two-pass publishing no longer needed)
* Support for sass/yaml language types
* Support parsed literal content
* Support publishing subset of documents
* Support the download directive
* Support the image/figure directives
* Support the manpage role

0.9.0 (2018-06-02)
==================

* Fixed a series of content escaping issues
* Fixed an issue when purging content would remove just-published pages
* Fixed detailed configuration errors from being hidden
* Improve proxy support for XML-RPC on various Python versions
* Improve support for various Confluence URL configurations
* Improve support in handling literal block languages
* Support automatic title generation for documents (if missing)
* Support ``:linenothreshold:`` option for highlight directive
* Support maximum page depth (nesting documents)
* Support the raw directive
* Support two-way SSL connections

0.8.0 (2017-12-05)
==================

* Fix case where first-publish with ``confluence_master_homepage`` fails to
  configure the space's homepage
* Support page hierarchy
* Improve PyPI cover notes

0.7.0 (2017-11-30)
==================

* Cap headers/sections to six levels for improved visualization
* Fixed REST publishing for encoding issues and Python 3.x (< 3.6) issues
* Improve markup for:

  * Body element lists
  * Citations
  * Definitions
  * Footnotes
  * Inline literals
  * Literal block (code)
  * Rubric
  * Seealso
  * Table
  * Versionmodified

* Re-work generated document references/targets (reference to section names)
* Sanitize output to prevent Confluence errors for certain characters
* Support indentations markup
* Support ``master_doc`` option to configure space's homepage
* Support removing document titles from page outputs
* Support silent page updates

0.6.0 (2017-04-23)
==================

* Cleanup module's structure, versions and other minor files
* Drop ``confluence`` PyPI package (embedded XML-RPC support added)
* Improve hyperlink and cross-referencing arbitrary locations/documents support
* Improve proxy support
* Re-support Python 3.x series
* Support anonymous publishing
* Support REST API

0.5.0 (2017-03-31)
==================

* (note) Known issues with Python 3.3, 3.4, 3.5 or 3.6 (see
  `sphinx-contrib/confluencebuilder#10`_)
* Header/footer support
* Purging support
* Use macros for admonitions

0.4.0 (2017-02-21)
==================

* Move from ``Confluence`` PyPI package to a ``confluence`` PyPI package
  (required for publishing to PyPI; see `pycontribs/confluence`_)

0.3.0 (2017-01-22)
==================

* Adding Travis CI, tox and initial unit testing
* Module now depends on ``future``
* Providing initial support for Python 3

0.2.0 (2016-07-13)
==================

* Moved configuration to the Sphinx config

0.1.1 (2016-07-12)
==================

* Added table support
* Fixed internal links

0.1.0 (2016-07-12)
==================

* Added lists, bullets, formatted text
* Added headings and titles

.. _pycontribs/confluence: https://github.com/pycontribs/confluence
.. _sphinx-contrib/confluencebuilder#10: https://github.com/sphinx-contrib/confluencebuilder/pull/10
.. _sphinx-contrib/confluencebuilder#192: https://github.com/sphinx-contrib/confluencebuilder/issues/192
