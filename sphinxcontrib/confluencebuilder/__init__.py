# -*- coding: utf-8 -*-
"""
    sphinxcontrib.confluencebuilder.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Sphinx extension to output Atlassian Confluence wiki files.

    :copyright: Copyright 2016-2017 by the contributors (see AUTHORS file).
    :license: BSD, see LICENSE.txt for details.
"""

from .builder import ConfluenceBuilder
from .common import ConfluenceLogger
from sphinx.writers.text import STDINDENT
import argparse

__version__='0.6.0.dev0'

def main():
    parser = argparse.ArgumentParser(prog=__name__,
        description='Sphinx extension to output Atlassian Confluence content.')
    parser.add_argument(
        '--version', action='version', version='%(prog)s ' + __version__)

    parser.parse_args()
    parser.print_help()
    return 0

def setup(app):
    ConfluenceLogger.initialize(app)

    app.require_sphinx('1.0')
    app.add_builder(ConfluenceBuilder)
    """(generic)"""
    """Filename suffix for generated files."""
    app.add_config_value('confluence_file_suffix', ".conf", False)
    """Translation of docname to a filename."""
    app.add_config_value('confluence_file_transform', None, False)
    """File to get page footer information from."""
    app.add_config_value('confluence_footer_file', None, False)
    """File to get page header information from."""
    app.add_config_value('confluence_header_file', None, False)
    """Indent to use for generated documents."""
    app.add_config_value('confluence_indent', STDINDENT, False)
    """Link suffix for generated files."""
    app.add_config_value('confluence_link_suffix', None, False)
    """Translation of docname to a (partial) URI."""
    app.add_config_value('confluence_link_transform', None, False)

    """(publishing)"""
    """Explictly prevent any Confluence REST API callers."""
    app.add_config_value('confluence_disable_rest', None, False)
    """Explictly prevent any Confluence XML-RPC API callers."""
    app.add_config_value('confluence_disable_xmlrpc', None, False)
    """Root/parent page's name to publish documents into."""
    app.add_config_value('confluence_parent_page', None, False)
    """Root/parent page's identifier to publish documents into."""
    app.add_config_value('confluence_parent_page_id_check', None, False)
    """Enablement of purging legacy child pages from a parent page."""
    app.add_config_value('confluence_purge', None, False)
    """List of extension-provided macros restricted for use."""
    app.add_config_value('confluence_restricted_macros', [], False)
    """Password to login to Confluence API with."""
    app.add_config_value('confluence_server_pass', None, False)
    """Username to login to Confluence API with."""
    app.add_config_value('confluence_server_user', None, False)
    """URL of the Confluence server to publish to."""
    app.add_config_value('confluence_server_url', None, False)
    """Confluence Space to publish to."""
    app.add_config_value('confluence_space_name', None, False)
    """Proxy server needed to communicate with Confluence server."""
    app.add_config_value('confluence_proxy', None, False)
    """Enablement of publishing."""
    app.add_config_value('confluence_publish', None, False)
    """Prefix to apply to published pages."""
    app.add_config_value('confluence_publish_prefix', None, False)
    """Timeout for network-related calls (publishing)."""
    app.add_config_value('confluence_timeout', None, False)
