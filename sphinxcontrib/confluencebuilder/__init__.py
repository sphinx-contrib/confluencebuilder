# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from pathlib import Path
from sphinx.util import docutils
from sphinxcontrib.confluencebuilder.builder import ConfluenceBuilder
from sphinxcontrib.confluencebuilder.config import handle_config_inited
from sphinxcontrib.confluencebuilder.config.manager import ConfigManager
from sphinxcontrib.confluencebuilder.directives import ConfluenceDocDirective
from sphinxcontrib.confluencebuilder.directives import ConfluenceExcerptDirective
from sphinxcontrib.confluencebuilder.directives import ConfluenceExcerptIncludeDirective
from sphinxcontrib.confluencebuilder.directives import ConfluenceExpandDirective
from sphinxcontrib.confluencebuilder.directives import ConfluenceHtmlDirective
from sphinxcontrib.confluencebuilder.directives import ConfluenceLatexDirective
from sphinxcontrib.confluencebuilder.directives import ConfluenceLinkDirective
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
from sphinxcontrib.confluencebuilder.roles import ConfluenceDocRole
from sphinxcontrib.confluencebuilder.roles import ConfluenceEmoticonRole
from sphinxcontrib.confluencebuilder.roles import ConfluenceLatexRole
from sphinxcontrib.confluencebuilder.roles import ConfluenceLinkRole
from sphinxcontrib.confluencebuilder.roles import ConfluenceMentionRole
from sphinxcontrib.confluencebuilder.roles import ConfluenceStatusRole
from sphinxcontrib.confluencebuilder.roles import ConfluenceStrikeRole
from sphinxcontrib.confluencebuilder.roles import JiraRole
from sphinxcontrib.confluencebuilder.singlebuilder import SingleConfluenceBuilder
from sphinxcontrib.confluencebuilder.transform import ConfluenceHyperlinkCollector

# load autosummary extension if available to add additional nodes
try:
    from sphinx.ext import autosummary
    has_autosummary = True
except ImportError:
    has_autosummary = False

# load imgmath extension if available to handle math configuration options
try:
    from sphinx.ext import imgmath
    has_imgmath = True
except ImportError:
    has_imgmath = False

__version__ = '2.10.1'


def setup(app):
    ConfluenceLogger.initialize()
    cm = app.config_manager_ = ConfigManager(app)

    app.require_sphinx('7.2')
    app.add_builder(ConfluenceBuilder)
    app.add_builder(ConfluenceReportBuilder)
    app.add_builder(SingleConfluenceBuilder)
    app.add_event('confluence-publish-attachment')
    app.add_event('confluence-publish-override-pageid')
    app.add_event('confluence-publish-page')
    app.add_event('confluence-publish-point')
    app.add_post_transform(ConfluenceHyperlinkCollector)

    # register this extension's locale
    package_dir = Path(__file__).parent.resolve()
    locale_dir = package_dir / 'locale'
    app.add_message_catalog(MESSAGE_CATALOG_NAME, str(locale_dir))

    # ##########################################################################

    # (configuration - essential)
    # Enablement of publishing.
    cm.add_conf_bool('confluence_publish')
    # API token to authenticate to Confluence API with.
    cm.add_conf('confluence_api_token')
    # PAT to authenticate to Confluence API with.
    cm.add_conf('confluence_publish_token')
    # Password to login to Confluence API with.
    cm.add_conf('confluence_server_pass')
    # URL of the Confluence instance to publish to.
    cm.add_conf('confluence_server_url')
    # Username to login to Confluence API with.
    cm.add_conf('confluence_server_user')
    # Confluence Space to publish to.
    cm.add_conf('confluence_space_key')

    # (configuration - generic)
    # Add page and section numbers if doctree has :numbered: option
    cm.add_conf_bool('confluence_add_secnumbers', 'confluence')
    # Specify the color scheme used for displaying code blocks.
    cm.add_conf('confluence_code_block_theme', 'confluence')
    # Default alignment for tables, figures, etc.
    cm.add_conf('confluence_default_alignment', 'confluence')
    # Do not attempt to pull configuration values from the environment.
    cm.add_conf_bool('confluence_disable_env_conf')
    # Enablement of a generated domain index documents
    cm.add_conf('confluence_domain_indices', 'confluence')
    # Confluence editor to target for publication.
    cm.add_conf('confluence_editor', 'confluence')
    # File to get page header information from.
    cm.add_conf('confluence_header_file', 'confluence')
    # Dictionary to pass to header when rendering template
    cm.add_conf('confluence_header_data', 'confluence')
    # File to get page footer information from.
    cm.add_conf('confluence_footer_file', 'confluence')
    # Dictionary to pass to footer when rendering template.
    cm.add_conf('confluence_footer_data', 'confluence')
    # Enablement of a generated search documents
    cm.add_conf_bool('confluence_include_search', 'confluence')
    # Enablement of a "page generated" notice.
    cm.add_conf('confluence_page_generation_notice', 'confluence')
    # Enablement of publishing pages into a hierarchy from a root toctree.
    cm.add_conf_bool('confluence_page_hierarchy', 'confluence')
    # Show previous/next buttons (bottom, top, both, None).
    cm.add_conf('confluence_prev_next_buttons_location', 'confluence')
    # Suffix to put after section numbers, before section name
    cm.add_conf('confluence_secnumber_suffix', 'confluence')
    # Enablement of a "Edit/Show Source" reference on each document
    cm.add_conf('confluence_sourcelink', 'confluence')
    # Enablement of a generated index document
    cm.add_conf_bool('confluence_use_index', 'confluence')
    # Enablement for toctrees for singleconfluence documents.
    cm.add_conf_bool('singleconfluence_toctree', 'singleconfluence')

    # (configuration - publishing)
    # Whether labels will be appended instead of overwriting them.
    cm.add_conf_bool('confluence_append_labels')
    # API mode to use for REST calls.
    cm.add_conf('confluence_api_mode')
    # Request for publish password to come from interactive session.
    cm.add_conf_bool('confluence_ask_password')
    # Request for publish username to come from interactive session.
    cm.add_conf_bool('confluence_ask_user')
    # Enablement of archiving legacy child pages.
    cm.add_conf_bool('confluence_cleanup_archive')
    # Enablement of cleaning legacy child pages from a root page.
    cm.add_conf_bool('confluence_cleanup_from_root')
    # Enablement of purging legacy child pages.
    cm.add_conf_bool('confluence_cleanup_purge')
    # Explicitly prevent page notifications on update.
    cm.add_conf_bool('confluence_disable_notifications')
    # Whether to utilize the full width of a Confluence page.
    cm.add_conf_bool('confluence_full_width', 'confluence')
    # Define a series of labels to apply to all published pages.
    cm.add_conf('confluence_global_labels', 'confluence')
    # Parent page's name or identifier to publish documents under.
    cm.add_conf('confluence_parent_page')
    # Perform a dry run of publishing to inspect what publishing will do.
    cm.add_conf_bool('confluence_publish_dryrun')
    # Postfix to apply to title of published pages.
    cm.add_conf('confluence_publish_postfix', 'confluence')
    # Prefix to apply to published pages.
    cm.add_conf('confluence_publish_prefix', 'confluence')
    # Root page's identifier to publish documents into.
    cm.add_conf_int('confluence_publish_root')
    # Enablement of configuring root as space's homepage.
    cm.add_conf_bool('confluence_root_homepage')
    # Timeout for network-related calls (publishing).
    cm.add_conf_int('confluence_timeout')
    # Whether or not new content should be watched.
    cm.add_conf_bool('confluence_watch')

    # (configuration - advanced publishing)
    # Register additional mime types to be selected for image candidates.
    cm.add_conf('confluence_additional_mime_types', 'confluence')
    # Forcing all assets to be standalone.
    cm.add_conf_bool('confluence_asset_force_standalone', 'confluence')
    # Tri-state asset handling (auto, force push or disable).
    cm.add_conf_bool('confluence_asset_override')
    # File/path to Certificate Authority
    cm.add_conf('confluence_ca_cert')
    # The mode to search for legacy child pages.
    cm.add_conf('confluence_cleanup_search_mode')
    # Path to client certificate to use for publishing
    cm.add_conf('confluence_client_cert')
    # Password for client certificate to use for publishing
    cm.add_conf('confluence_client_cert_pass')
    # Explicitly prevent auto-generation of titles for titleless documents.
    cm.add_conf_bool('confluence_disable_autogen_title')
    # Disable SSL validation with Confluence server.
    cm.add_conf_bool('confluence_disable_ssl_validation')
    # Ignore adding a titlefix on the index document.
    cm.add_conf_bool('confluence_ignore_titlefix_on_index', 'confluence')
    # The mode to search for page contents.
    cm.add_conf('confluence_page_search_mode')
    # Translation to override parent page identifier to publish to.
    cm.add_conf('confluence_parent_override_transform')
    # Proxy server needed to communicate with Confluence server.
    cm.add_conf('confluence_proxy')
    # Subset of documents which are allowed to be published.
    cm.add_conf('confluence_publish_allowlist')
    # Configure debugging for publish requests.
    cm.add_conf('confluence_publish_debug')
    # Duration (in seconds) to delay each API request.
    cm.add_conf('confluence_publish_delay')
    # Subset of documents which are denied to be published.
    cm.add_conf('confluence_publish_denylist')
    # Whether to check for changes on remote before publishing.
    cm.add_conf_bool('confluence_publish_force')
    # Header(s) to use for Confluence REST interaction.
    cm.add_conf('confluence_publish_headers')
    # Whether to publish a generated intersphinx database to the root document
    cm.add_conf_bool('confluence_publish_intersphinx')
    # Publish only new content (no page updates, etc.).
    cm.add_conf_bool('confluence_publish_onlynew')
    # Publish orphan pages to Confluence.
    cm.add_conf_bool('confluence_publish_orphan')
    # Container page to publish orphan pages under.
    cm.add_conf_int('confluence_publish_orphan_container')
    # Override the path prefixes for various REST API requests.
    cm.add_conf('confluence_publish_override_api_prefix')
    # Number of attempts permitted when trying to retry a failed API request
    cm.add_conf('confluence_publish_retry_attempts')
    # Duration (in seconds) between retrying failed API requests
    cm.add_conf('confluence_publish_retry_duration')
    # Manipulate a requests instance.
    cm.add_conf('confluence_request_session_override')
    # Authentication passthrough for Confluence REST interaction.
    cm.add_conf('confluence_server_auth')
    # Cookie(s) to use for Confluence REST interaction.
    cm.add_conf('confluence_server_cookies')
    # docname-2-title dictionary for title overrides.
    cm.add_conf('confluence_title_overrides', 'confluence')
    # Comment added to confluence version history.
    cm.add_conf('confluence_version_comment')

    # (configuration - advanced processing)
    # Filename suffix for generated files.
    cm.add_conf('confluence_file_suffix', 'confluence')
    # Macro configuration for Confluence-managed HTML content.
    cm.add_conf('confluence_html_macro', 'confluence')
    # Configuration for named JIRA Servers
    cm.add_conf('confluence_jira_servers', 'confluence')
    # Translation of a raw language to code block macro language.
    cm.add_conf('confluence_lang_overrides', 'confluence')
    # Macro configuration for Confluence-managed LaTeX content.
    cm.add_conf('confluence_latex_macro', 'confluence')
    # Link suffix for generated files.
    cm.add_conf('confluence_link_suffix', 'confluence')
    # Enable raw math output for MathJax support
    cm.add_conf_bool('confluence_mathjax', 'confluence')
    # Embed page/attachment data into the manifest
    cm.add_conf_bool('confluence_manifest_data')
    # Mappings for documentation mentions to Confluence keys.
    cm.add_conf('confluence_mentions', 'confluence')
    # Inject navigational hints into the documentation.
    cm.add_conf('confluence_navdocs_transform')
    # Enablement of permitting raw html blocks to be used in storage format.
    cm.add_conf('confluence_permit_raw_html', 'confluence')
    # Remove a detected title from generated documents.
    cm.add_conf_bool('confluence_remove_title', 'confluence')

    # (configuration - third-party related)
    # Wrap Mermaid nodes into HTML macros.
    cm.add_conf_bool('confluence_mermaid_html_macro', 'confluence')

    # (configuration - undocumented)
    # Enablement for bulk archiving of packages (for premium environments).
    cm.add_conf_bool('confluence_adv_bulk_archiving')
    # Force override for detected Cloud state.
    cm.add_conf_bool('confluence_adv_cloud')
    # Disable any delays when publishing property updates on Cloud
    cm.add_conf_bool('confluence_adv_disable_cloud_prop_delay')
    # Disable workaround for: https://jira.atlassian.com/browse/CONFCLOUD-74698
    cm.add_conf_bool('confluence_adv_disable_confcloud_74698')
    # Disable workaround for inline-extension anchor injection
    cm.add_conf_bool('confluence_adv_disable_confcloud_ieaj')
    # Disable any attempts to initialize this extension's custom entities.
    cm.add_conf_bool('confluence_adv_disable_init')
    # Flag to permit the use of embedded certificates from requests.
    cm.add_conf_bool('confluence_adv_embedded_certs')
    # List of node types to ignore if no translator support exists.
    cm.add_conf('confluence_adv_ignore_nodes')
    # Add the inline attribute for images (v2 editor)
    cm.add_conf_bool('confluence_adv_inlined_images')
    # Unknown node handler dictionary for advanced integrations.
    cm.add_conf('confluence_adv_node_handler')
    # Permit any string value to be provided as the editor.
    cm.add_conf('confluence_adv_permit_editor', 'confluence')
    # Flag to tweak code-block CDATA EOFs to prevent publishing issues.
    cm.add_conf_bool('confluence_adv_quirk_cdata')
    # List of optional features/macros/etc. restricted for use.
    cm.add_conf('confluence_adv_restricted', 'confluence')
    # Enablement of tracing processed data.
    cm.add_conf_bool('confluence_adv_trace_data')
    # Do not cap sections to a maximum of six (6) levels.
    cm.add_conf_bool('confluence_adv_writer_no_section_cap', 'confluence')

    # (configuration - deprecated)
    # replaced by confluence_cleanup_search_mode
    cm.add_conf_bool('confluence_adv_aggressive_search')
    # replaced by confluence_permit_raw_html
    cm.add_conf_bool('confluence_adv_permit_raw_html')
    # replaced by confluence_lang_overrides
    cm.add_conf('confluence_lang_transform', 'confluence')
    # replaced by confluence_root_homepage
    cm.add_conf('confluence_master_homepage')
    # confluence_parent_page supports both names and identifiers
    cm.add_conf_int('confluence_parent_page_id_check')
    # replaced by confluence_publish_override_api_prefix
    cm.add_conf_bool('confluence_publish_disable_api_prefix')
    # replaced by confluence_publish_allowlist
    cm.add_conf('confluence_publish_subset')
    # replaced by confluence_purge_from_root
    cm.add_conf_bool('confluence_purge_from_master')
    # replaced by confluence_cleanup_from_root
    cm.add_conf_bool('confluence_purge_from_root')
    # replaced by confluence_space_key
    cm.add_conf('confluence_space_name')
    # dropped
    cm.add_conf_int('confluence_max_doc_depth')

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

    # always skip initialization if configured to do so
    if app.config.confluence_adv_disable_init:
        return

    # ignore non-confluence builder types if they have a translator
    # (i.e. a builder that needs to support processing nodes generated
    # from custom directives/roles); this allows other builders such
    # as Sphinx's external link check to not generate warnings about
    # unknown directives/roles, while being flexible for builder that
    # expect to translate but would generate an exception for an unknown
    # node
    if not isinstance(app.builder, ConfluenceBuilder):
        try:
            translator = app.builder.get_translator_class()
        except AttributeError:
            pass
        else:
            if translator:
                return

    # register nodes required by confluence-specific directives
    if not docutils.is_node_registered(confluence_metadata):
        app.add_node(confluence_metadata)
    if not docutils.is_node_registered(jira):
        app.add_node(jira)
    if not docutils.is_node_registered(jira_issue):
        app.add_node(jira_issue)

    # register directives
    app.add_directive('confluence_doc', ConfluenceDocDirective)
    app.add_directive('confluence_excerpt', ConfluenceExcerptDirective)
    app.add_directive('confluence_excerpt_include',
        ConfluenceExcerptIncludeDirective)
    app.add_directive('confluence_expand', ConfluenceExpandDirective)
    app.add_directive('confluence_html', ConfluenceHtmlDirective)
    app.add_directive('confluence_latex', ConfluenceLatexDirective)
    app.add_directive('confluence_link', ConfluenceLinkDirective)
    app.add_directive('confluence_metadata', ConfluenceMetadataDirective)
    app.add_directive('confluence_newline', ConfluenceNewline)
    app.add_directive('confluence_toc', ConfluenceToc)
    app.add_directive('jira', JiraDirective)
    app.add_directive('jira_issue', JiraIssueDirective)

    # register roles
    app.add_role('confluence_doc', ConfluenceDocRole)
    app.add_role('confluence_emoticon', ConfluenceEmoticonRole)
    app.add_role('confluence_latex', ConfluenceLatexRole)
    app.add_role('confluence_link', ConfluenceLinkRole)
    app.add_role('confluence_mention', ConfluenceMentionRole)
    app.add_role('confluence_status', ConfluenceStatusRole)
    app.add_role('confluence_strike', ConfluenceStrikeRole)
    app.add_role('jira', JiraRole)

    # always ignore non-confluence builder types for overrides below
    if not isinstance(app.builder, ConfluenceBuilder):
        return

    # other
    confluence_autosummary_support(app)
    confluence_imgmath_support(app)
    confluence_remove_mathnodemigrator(app)


def confluence_autosummary_support(app):
    """
    inject compatible autosummary nodes if the extension is available/loaded

    Args:
        app: the sphinx application
    """

    if has_autosummary:
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


def confluence_imgmath_support(app):
    """
    lazy bind sphinx.ext.imgmath to provide configuration options

    If 'sphinx.ext.imgmath' is not already explicitly loaded, bind it into the
    setup process to a configurer can use the same configuration options
    outlined in the sphinx.ext.imgmath in this extension.

    Args:
        app: the sphinx application
    """

    if has_imgmath and 'sphinx.ext.imgmath' not in app.config.extensions:
        imgmath.setup(app)


def confluence_remove_mathnodemigrator(app):
    """
    remove math-node-migration post-transform

    Remove math-node-migration post-transform as this extension manages both
    future and legacy math implementations (removing this transform removes
    a warning notification to the user)

    Args:
        app: the sphinx application
    """

    for transform in app.registry.get_post_transforms():
        if transform.__name__ == 'MathNodeMigrator':
            app.registry.get_post_transforms().remove(transform)
            break
