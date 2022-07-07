# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2022 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from os import path
from sphinx.util import docutils
from sphinxcontrib.confluencebuilder.builder import ConfluenceBuilder
from sphinxcontrib.confluencebuilder.config import handle_config_inited
from sphinxcontrib.confluencebuilder.directives import ConfluenceExpandDirective
from sphinxcontrib.confluencebuilder.directives import ConfluenceLatexDirective
from sphinxcontrib.confluencebuilder.directives import ConfluenceMetadataDirective
from sphinxcontrib.confluencebuilder.directives import ConfluenceNewline
from sphinxcontrib.confluencebuilder.directives import ConfluenceToc
from sphinxcontrib.confluencebuilder.directives import JiraDirective
from sphinxcontrib.confluencebuilder.directives import JiraIssueDirective
from sphinxcontrib.confluencebuilder.locale import MESSAGE_CATALOG_NAME
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger
from sphinxcontrib.confluencebuilder.nodes import confluence_metadata
from sphinxcontrib.confluencebuilder.nodes import jira
from sphinxcontrib.confluencebuilder.nodes import jira_issue
from sphinxcontrib.confluencebuilder.reportbuilder import ConfluenceReportBuilder
from sphinxcontrib.confluencebuilder.roles import ConfluenceLatexRole
from sphinxcontrib.confluencebuilder.roles import ConfluenceMentionRole
from sphinxcontrib.confluencebuilder.roles import ConfluenceStatusRole
from sphinxcontrib.confluencebuilder.roles import JiraRole
from sphinxcontrib.confluencebuilder.singlebuilder import SingleConfluenceBuilder

# load autosummary extension if available to add additional nodes
try:
    from sphinx.ext import autosummary
except ImportError:
    autosummary = None

# load imgmath extension if available to handle math configuration options
try:
    from sphinx.ext import imgmath
except ImportError:
    imgmath = None

__version__ = '1.9.0.dev0'


def setup(app):
    ConfluenceLogger.initialize()

    app.require_sphinx('1.8')
    app.add_builder(ConfluenceBuilder)
    app.add_builder(ConfluenceReportBuilder)
    app.add_builder(SingleConfluenceBuilder)

    # register this extension's locale
    package_dir = path.abspath(path.dirname(__file__))
    locale_dir = path.join(package_dir, 'locale')
    app.add_message_catalog(MESSAGE_CATALOG_NAME, locale_dir)

    # ##########################################################################

    # (configuration - essential)
    # Enablement of publishing.
    app.add_config_value('confluence_publish', None, '')
    # PAT to authenticate to Confluence API with.
    app.add_config_value('confluence_publish_token', None, '')
    # API key/password to login to Confluence API with.
    app.add_config_value('confluence_server_pass', None, '')
    # URL of the Confluence instance to publish to.
    app.add_config_value('confluence_server_url', None, '')
    # Username to login to Confluence API with.
    app.add_config_value('confluence_server_user', None, '')
    # Confluence Space to publish to.
    app.add_config_value('confluence_space_key', None, '')

    # (configuration - generic)
    # Add page and section numbers if doctree has :numbered: option
    app.add_config_value('confluence_add_secnumbers', None, 'env')
    # Default alignment for tables, figures, etc.
    app.add_config_value('confluence_default_alignment', None, 'env')
    # Enablement of a generated domain index documents
    app.add_config_value('confluence_domain_indices', None, '')
    # File to get page header information from.
    app.add_config_value('confluence_header_file', None, 'env')
    # Dictionary to pass to header when rendering template
    app.add_config_value('confluence_header_data', None, 'env')
    # File to get page footer information from.
    app.add_config_value('confluence_footer_file', None, 'env')
    # Dictionary to pass to footer when rendering template.
    app.add_config_value('confluence_footer_data', None, 'env')
    # Enablement of a generated search documents
    app.add_config_value('confluence_include_search', None, '')
    # Enablement of the maximum document depth (before inlining).
    app.add_config_value('confluence_max_doc_depth', None, 'env')
    # Enablement of a "page generated" notice.
    app.add_config_value('confluence_page_generation_notice', None, 'env')
    # Enablement of publishing pages into a hierarchy from a root toctree.
    app.add_config_value('confluence_page_hierarchy', None, False)
    # Show previous/next buttons (bottom, top, both, None).
    app.add_config_value('confluence_prev_next_buttons_location', None, 'env')
    # Suffix to put after section numbers, before section name
    app.add_config_value('confluence_secnumber_suffix', None, 'env')
    # Enablement of a "Edit/Show Source" reference on each document
    app.add_config_value('confluence_sourcelink', None, 'env')
    # Enablement of a generated index document
    app.add_config_value('confluence_use_index', None, '')
    # Enablement for toctrees for singleconfluence documents.
    app.add_config_value('singleconfluence_toctree', None, 'singleconfluence')

    # (configuration - publishing)
    # Request for publish password to come from interactive session.
    app.add_config_value('confluence_ask_password', None, '')
    # Request for publish username to come from interactive session.
    app.add_config_value('confluence_ask_user', None, '')
    # Explicitly prevent auto-generation of titles for titleless documents.
    app.add_config_value('confluence_disable_autogen_title', None, '')
    # Explicitly prevent page notifications on update.
    app.add_config_value('confluence_disable_notifications', None, '')
    # Define a series of labels to apply to all published pages.
    app.add_config_value('confluence_global_labels', None, '')
    # Enablement of configuring root as space's homepage.
    app.add_config_value('confluence_root_homepage', None, '')
    # Parent page's name or identifier to publish documents under.
    app.add_config_value('confluence_parent_page', None, '')
    # Perform a dry run of publishing to inspect what publishing will do.
    app.add_config_value('confluence_publish_dryrun', None, '')
    # Publish only new content (no page updates, etc.).
    app.add_config_value('confluence_publish_onlynew', None, '')
    # Postfix to apply to title of published pages.
    app.add_config_value('confluence_publish_postfix', None, 'env')
    # Prefix to apply to published pages.
    app.add_config_value('confluence_publish_prefix', None, 'env')
    # Root page's identifier to publish documents into.
    app.add_config_value('confluence_publish_root', None, '')
    # Enablement of purging legacy child pages from a parent page.
    app.add_config_value('confluence_purge', None, '')
    # Enablement of purging legacy child pages from a root page.
    app.add_config_value('confluence_purge_from_root', None, '')
    # docname-2-title dictionary for title overrides.
    app.add_config_value('confluence_title_overrides', None, 'env')
    # Timeout for network-related calls (publishing).
    app.add_config_value('confluence_timeout', None, '')
    # Whether or not new content should be watched.
    app.add_config_value('confluence_watch', None, '')

    app.add_config_value('confluence_title_hash_root_path', None, 'env')


    # (configuration - advanced publishing)
    # Register additional mime types to be selected for image candidates.
    app.add_config_value('confluence_additional_mime_types', None, 'env')
    # Whether or not labels will be appended instead of overwriting them.
    app.add_config_value('confluence_append_labels', None, '')
    # Forcing all assets to be standalone.
    app.add_config_value('confluence_asset_force_standalone', None, 'env')
    # Tri-state asset handling (auto, force push or disable).
    app.add_config_value('confluence_asset_override', None, '')
    # File/path to Certificate Authority
    app.add_config_value('confluence_ca_cert', None, '')
    # Path to client certificate to use for publishing
    app.add_config_value('confluence_client_cert', None, '')
    # Password for client certificate to use for publishing
    app.add_config_value('confluence_client_cert_pass', None, '')
    # Disable SSL validation with Confluence server.
    app.add_config_value('confluence_disable_ssl_validation', None, '')
    # Ignore adding a titlefix on the index document.
    app.add_config_value('confluence_ignore_titlefix_on_index', None, 'env')
    # Parent page's identifier to publish documents under.
    app.add_config_value('confluence_parent_page_id_check', None, '')
    # Proxy server needed to communicate with Confluence server.
    app.add_config_value('confluence_proxy', None, '')
    # Subset of documents which are allowed to be published.
    app.add_config_value('confluence_publish_allowlist', None, '')
    # Enable debugging for publish requests.
    app.add_config_value('confluence_publish_debug', None, '')
    # Duration (in seconds) to delay each API request.
    app.add_config_value('confluence_publish_delay', None, '')
    # Subset of documents which are denied to be published.
    app.add_config_value('confluence_publish_denylist', None, '')
    # Disable adding `rest/api` to REST requests.
    app.add_config_value('confluence_publish_disable_api_prefix', None, '')
    # Header(s) to use for Confluence REST interaction.
    app.add_config_value('confluence_publish_headers', None, '')
    # Manipulate a requests instance.
    app.add_config_value('confluence_request_session_override', None, '')
    # Authentication passthrough for Confluence REST interaction.
    app.add_config_value('confluence_server_auth', None, '')
    # Cookie(s) to use for Confluence REST interaction.
    app.add_config_value('confluence_server_cookies', None, '')
    # Comment added to confluence version history.
    app.add_config_value('confluence_version_comment', None, '')

    # (configuration - advanced processing)
    # Filename suffix for generated files.
    app.add_config_value('confluence_file_suffix', None, 'env')
    # Translation of docname to a filename.
    app.add_config_value('confluence_file_transform', None, 'env')
    # Configuration for named JIRA Servers
    app.add_config_value('confluence_jira_servers', None, 'env')
    # Translation of a raw language to code block macro language.
    app.add_config_value('confluence_lang_transform', None, 'env')
    # Macro configuration for Confluence-managed LaTeX content.
    app.add_config_value('confluence_latex_macro', None, 'env')
    # Link suffix for generated files.
    app.add_config_value('confluence_link_suffix', None, 'env')
    # Translation of docname to a (partial) URI.
    app.add_config_value('confluence_link_transform', None, 'env')
    # Mappings for documentation mentions to Confluence keys.
    app.add_config_value('confluence_mentions', None, 'env')
    # Inject navigational hints into the documentation.
    app.add_config_value('confluence_navdocs_transform', None, '')
    # Remove a detected title from generated documents.
    app.add_config_value('confluence_remove_title', None, 'env')

    # (configuration - undocumented)
    # Enablement for aggressive descendents search (for purge).
    app.add_config_value('confluence_adv_aggressive_search', None, '')
    # List of node types to ignore if no translator support exists.
    app.add_config_value('confluence_adv_ignore_nodes', None, '')
    # Unknown node handler dictionary for advanced integrations.
    app.add_config_value('confluence_adv_node_handler', None, '')
    # Enablement of permitting raw html blocks to be used in storage format.
    app.add_config_value('confluence_adv_permit_raw_html', None, 'env')
    # List of optional features/macros/etc. restricted for use.
    app.add_config_value('confluence_adv_restricted', None, 'env')
    # Enablement of tracing processed data.
    app.add_config_value('confluence_adv_trace_data', None, '')
    # Do not cap sections to a maximum of six (6) levels.
    app.add_config_value('confluence_adv_writer_no_section_cap', None, 'env')

    # (configuration - deprecated)
    # replaced by confluence_root_homepage
    app.add_config_value('confluence_master_homepage', None, '')
    # replaced by confluence_publish_allowlist
    app.add_config_value('confluence_publish_subset', None, '')
    # replaced by confluence_purge_from_root
    app.add_config_value('confluence_purge_from_master', None, '')
    # replaced by confluence_space_key
    app.add_config_value('confluence_space_name', None, '')

    # ##########################################################################

    # hook onto configuration initialization to finalize its state before
    # passing it to the builder (e.g. handling deprecated options)
    app.connect('config-inited', handle_config_inited)

    # hook on a builder initialization event, to perform additional
    # configuration required when a user is using a confluence builder
    app.connect('builder-inited', confluence_builder_inited)

    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }


def confluence_builder_inited(app):
    """
    invoked when the configured sphinx builder is initialized

    Handling a `builder-inited` event generated from Sphinx.
    """

    # ignore non-confluence builder types
    if not isinstance(app.builder, ConfluenceBuilder):
        return

    # register nodes required by confluence-specific directives
    if not docutils.is_node_registered(confluence_metadata):
        app.add_node(confluence_metadata)
    if not docutils.is_node_registered(jira):
        app.add_node(jira)
    if not docutils.is_node_registered(jira_issue):
        app.add_node(jira_issue)

    # register directives
    app.add_directive('confluence_expand', ConfluenceExpandDirective)
    app.add_directive('confluence_latex', ConfluenceLatexDirective)
    app.add_directive('confluence_metadata', ConfluenceMetadataDirective)
    app.add_directive('confluence_newline', ConfluenceNewline)
    app.add_directive('confluence_toc', ConfluenceToc)
    app.add_directive('jira', JiraDirective)
    app.add_directive('jira_issue', JiraIssueDirective)

    # register roles
    app.add_role('confluence_latex', ConfluenceLatexRole)
    app.add_role('confluence_mention', ConfluenceMentionRole)
    app.add_role('confluence_status', ConfluenceStatusRole)
    app.add_role('jira', JiraRole)

    # inject compatible autosummary nodes if the extension is available/loaded
    if autosummary:
        for ext in app.extensions.values():
            if ext.name == 'sphinx.ext.autosummary':
                app.registry.add_translation_handlers(
                    autosummary.autosummary_table,
                    confluence=(
                        autosummary.autosummary_table_visit_html,
                        autosummary.autosummary_noop,
                    ),
                    singleconfluence=(
                        autosummary.autosummary_table_visit_html,
                        autosummary.autosummary_noop,
                    ),
                )
                app.registry.add_translation_handlers(
                    autosummary.autosummary_toc,
                    confluence=(
                        autosummary.autosummary_toc_visit_html,
                        autosummary.autosummary_noop,
                    ),
                    singleconfluence=(
                        autosummary.autosummary_toc_visit_html,
                        autosummary.autosummary_noop,
                    ),
                )
                break

    # lazy bind sphinx.ext.imgmath to provide configuration options
    #
    # If 'sphinx.ext.imgmath' is not already explicitly loaded, bind it into the
    # setup process to a configurer can use the same configuration options
    # outlined in the sphinx.ext.imgmath in this extension. This applies for
    # Sphinx 1.8 and higher which math support is embedded; for older versions,
    # users will need to explicitly load 'sphinx.ext.mathbase'.
    if imgmath is not None:
        if 'sphinx.ext.imgmath' not in app.config.extensions:
            imgmath.setup(app)

    # remove math-node-migration post-transform as this extension manages both
    # future and legacy math implementations (removing this transform removes
    # a warning notification to the user)
    for transform in app.registry.get_post_transforms():
        if transform.__name__ == 'MathNodeMigrator':
            app.registry.get_post_transforms().remove(transform)
            break
