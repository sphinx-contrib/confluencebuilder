# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020-2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from sphinxcontrib.confluencebuilder.util import str2bool

def apply_defaults(conf):
    """
    applies default values for select configurations

    This call will populate default values for various configuration options.
    This method is used in alternative to the default values provided in the
    `add_config_value` call, which allows this extension to apply defaults at
    a more controlled time.

    Args:
        conf: the configuration to modify
    """

    if conf.confluence_add_secnumbers is None:
        conf.confluence_add_secnumbers = True

    if conf.confluence_adv_ignore_nodes is None:
        conf.confluence_adv_ignore_nodes = []

    if conf.confluence_adv_restricted is None:
        conf.confluence_adv_restricted = []

    if conf.confluence_client_cert is not None:
        if not isinstance(conf.confluence_client_cert, tuple):
            conf.confluence_client_cert = (conf.confluence_client_cert, None)

    if (not conf.confluence_file_suffix or
            conf.confluence_file_suffix.endswith('.')):
        conf.confluence_file_suffix = '.conf'

    if conf.confluence_jira_servers is None:
        conf.confluence_jira_servers = {}

    if conf.confluence_remove_title is None:
        conf.confluence_remove_title = True

    if conf.confluence_secnumber_suffix is None:
        conf.confluence_secnumber_suffix = '. '

    config2bool = [
        'confluence_add_secnumbers',
        'confluence_adv_aggressive_search',
        'confluence_adv_hierarchy_child_macro',
        'confluence_adv_permit_raw_html',
        'confluence_adv_trace_data',
        'confluence_adv_writer_no_section_cap',
        'confluence_ask_password',
        'confluence_ask_user',
        'confluence_asset_force_standalone',
        'confluence_disable_autogen_title',
        'confluence_disable_notifications',
        'confluence_disable_ssl_validation',
        'confluence_ignore_titlefix_on_index',
        'confluence_master_homepage',
        'confluence_page_hierarchy',
        'confluence_publish_dryrun',
        'confluence_publish_onlynew',
        'confluence_purge',
        'confluence_purge_from_master',
        'confluence_purge_from_root',
        'confluence_remove_title',
        'confluence_root_homepage',
        'confluence_watch',
    ]
    for key in config2bool:
        if getattr(conf, key) is not None:
            if not isinstance(getattr(conf, key), bool) and conf[key]:
                conf[key] = str2bool(conf[key])

    config2int = [
        'confluence_max_doc_depth',
        'confluence_parent_page_id_check',
        'confluence_publish_root',
        'confluence_timeout',
    ]
    for key in config2int:
        if getattr(conf, key) is not None:
            if not isinstance(getattr(conf, key), int) and conf[key]:
                conf[key] = int(conf[key])

    # if running an older version of Sphinx which does not define `root_doc`,
    # copy it over now from the legacy configuration
    if 'root_doc' not in conf:
        conf.root_doc = conf.master_doc
