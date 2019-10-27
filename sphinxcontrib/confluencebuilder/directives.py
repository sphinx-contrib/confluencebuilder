# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2016-2019 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from collections import OrderedDict


def snake_case_to_camel_case(s):
    s = ''.join(list(map(lambda x: x.capitalize(), s.split('_'))))
    s = s[0].lower() + s[1:]
    return s


class jira(nodes.Element, nodes.Structural):
    config = OrderedDict()


class jira_issue(nodes.Element, nodes.Structural):
    config = OrderedDict()


class JIRABaseDirective(Directive):

    has_content = False
    required_arguments = 1
    option_spec = {
        'server_name': directives.unchanged,
        'server': directives.unchanged,
        'server_id': directives.unchanged,
        'columns': directives.unchanged,
        'count': lambda x: directives.choice(x, ('true', 'false')),
        'maximum_issues': directives.positive_int
    }

    def get_base_node_object(self):
        raise NotImplementedError()

    def get_required_option_name(self):
        raise NotImplementedError()

    def get_required_option_value(self):
        raise NotImplementedError()

    def get_keys_to_remove(self):
        raise NotImplementedError()

    def run(self):
        node = self.get_base_node_object()

        keys_to_skip = self.get_keys_to_remove()

        # Add either the JQL query or Key to the content
        self.options[self.get_required_option_name()] = self.get_required_option_value()

        # Resolve server name to the appropriate server values supplied in config

        if 'server_name' in self.options:
            # We don't want this field in the final output
            server_name = self.options.pop('server_name')
            config = self.state.document.settings.env.config
            jira_servers = config['confluence_jira_servers']

            jira_server_config = jira_servers[server_name]

            # We only apply the jira_server_config values if they weren't manually overwritten on the directive
            if 'server' not in self.options:
                self.options['server'] = jira_server_config['name']
            if 'server_id' not in self.options:
                self.options['server_id'] = jira_server_config['id']

        # Sort the keys. This is for having a reliable parameter order for using the assertExpectedWithOutput
        # method; Confluence doesn't require the parameters to be in any particular order
        options_copy = OrderedDict((k, self.options[k]) for k in sorted(self.options.keys()))

        for k, v in options_copy.items():
            if k not in keys_to_skip:
                node.config[snake_case_to_camel_case(k)] = v

        return [node]


class JIRADirective(JIRABaseDirective):

    final_argument_whitespace = True

    def get_keys_to_remove(self):
        return []

    def get_base_node_object(self):
        return jira()

    def get_required_option_name(self):
        return 'jql_query'

    def get_required_option_value(self):
        return self.arguments[0]


class JIRAIssueDirective(JIRABaseDirective):

    def get_base_node_object(self):
        return jira_issue()

    def get_required_option_name(self):
        return 'key'

    def get_required_option_value(self):
        return self.arguments[0]

    def get_keys_to_remove(self):
        return ['maximum_issues', 'count']
