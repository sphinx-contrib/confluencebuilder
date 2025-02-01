# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from pathlib import Path
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluenceApiModeConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluenceCleanupSearchModeConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluenceClientCertBadTupleConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluenceClientCertMissingCertConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluenceConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluenceDefaultAlignmentConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluenceDomainIndicesConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluenceEditorConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluenceFooterFileConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluenceGlobalLabelsConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluenceHeaderFileConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluenceJiraServersConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluenceLatexMacroInvalidConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluenceLatexMacroMissingKeysConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluencePageGenerationNoticeConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluencePageSearchModeConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluenceParentPageConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluencePermitRawHtmlConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluencePrevNextButtonsLocationConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluencePublishCleanupConflictConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluencePublishConflictPublishPointConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluencePublishDebugConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluencePublishListConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluencePublishMissingParentPageConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluencePublishMissingServerUrlConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluencePublishMissingSpaceKeyConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluencePublishMissingUsernameAskConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluencePublishMissingUsernameAuthConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluencePublishMissingUsernamePassConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluenceServerAuthConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluenceSourcelinkRequiredConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluenceSourcelinkReservedConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluenceSourcelinkTypeConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluenceSourcelinkUrlConfigError
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluenceTimeoutConfigError
from sphinxcontrib.confluencebuilder.config.notifications import deprecated
from sphinxcontrib.confluencebuilder.config.notifications import warnings
from sphinxcontrib.confluencebuilder.config.validation import ConfigurationValidation
from sphinxcontrib.confluencebuilder.debug import PublishDebug
from sphinxcontrib.confluencebuilder.std.confluence import API_MODES
from sphinxcontrib.confluencebuilder.std.confluence import EDITORS
from sphinxcontrib.confluencebuilder.util import handle_cli_file_subset
from requests.auth import AuthBase
import os


def validate_configuration(builder):
    """
    validate a builder's configuration state

    This call will check if the provided builder's configuration has any issues
    with the existing configuration. For errors in the existing configuration,
    an `ConfluenceConfigError` exception will be thrown.

    In addition to errors, this call will also generate warning messages on
    other configuration issues such as deprecated configurations.

    Args:
        builder: the builder state to validate a configuration on
    """

    config = builder.config
    env = builder.app.env
    validator = ConfigurationValidation(builder)

    # ##################################################################

    # confluence_add_secnumbers
    validator.conf('confluence_add_secnumbers') \
             .bool()

    # ##################################################################

    # confluence_additional_mime_types
    validator.conf('confluence_additional_mime_types') \
             .strings(no_space=True)

    # ##################################################################

    # confluence_adv_aggressive_search
    validator.conf('confluence_adv_aggressive_search') \
             .bool()

    # ##################################################################

    # confluence_adv_bulk_archiving
    validator.conf('confluence_adv_bulk_archiving') \
             .bool()

    # ##################################################################

    # confluence_adv_permit_editor
    validator.conf('confluence_adv_permit_editor') \
             .bool()

    # ##################################################################

    # confluence_adv_permit_raw_html
    validator.conf('confluence_adv_permit_raw_html') \
             .bool()

    # ##################################################################

    # confluence_adv_trace_data
    validator.conf('confluence_adv_trace_data') \
             .bool()

    # ##################################################################

    # confluence_adv_writer_no_section_cap
    validator.conf('confluence_adv_writer_no_section_cap') \
             .bool()

    # ##################################################################

    # confluence_api_mode
    validator.conf('confluence_api_mode') \
             .string()

    if config.confluence_api_mode:
        if config.confluence_api_mode not in API_MODES:
            modes = '\n - '.join(API_MODES)
            raise ConfluenceApiModeConfigError(modes)

    # ##################################################################

    # confluence_api_token
    validator.conf('confluence_api_token') \
             .string()

    # ##################################################################

    # confluence_append_labels
    validator.conf('confluence_append_labels') \
             .bool()

    # ##################################################################

    # confluence_ask_password
    validator.conf('confluence_ask_password') \
             .bool()

    # ##################################################################

    # confluence_ask_user
    validator.conf('confluence_ask_user') \
             .bool()

    # ##################################################################

    # confluence_asset_force_standalone
    validator.conf('confluence_asset_force_standalone') \
             .bool()

    # ##################################################################

    # confluence_asset_override
    validator.conf('confluence_asset_override') \
             .bool()

    # ##################################################################

    validator.conf('confluence_ca_cert') \
             .path()

    # ##################################################################

    # confluence_cleanup_archive
    validator.conf('confluence_cleanup_archive') \
             .bool()

    # ##################################################################

    # confluence_cleanup_from_root
    validator.conf('confluence_cleanup_from_root') \
             .bool()

    # ##################################################################

    # confluence_cleanup_purge
    validator.conf('confluence_cleanup_purge') \
             .bool()

    # ##################################################################

    # confluence_cleanup_search_mode
    try:
        validator.conf('confluence_cleanup_search_mode').matching(
            'direct',
            'direct-aggressive',
            'search',
            'search-aggressive',
        )
    except ConfluenceConfigError as ex:
        raise ConfluenceCleanupSearchModeConfigError(ex) from ex

    # ##################################################################

    if config.confluence_client_cert is not None:
        client_cert = config.confluence_client_cert
        if isinstance(client_cert, tuple):
            cert_files = client_cert
        else:
            cert_files = (client_cert, None)

        if len(cert_files) != 2:
            raise ConfluenceClientCertBadTupleConfigError

        for cert in cert_files:
            if cert and not Path(env.srcdir, cert).is_file():
                raise ConfluenceClientCertMissingCertConfigError(cert)

    # ##################################################################

    # confluence_client_cert_pass
    validator.conf('confluence_client_cert_pass') \
             .string()

    # ##################################################################

    # confluence_code_block_theme
    validator.conf('confluence_code_block_theme') \
        .string()

    # ##################################################################

    # confluence_default_alignment
    try:
        validator.conf('confluence_default_alignment') \
                 .matching('left', 'center', 'right')
    except ConfluenceConfigError as ex:
        raise ConfluenceDefaultAlignmentConfigError(ex) from ex

    # ##################################################################

    # confluence_disable_autogen_title
    validator.conf('confluence_disable_autogen_title') \
             .bool()

    # ##################################################################

    # confluence_disable_notifications
    validator.conf('confluence_disable_notifications') \
             .bool()

    # ##################################################################

    # confluence_disable_ssl_validation
    validator.conf('confluence_disable_ssl_validation') \
             .bool()

    # ##################################################################

    # confluence_domain_indices
    try:
        validator.conf('confluence_domain_indices').bool()
    except ConfluenceConfigError:
        try:
            validator.conf('confluence_domain_indices').strings()
        except ConfluenceConfigError as ex:
            raise ConfluenceDomainIndicesConfigError from ex

    # ##################################################################

    # confluence_editor
    validator.conf('confluence_editor') \
             .string()

    if config.confluence_editor:
        if not config.confluence_adv_permit_editor:
            if config.confluence_editor not in EDITORS:
                raise ConfluenceEditorConfigError('\n - '.join(EDITORS))

    # ##################################################################

    # confluence_file_suffix
    validator.conf('confluence_file_suffix') \
             .string()

    # ##################################################################

    # confluence_footer_file
    try:
        validator.conf('confluence_footer_file') \
                 .file()
    except ConfluenceConfigError as ex:
        raise ConfluenceFooterFileConfigError(ex) from ex

    # ##################################################################

    # confluence_full_width
    validator.conf('confluence_full_width') \
             .bool()

    # ##################################################################

    # confluence_global_labels
    try:
        validator.conf('confluence_global_labels') \
                 .strings(no_space=True)
    except ConfluenceConfigError as ex:
        raise ConfluenceGlobalLabelsConfigError(ex) from ex

    # ##################################################################

    # confluence_header_file
    try:
        validator.conf('confluence_header_file') \
                 .file()
    except ConfluenceConfigError as ex:
        raise ConfluenceHeaderFileConfigError(ex) from ex

    # ##################################################################

    # confluence_html_macro
    validator.conf('confluence_html_macro') \
             .string()

    # ##################################################################

    # confluence_ignore_titlefix_on_index
    validator.conf('confluence_ignore_titlefix_on_index') \
             .bool()

    # ##################################################################

    # confluence_include_search
    validator.conf('confluence_include_search') \
             .bool()

    # ##################################################################

    # confluence_jira_servers
    if config.confluence_jira_servers is not None:
        issue = False
        jira_servers = config.confluence_jira_servers

        if not isinstance(jira_servers, dict):
            issue = True
        else:
            for name, info in jira_servers.items():
                if not isinstance(name, str):
                    issue = True
                    break

                if not isinstance(info, dict):
                    issue = True
                    break

                jira_id = info.get('id')
                jira_name = info.get('name')

                if not (isinstance(jira_id, str) and
                        isinstance(jira_name, str)):
                    issue = True
                    break

        if issue:
            raise ConfluenceJiraServersConfigError

    # ##################################################################

    # confluence_lang_overrides
    try:
        validator.conf('confluence_lang_overrides').dict_str_str()
    except ConfluenceConfigError:
        validator.conf('confluence_lang_overrides').callable_()

    # ##################################################################

    # confluence_latex_macro
    try:
        validator.conf('confluence_latex_macro').string()
    except ConfluenceConfigError as ex:
        try:
            validator.conf('confluence_latex_macro').dict_str_str()

        except ConfluenceConfigError as ex:
            raise ConfluenceLatexMacroInvalidConfigError from ex

        if config.confluence_latex_macro:
            conf_keys = config.confluence_latex_macro.keys()

            required_keys = [
                'block-macro',
                'inline-macro',
            ]

            if not all(name in conf_keys for name in required_keys):
                keys_str = '\n - '.join(required_keys)
                raise ConfluenceLatexMacroMissingKeysConfigError(keys_str) \
                    from ex

    # ##################################################################

    # confluence_link_suffix
    validator.conf('confluence_link_suffix') \
             .string()

    # ##################################################################

    # confluence_mentions
    validator.conf('confluence_mentions') \
             .dict_str_str()

    # ##################################################################

    # confluence_page_search_mode
    try:
        validator.conf('confluence_page_search_mode').matching(
            'default',
            'content',
            'search',
        )
    except ConfluenceConfigError as ex:
        raise ConfluencePageSearchModeConfigError(ex) from ex

    # ##################################################################

    # confluence_root_homepage
    validator.conf('confluence_root_homepage') \
             .bool()

    # ##################################################################

    # confluence_navdocs_transform
    validator.conf('confluence_navdocs_transform') \
             .callable_()

    # ##################################################################

    # confluence_parent_override_transform
    validator.conf('confluence_parent_override_transform') \
             .callable_()

    # ##################################################################

    try:
        validator.conf('confluence_parent_page').string()
    except ConfluenceConfigError:
        try:
            validator.conf('confluence_parent_page').int_(positive=True)
        except ConfluenceConfigError as ex:
            raise ConfluenceParentPageConfigError from ex

    # ##################################################################

    validator.conf('confluence_parent_page_id_check') \
             .int_(positive=True)

    # ##################################################################

    # confluence_page_hierarchy
    validator.conf('confluence_page_hierarchy') \
             .bool()

    # ##################################################################

    # confluence_page_generation_notice
    try:
        validator.conf('confluence_page_generation_notice').bool()
    except ConfluenceConfigError:
        try:
            validator.conf('confluence_page_generation_notice').string()
        except ConfluenceConfigError as ex:
            raise ConfluencePageGenerationNoticeConfigError from ex

    # ##################################################################

    # confluence_permit_raw_html
    try:
        validator.conf('confluence_permit_raw_html').bool()
    except ConfluenceConfigError:
        try:
            validator.conf('confluence_permit_raw_html').string()
        except ConfluenceConfigError as ex:
            raise ConfluencePermitRawHtmlConfigError from ex

    # ##################################################################

    # confluence_prev_next_buttons_location
    try:
        validator.conf('confluence_prev_next_buttons_location') \
                 .matching('bottom', 'both', 'top')
    except ConfluenceConfigError as ex:
        raise ConfluencePrevNextButtonsLocationConfigError(ex) from ex

    # ##################################################################

    # confluence_proxy
    validator.conf('confluence_proxy') \
             .string()

    # ##################################################################

    # confluence_publish_allowlist
    # confluence_publish_denylist
    publish_list_options = [
        'confluence_publish_allowlist',
        'confluence_publish_denylist',
    ]

    for option in publish_list_options:
        value = getattr(config, option)
        if not value:
            continue

        # if provided a file via command line, treat as a list
        def conf_translate(value):
            return handle_cli_file_subset(builder, option, value)  # noqa: B023

        value = conf_translate(value)
        option_val = validator.conf(option, conf_translate)

        try:
            if isinstance(value, (str, os.PathLike)):
                option_val.docnames_from_file()
            else:
                option_val.docnames()
        except ConfluenceConfigError as ex:
            raise ConfluencePublishListConfigError(ex) from ex

    # ##################################################################

    # confluence_publish_debug
    try:
        validator.conf('confluence_publish_debug').bool()  # deprecated
    except ConfluenceConfigError:
        try:
            validator.conf('confluence_publish_debug').enum(PublishDebug)
        except ConfluenceConfigError as ex:
            raise ConfluencePublishDebugConfigError(ex) from ex

    # ##################################################################

    validator.conf('confluence_publish_delay') \
             .float_(positive=True)

    # ##################################################################

    # confluence_publish_dryrun
    validator.conf('confluence_publish_dryrun') \
             .bool()

    # ##################################################################

    # confluence_publish_headers
    validator.conf('confluence_publish_headers') \
             .dict_str_str()

    # ##################################################################

    # confluence_publish_onlynew
    validator.conf('confluence_publish_onlynew') \
             .bool()

    # ##################################################################

    # confluence_publish_orphan
    validator.conf('confluence_publish_orphan') \
             .bool()

    # ##################################################################

    # confluence_publish_orphan_container
    validator.conf('confluence_publish_orphan_container') \
             .int_()

    # ##################################################################

    # confluence_publish_orphan_container
    validator.conf('confluence_publish_override_api_prefix') \
             .dict_str_str()

    # ##################################################################

    # confluence_publish_postfix
    validator.conf('confluence_publish_postfix') \
             .string()

    # ##################################################################

    # confluence_publish_prefix
    validator.conf('confluence_publish_prefix') \
             .string()

    # ##################################################################

    validator.conf('confluence_publish_retry_attempts') \
             .int_(positive=True)

    # ##################################################################

    validator.conf('confluence_publish_retry_duration') \
             .int_(positive=True)

    # ##################################################################

    validator.conf('confluence_publish_root') \
             .int_(positive=True)

    # ##################################################################

    # confluence_publish_token
    validator.conf('confluence_publish_token') \
             .string()

    # ##################################################################

    # confluence_remove_title
    validator.conf('confluence_remove_title') \
             .bool()

    # ##################################################################

    # confluence_request_session_override
    validator.conf('confluence_request_session_override') \
             .callable_()

    # ##################################################################

    # confluence_secnumber_suffix
    validator.conf('confluence_secnumber_suffix') \
             .string()

    # ##################################################################

    # confluence_server_auth
    if config.confluence_server_auth is not None:
        if not issubclass(type(config.confluence_server_auth), AuthBase):
            raise ConfluenceServerAuthConfigError

    # ##################################################################

    # confluence_server_cookies
    validator.conf('confluence_server_cookies') \
             .dict_str_str()

    # ##################################################################

    # confluence_server_pass
    validator.conf('confluence_server_pass') \
             .string()

    # ##################################################################

    # confluence_server_url
    validator.conf('confluence_server_url') \
             .string()

    # ##################################################################

    # confluence_server_user
    validator.conf('confluence_server_user') \
             .string()

    # ##################################################################

    # confluence_sourcelink
    validator.conf('confluence_sourcelink') \
             .dict_str_str()

    if config.confluence_sourcelink:
        sourcelink = config.confluence_sourcelink

        # check if a supported template type is provided
        supported_types = [
            'bitbucket',
            'codeberg',
            'github',
            'gitlab',
        ]
        if 'type' in sourcelink:
            if sourcelink['type'] not in supported_types:
                supported_types_str = '\n - '.join(supported_types)
                raise ConfluenceSourcelinkTypeConfigError(supported_types_str)

            # ensure requires options are set
            required = [
                'owner',
                'repo',
                'version',
            ]
            if not all(k in sourcelink for k in required):
                required_str = '\n - '.join(required)
                raise ConfluenceSourcelinkRequiredConfigError(required_str)

        # if not using a template type, ensure url is set
        elif 'url' not in sourcelink or not sourcelink['url']:
            raise ConfluenceSourcelinkUrlConfigError

        reserved = [
            'page',
            'suffix',
        ]
        if any(k in sourcelink for k in reserved):
            reserved_str = '\n - '.join(reserved)
            raise ConfluenceSourcelinkReservedConfigError(reserved_str)

    # ##################################################################

    # confluence_space_key
    validator.conf('confluence_space_key') \
             .string()

    # ##################################################################

    # confluence_title_overrides
    validator.conf('confluence_title_overrides') \
             .dict_str_str()

    # ##################################################################

    # confluence_timeout
    try:
        validator.conf('confluence_timeout') \
                 .int_()
    except ConfluenceConfigError as ex:
        raise ConfluenceTimeoutConfigError(ex) from ex

    # ##################################################################

    # confluence_use_index
    validator.conf('confluence_use_index') \
             .bool()

    # ##################################################################

    # confluence_version_comment
    validator.conf('confluence_version_comment') \
             .string()

    # ##################################################################

    # confluence_watch
    validator.conf('confluence_watch') \
             .bool()

    # ##################################################################

    if config.confluence_publish:
        if not config.confluence_server_url:
            raise ConfluencePublishMissingServerUrlConfigError

        if not config.confluence_space_key and not config.confluence_space_name:
            raise ConfluencePublishMissingSpaceKeyConfigError

        if (config.confluence_ask_password and not config.confluence_server_user
                and not config.confluence_ask_user):
            raise ConfluencePublishMissingUsernameAskConfigError

        if not config.confluence_server_user:
            if config.confluence_api_token:
                raise ConfluencePublishMissingUsernameAuthConfigError
            if config.confluence_server_pass:
                raise ConfluencePublishMissingUsernamePassConfigError

        if config.confluence_parent_page_id_check:
            if not config.confluence_parent_page:
                raise ConfluencePublishMissingParentPageConfigError

        if config.confluence_publish_root:
            if config.confluence_parent_page:
                raise ConfluencePublishConflictPublishPointConfigError

        if config.confluence_cleanup_purge:
            if config.confluence_cleanup_archive:
                raise ConfluencePublishCleanupConflictConfigError

    # ##################################################################

    # singleconfluence_toctree
    validator.conf('singleconfluence_toctree') \
             .bool()

    # ##################################################################

    # inform users of additional configuration information
    deprecated(validator)
    warnings(validator)
