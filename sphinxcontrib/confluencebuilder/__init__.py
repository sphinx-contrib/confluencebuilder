# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from sphinx.util import docutils

from sphinxcontrib.confluencebuilder.builder import ConfluenceBuilder
from sphinxcontrib.confluencebuilder.config import handle_config_inited
from sphinxcontrib.confluencebuilder.directives import (
    ConfluenceExpandDirective, ConfluenceMetadataDirective, JiraDirective,
    JiraIssueDirective)
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger
from sphinxcontrib.confluencebuilder.nodes import (confluence_metadata, jira,
                                                   jira_issue)
from sphinxcontrib.confluencebuilder.reportbuilder import \
    ConfluenceReportBuilder
from sphinxcontrib.confluencebuilder.singlebuilder import \
    SingleConfluenceBuilder

# load autosummary extension if available to add additional nodes
try:
    from sphinx.ext import autosummary
except ImportError:
    pass

# load imgmath extension if available to handle math configuration options
try:
    from sphinx.ext import imgmath
except ImportError:
    imgmath = None

__version__ = '1.7.0.dev0'

def setup(app):
    ConfluenceLogger.initialize()

    app.require_sphinx('1.8')
    app.add_builder(ConfluenceBuilder)
    app.add_builder(ConfluenceReportBuilder)
    app.add_builder(SingleConfluenceBuilder)

    # Images defined by data uri schemas can be resolved into generated images
    # after a document's post-transformation stage. After a document's doctree
    # has been resolved, re-check for any images that have been translated.
    def assetsDocTreeResolvedHook(app, doctree, docname):
        app.builder.assets.processDocument(doctree, docname, True)
    def builderInitedHook(app):
        if type(app.builder) == ConfluenceBuilder:
            app.connect('doctree-resolved', assetsDocTreeResolvedHook)
    app.connect('builder-inited', builderInitedHook)

    # remove math-node-migration post-transform as this extension manages both
    # future and legacy math implementations (removing this transform removes
    # a warning notification to the user)
    for transform in app.registry.get_post_transforms():
        if transform.__name__ == 'MathNodeMigrator':
            app.registry.get_post_transforms().remove(transform)
            break

    # ##########################################################################

    """(configuration - essential)"""
    """Enablement of publishing."""
    app.add_config_value('confluence_publish', None, False)
    """API key/password to login to Confluence API with."""
    app.add_config_value('confluence_server_pass', None, False)
    """URL of the Confluence instance to publish to."""
    app.add_config_value('confluence_server_url', None, False)
    """Username to login to Confluence API with."""
    app.add_config_value('confluence_server_user', None, False)
    """Confluence Space to publish to."""
    app.add_config_value('confluence_space_name', None, False)

    """(configuration - generic)"""
    """Add page and section numbers if doctree has :numbered: option"""
    app.add_config_value('confluence_add_secnumbers', None, False)
    """Default alignment for tables, figures, etc."""
    app.add_config_value('confluence_default_alignment', None, 'env')
    """File to get page header information from."""
    app.add_config_value('confluence_header_file', None, False)
    """File to get page footer information from."""
    app.add_config_value('confluence_footer_file', None, False)
    """Enablement of the maximum document depth (before inlining)."""
    app.add_config_value('confluence_max_doc_depth', None, False)
    """Enablement of publishing pages into a hierarchy from a root toctree."""
    app.add_config_value('confluence_page_hierarchy', None, False)
    """Show previous/next buttons (bottom, top, both, None)."""
    app.add_config_value('confluence_prev_next_buttons_location', None, False)
    """Suffix to put after section numbers, before section name"""
    app.add_config_value('confluence_secnumber_suffix', None, False)

    """(configuration - publishing)"""
    """Request for publish password to come from interactive session."""
    app.add_config_value('confluence_ask_password', None, False)
    """Request for publish username to come from interactive session."""
    app.add_config_value('confluence_ask_user', None, False)
    """Explicitly prevent auto-generation of titles for titleless documents."""
    app.add_config_value('confluence_disable_autogen_title', None, False)
    """Explicitly prevent page notifications on update."""
    app.add_config_value('confluence_disable_notifications', None, False)
    """Define a series of labels to apply to all published pages."""
    app.add_config_value('confluence_global_labels', None, False)
    """Enablement of configuring root as space's homepage."""
    app.add_config_value('confluence_root_homepage', None, False)
    """Parent page's name to publish documents under."""
    app.add_config_value('confluence_parent_page', None, False)
    """Perform a dry run of publishing to inspect what publishing will do."""
    app.add_config_value('confluence_publish_dryrun', None, '')
    """Publish only new content (no page updates, etc.)."""
    app.add_config_value('confluence_publish_onlynew', None, '')
    """Postfix to apply to title of published pages."""
    app.add_config_value('confluence_publish_postfix', None, False)
    """Prefix to apply to published pages."""
    app.add_config_value('confluence_publish_prefix', None, False)
    """Root page's identifier to publish documents into."""
    app.add_config_value('confluence_publish_root', None, '')
    """Enablement of purging legacy child pages from a parent page."""
    app.add_config_value('confluence_purge', None, False)
    """Enablement of purging legacy child pages from a root page."""
    app.add_config_value('confluence_purge_from_root', None, False)
    """docname-2-title dictionary for title overrides."""
    app.add_config_value('confluence_title_overrides', None, 'env')
    """Timeout for network-related calls (publishing)."""
    app.add_config_value('confluence_timeout', None, False)
    """Whether or not new content should be watched."""
    app.add_config_value('confluence_watch', None, False)

    """(configuration - advanced publishing)"""
    """Register additional mime types to be selected for image candidates."""
    app.add_config_value('confluence_additional_mime_types', None, False)
    """Whether or not labels will be appended instead of overwriting them."""
    app.add_config_value('confluence_append_labels', None, False)
    """Forcing all assets to be standalone."""
    app.add_config_value('confluence_asset_force_standalone', None, False)
    """Tri-state asset handling (auto, force push or disable)."""
    app.add_config_value('confluence_asset_override', None, False)
    """File/path to Certificate Authority"""
    app.add_config_value('confluence_ca_cert', None, False)
    """Path to client certificate to use for publishing"""
    app.add_config_value('confluence_client_cert', None, False)
    """Password for client certificate to use for publishing"""
    app.add_config_value('confluence_client_cert_pass', None, False)
    """Disable SSL validation with Confluence server."""
    app.add_config_value('confluence_disable_ssl_validation', None, False)
    """Ignore adding a titlefix on the index document."""
    app.add_config_value('confluence_ignore_titlefix_on_index', None, False)
    """Parent page's identifier to publish documents under."""
    app.add_config_value('confluence_parent_page_id_check', None, False)
    """Proxy server needed to communicate with Confluence server."""
    app.add_config_value('confluence_proxy', None, False)
    """Subset of documents which are allowed to be published."""
    app.add_config_value('confluence_publish_allowlist', None, False)
    """Subset of documents which are denied to be published."""
    app.add_config_value('confluence_publish_denylist', None, False)
    """Header(s) to use for Confluence REST interaction."""
    app.add_config_value('confluence_publish_headers', None, False)
    """Authentication passthrough for Confluence REST interaction."""
    app.add_config_value('confluence_server_auth', None, False)
    """Cookie(s) to use for Confluence REST interaction."""
    app.add_config_value('confluence_server_cookies', None, False)

    """(configuration - advanced processing)"""
    """Filename suffix for generated files."""
    app.add_config_value('confluence_file_suffix', None, False)
    """Translation of docname to a filename."""
    app.add_config_value('confluence_file_transform', None, False)
    """Configuration for named JIRA Servers"""
    app.add_config_value('confluence_jira_servers', None, True)
    """Translation of a raw language to code block macro language."""
    app.add_config_value('confluence_lang_transform', None, False)
    """Link suffix for generated files."""
    app.add_config_value('confluence_link_suffix', None, False)
    """Translation of docname to a (partial) URI."""
    app.add_config_value('confluence_link_transform', None, False)
    """Remove a detected title from generated documents."""
    app.add_config_value('confluence_remove_title', None, False)

    """(configuration - undocumented)"""
    """Enablement for aggressive descendents search (for purge)."""
    app.add_config_value('confluence_adv_aggressive_search', None, False)
    """Enablement of the children macro for hierarchy mode."""
    app.add_config_value('confluence_adv_hierarchy_child_macro', None, False)
    """List of node types to ignore if no translator support exists."""
    app.add_config_value('confluence_adv_ignore_nodes', None, False)
    """Unknown node handler dictionary for advanced integrations."""
    app.add_config_value('confluence_adv_node_handler', None, '')
    """Enablement of permitting raw html blocks to be used in storage format."""
    app.add_config_value('confluence_adv_permit_raw_html', None, False)
    """List of optional features/macros/etc. restricted for use."""
    app.add_config_value('confluence_adv_restricted', None, False)
    """Enablement of tracing processed data."""
    app.add_config_value('confluence_adv_trace_data', None, False)
    """Do not cap sections to a maximum of six (6) levels."""
    app.add_config_value('confluence_adv_writer_no_section_cap', None, False)

    """(configuration - deprecated)"""
    # replaced by confluence_root_homepage
    app.add_config_value('confluence_master_homepage', None, False)
    # replaced by confluence_publish_allowlist
    app.add_config_value('confluence_publish_subset', None, False)
    # replaced by confluence_purge_from_root
    app.add_config_value('confluence_purge_from_master', None, False)

    # ##########################################################################

    """JIRA directives"""
    """Adds the custom nodes needed for JIRA directives"""
    if not docutils.is_node_registered(jira):
        app.add_node(jira)
    if not docutils.is_node_registered(jira_issue):
        app.add_node(jira_issue)
    """Wires up the directives themselves"""
    app.add_directive('jira', JiraDirective)
    app.add_directive('jira_issue', JiraIssueDirective)

    """Confluence directives"""
    """Adds the custom nodes needed for Confluence directives"""
    if not docutils.is_node_registered(confluence_metadata):
        app.add_node(confluence_metadata)
    """Wires up the directives themselves"""
    app.add_directive('confluence_expand', ConfluenceExpandDirective)
    app.add_directive('confluence_metadata', ConfluenceMetadataDirective)

    # hook onto configuration initialization to finalize its state before
    # passing it to the builder (e.g. handling deprecated options)
    app.connect('config-inited', handle_config_inited)

    # inject the compatible autosummary nodes if the extension is loaded
    def inject_autosummary_notes_hook(app):
        for ext in app.extensions.values():
            if ext.name == 'sphinx.ext.autosummary':
                add_autosummary_nodes(app)
                break
    app.connect('builder-inited', inject_autosummary_notes_hook)

    # lazy bind sphinx.ext.imgmath to provide configuration options
    #
    # If 'sphinx.ext.imgmath' is not already explicitly loaded, bind it into the
    # setup process to a configurer can use the same configuration options
    # outlined in the sphinx.ext.imgmath in this extension. This applies for
    # Sphinx 1.8 and higher which math support is embedded; for older versions,
    # users will need to explicitly load 'sphinx.ext.mathbase'.
    if (imgmath is not None and
            'sphinx.ext.imgmath' not in app.config.extensions):
        def lazy_bind_imgmath(app):
            if app.builder.name in ['confluence', 'singleconfluence']:
                imgmath.setup(app)
        app.connect('builder-inited', lazy_bind_imgmath)

    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }

def add_autosummary_nodes(app):
    """
    register custom nodes from autosummary extension

    The autosummary extensions adds custom nodes to the doctree.
    Add the required translation handlers manually.
    """
    app.registry.add_translation_handlers(
        autosummary.autosummary_table,
        confluence=(
            autosummary.autosummary_table_visit_html,
            autosummary.autosummary_noop)
    )
    app.registry.add_translation_handlers(
        autosummary.autosummary_toc,
        confluence=(
            autosummary.autosummary_toc_visit_html,
            autosummary.autosummary_noop)
    )
