# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger as logger
from sphinxcontrib.confluencebuilder.nodes import confluence_doc_card
from sphinxcontrib.confluencebuilder.nodes import confluence_expand
from sphinxcontrib.confluencebuilder.nodes import confluence_excerpt
from sphinxcontrib.confluencebuilder.nodes import confluence_excerpt_include
from sphinxcontrib.confluencebuilder.nodes import confluence_html
from sphinxcontrib.confluencebuilder.nodes import confluence_latex_block
from sphinxcontrib.confluencebuilder.nodes import confluence_link_card
from sphinxcontrib.confluencebuilder.nodes import confluence_metadata
from sphinxcontrib.confluencebuilder.nodes import confluence_newline
from sphinxcontrib.confluencebuilder.nodes import confluence_toc
from sphinxcontrib.confluencebuilder.nodes import jira
from sphinxcontrib.confluencebuilder.nodes import jira_issue
from sphinxcontrib.confluencebuilder.std.confluence import EDITORS
from uuid import UUID


def string_list(argument):
    """
    string-list validator

    A directive validation which converts a raw string into a list of strings.

    Args:
        argument: the raw string argument

    Returns:
        the list
    """
    data = []

    if argument:
        for line in argument.splitlines():
            for label_entry in line.strip().split(' '):
                label = label_entry.strip()
                if label:
                    data.append(label)

    return data


class ConfluenceCardDirective(Directive):
    has_content = False
    option_spec = {
        'card': lambda x: directives.choice(x, ('block', 'embed')),
        'layout': lambda x: directives.choice(x, ('align-start', 'align-end',
            'center', 'wrap-left', 'wrap-right')),
        'width': directives.positive_int,
    }
    required_arguments = 1
    final_argument_whitespace = True

    def run(self):
        node = self._build_card_node()
        node.params['href'] = self.arguments[0]
        warnings = []

        card = self.options.get('card', None)
        layout = self.options.get('layout', None)
        width = self.options.get('width', None)

        if card:
            node.params['data-card-appearance'] = card

        if layout and card == 'embed':
            node.params['data-layout'] = layout
        elif layout:
            warnings.append('layout only allowed for embedded card')

        if width and card == 'embed':
            node.params['data-width'] = width
        elif width:
            warnings.append('width only allowed for embedded card')

        for warning in warnings:
            reporter = self.state.document.reporter
            source, lineno = reporter.get_source_and_line(self.lineno)
            logger.warn('%s:%s: %s', source, lineno, warning)

        return [node]

    def _build_card_node(self):
        raise NotImplementedError


class ConfluenceDocDirective(ConfluenceCardDirective):
    def _build_card_node(self):
        return confluence_doc_card()


class ConfluenceLinkDirective(ConfluenceCardDirective):
    def _build_card_node(self):
        return confluence_link_card()


class ConfluenceExcerptDirective(Directive):
    has_content = True
    option_spec = {
        'atlassian-macro-output-type':
            lambda x: directives.choice(x, ('block', 'inline')),
        'hidden': lambda x: directives.choice(x, ('true', 'false')),
        'name': directives.unchanged,
    }

    def run(self):
        self.assert_has_content()
        text = '\n'.join(self.content)

        node = confluence_excerpt(rawsource=text)

        # an excerpt's output type is a special option which does not appear
        # to support/following the Kebab  case style -- extract and manually
        # apply this option directly on the node (values for this option are
        # also expected to be in uppercase)
        output_type = 'atlassian-macro-output-type'
        if output_type in self.options:
            node.params[output_type] = self.options[output_type].upper()
            del self.options[output_type]

        for k, v in self.options.items():
            node.params[kebab_case_to_camel_case(k)] = v

        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]


class ConfluenceExcerptIncludeDirective(Directive):
    has_content = False
    option_spec = {
        'name': directives.unchanged,
        'nopanel': lambda x: directives.choice(x, ('true', 'false')),
    }
    required_arguments = 1
    final_argument_whitespace = True

    def run(self):
        node = confluence_excerpt_include()
        node['doclink'] = self.arguments[0]

        for k, v in self.options.items():
            node.params[kebab_case_to_camel_case(k)] = v

        return [node]


class ConfluenceExpandDirective(Directive):
    has_content = True
    option_spec = {
        'title': directives.unchanged,
    }

    def run(self):
        self.assert_has_content()
        text = '\n'.join(self.content)

        node = confluence_expand(rawsource=text)
        if 'title' in self.options:
            node['title'] = self.options['title']

        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]


class ConfluenceHtmlDirective(Directive):
    has_content = True

    def run(self):
        self.assert_has_content()
        text = '\n'.join(self.content)

        node = confluence_html(rawsource=text)

        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]


class ConfluenceLatexDirective(Directive):
    has_content = True
    option_spec = {
        'align': directives.unchanged,
    }

    def run(self):
        self.assert_has_content()
        text = '\n'.join(self.content)

        node = confluence_latex_block(rawsource=text, text=text)
        node['align'] = self.options.get('align', 'center')

        return [node]


class ConfluenceMetadataDirective(Directive):
    has_content = False
    option_spec = {
        'editor': lambda x: directives.choice(x, EDITORS),
        'full-width': lambda x: directives.choice(x, ('true', 'false')),
        'guid': directives.unchanged,
        'labels': string_list,
    }

    def run(self):
        node = confluence_metadata()

        for k, v in self.options.items():
            node.params[kebab_case_to_camel_case(k)] = v

        return [node]


class ConfluenceNewline(Directive):
    has_content = False

    def run(self):
        node = confluence_newline()

        return [node]


class ConfluenceToc(Directive):
    has_content = False
    option_spec = {
        'absolute-url': lambda x: directives.choice(x, ('true', 'false')),
        'exclude': directives.unchanged,
        'include': directives.unchanged,
        'indent': directives.unchanged,
        'max-level': directives.positive_int,
        'min-level': directives.positive_int,
        'outline': lambda x: directives.choice(x, ('true', 'false')),
        'printable': lambda x: directives.choice(x, ('true', 'false')),
        'separator': directives.unchanged,
        'style': directives.unchanged,
        'type': lambda x: directives.choice(x, ('flat', 'list')),
    }

    def run(self):
        node = confluence_toc()

        for k, v in self.options.items():
            node.params[kebab_case_to_camel_case(k)] = v

        return [node]


class JiraBaseDirective(Directive):
    has_content = False
    required_arguments = 1

    def run(self):
        node = self._build_jira_node()
        params = node.params

        # confluence expects camel case parameters
        for k, v in self.options.items():
            params[kebab_case_to_camel_case(k)] = v

        # extract target server helper
        #
        # If a user defines a `server` key (`confluence_jira_servers` mapping),
        # remove it and track it inside `target_server`. The `server` key is a
        # reversed option for the JIRA macro; however, we dance between
        # `server` and `server-name` so that users can use the option `server`
        # as simpler directive option to use. If `server-name` is set, prepare
        # it to be set as the `server` option in the macro.
        target_server = params.pop('server', None)

        if 'serverName' in params:
            params['server'] = params.pop('serverName', None)

        # if explicit server is provided, ensure both options are set
        if 'server' in params or 'serverId' in params:
            if 'server' not in params:
                msg = (
                    ':server-name: required when server-id is set; '
                    'but none supplied'
                )
                raise self.error(msg)
            if 'serverId' not in params:
                msg = (
                    ':server-id: required when server-name is set; '
                    'but none supplied'
                )
                raise self.error(msg)
        # if a server key is provided, fetch values from configuration
        elif target_server:
            config = self.state.document.settings.env.config
            if not config.confluence_jira_servers:
                msg = (
                    ':server: is set but no '
                    'confluence_jira_servers defined in config'
                )
                raise self.error(msg)
            jira_servers = config['confluence_jira_servers']
            if target_server not in jira_servers:
                msg = (
                    ':server: is set but does not exist in '
                    'confluence_jira_servers config'
                )
                raise self.error(msg)
            jira_server_config = jira_servers[target_server]
            if 'name' not in jira_server_config:
                msg = (
                    ':server: is set but missing name entry in '
                    'confluence_jira_servers config'
                )
                raise self.error(msg)
            params['server'] = jira_server_config['name']
            if 'id' not in jira_server_config:
                msg = (
                    ':server: is set but missing id entry in '
                    'confluence_jira_servers config'
                )
                raise self.error(msg)
            params['serverId'] = jira_server_config['id']

        if 'serverId' in params:
            try:
                UUID(params['serverId'], version=4)
            except ValueError as ex:
                msg = 'server-id is not a valid uuid'
                raise self.error(msg) from ex

        return [node]

    def _build_jira_node(self):
        raise NotImplementedError


class JiraDirective(JiraBaseDirective):
    option_spec = {
        'columns': directives.unchanged,
        'count': lambda x: directives.choice(x, ('true', 'false')),
        'maximum-issues': directives.positive_int,
        'server': directives.unchanged,
        'server-id': directives.unchanged,
        'server-name': directives.unchanged,
    }
    final_argument_whitespace = True

    def _build_jira_node(self):
        node = jira()
        self.options['jql-query'] = self.arguments[0]
        return node


class JiraIssueDirective(JiraBaseDirective):
    option_spec = {
        'server': directives.unchanged,
        'server-id': directives.unchanged,
        'server-name': directives.unchanged,
    }

    def _build_jira_node(self):
        node = jira_issue()
        self.options['key'] = self.arguments[0]
        return node


def kebab_case_to_camel_case(s):
    """
    convert a kebab case string to a camel case string

    A utility function to help convert a kebab case string into a camel case
    string. This is to help convert directive options typically defined in kebab
    case to Confluence macro parameters values which are typically required to
    be in camel case.

    Args:
        s: the string to convert

    Returns:
        the converted string
    """
    s = ''.join(x.capitalize() for x in s.split('-'))
    return s[0].lower() + s[1:]
