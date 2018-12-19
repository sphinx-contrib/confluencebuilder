# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2016-2018 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from __future__ import unicode_literals
from .exceptions import ConfluenceError
from .logger import ConfluenceLogger
from .state import ConfluenceState
from .std.confluence import FCMMO
from .std.confluence import INDENT
from .std.confluence import LITERAL2LANG_MAP
from .std.sphinx import DEFAULT_HIGHLIGHT_STYLE
from docutils import nodes
from docutils.nodes import NodeVisitor as BaseTranslator
from os import path
from sphinx.locale import admonitionlabels
from sphinx.util.osutil import SEP
import io
import posixpath
import sys

class ConfluenceTranslator(BaseTranslator):
    _tracked_unknown_code_lang = []

    """
    confluence extension translator

    Translator instance for the Confluence extension for Sphinx. This
    implementation is responsible for processing individual documents based on
    parsed node entries provided by docutils (used by Sphinx).

    Args:
        document: the document being translated
        builder: the sphinx builder instance
    """
    def __init__(self, document, builder):
        BaseTranslator.__init__(self, document)
        self.builder = builder
        config = builder.config

        # acquire the active document name from the builder
        assert builder.current_docname
        self.docname = builder.current_docname

        # determine the active document's parent path to assist it title mapping
        # for relative document uris
        # (see '_visit_reference_intern_uri')
        if SEP in self.docname:
            self.docparent = self.docname[0:self.docname.rfind(SEP) + 1]
        else:
            self.docparent = ''

        self.assets = builder.assets
        self.body = []
        self.context = []
        self.nl = '\n'
        self.warn = document.reporter.warning
        self._building_footnotes = False
        self._manpage_url = getattr(config, 'manpages_url', None)
        self._quote_level = 0
        self._reference_context = []
        self._section_level = 1
        self._thead_context = []
        self._tocdepth = ConfluenceState.toctreeDepth(self.docname)

        if config.highlight_language:
            self._highlight = config.highlight_language
        else:
            self._highlight = DEFAULT_HIGHLIGHT_STYLE
        self._linenothreshold = sys.maxsize

        # helpers for dealing with disabled/unsupported macros
        restricted_macros = config.confluence_adv_restricted_macros
        self.can_admonition = not 'info' in restricted_macros
        self.can_anchor = not 'anchor' in restricted_macros
        self.can_children = not 'children' in restricted_macros
        self.can_code = not 'code' in restricted_macros
        self.can_viewfile = not 'viewfile' in restricted_macros

        if (config.confluence_page_hierarchy
                and config.confluence_adv_hierarchy_child_macro
                and self.can_children):
            self.apply_hierarchy_children_macro = True
        else:
            self.apply_hierarchy_children_macro = False

    # ##########################################################################
    # #                                                                        #
    # # base translator overrides                                              #
    # #                                                                        #
    # ##########################################################################

    def visit_document(self, node):
        pass

    def depart_document(self, node):
        self.document = '';

        # prepend header (if any)
        if self.builder.config.confluence_header_file is not None:
            headerFile = path.join(self.builder.env.srcdir,
                self.builder.config.confluence_header_file)
            try:
                with io.open(headerFile, encoding='utf-8') as file:
                    self.document += file.read() + self.nl
            except (IOError, OSError) as err:
                ConfluenceLogger.warn('error reading file '
                    '{}: {}'.format(headerFile, err))

        self.document += ''.join(self.body)

        # append footer (if any)
        if self.builder.config.confluence_footer_file is not None:
            footerFile = path.join(self.builder.env.srcdir,
                self.builder.config.confluence_footer_file)
            try:
                with io.open(footerFile, encoding='utf-8') as file:
                    self.document += file.read() + self.nl
            except (IOError, OSError) as err:
                ConfluenceLogger.warn('error reading file '
                    '{}: {}'.format(footerFile, err))

    def visit_Text(self, node):
        text = node.astext()
        text = self._escape_sf(text)
        self.body.append(text)
        raise nodes.SkipNode

    def unknown_visit(self, node):
        raise NotImplementedError('unknown node: ' + node.__class__.__name__)

    # ---------
    # structure
    # ---------

    def visit_section(self, node):
        level = self._section_level

        if not self.builder.config.confluence_adv_writer_no_section_cap:
            MAX_CONFLUENCE_SECTIONS = 6
            if self._section_level > MAX_CONFLUENCE_SECTIONS:
                level = MAX_CONFLUENCE_SECTIONS

        self._title_level = level
        self._section_level += 1

    def depart_section(self, node):
        self._section_level -= 1

    def visit_title(self, node):
        if isinstance(node.parent, (nodes.section, nodes.topic)):
            self.body.append(
                self._start_tag(node, 'h{}'.format(self._title_level)))
            self.context.append(self._end_tag(node))
        else:
            # Only render section/topic titles in headers. For all other nodes,
            # they must explicitly manage their own title entries.
            raise nodes.SkipNode

    def depart_title(self, node):
        if isinstance(node.parent, (nodes.section, nodes.topic)):
            self.body.append(self.context.pop()) # h<x>

    def visit_paragraph(self, node):
        self.body.append(self._start_tag(node, 'p'))
        self.context.append(self._end_tag(node))

    def depart_paragraph(self, node):
        self.body.append(self.context.pop()) # p

    def visit_transition(self, node):
        self.body.append(self._start_tag(
            node, 'hr', suffix=self.nl, empty=True))
        raise nodes.SkipNode

    visit_topic = visit_section
    depart_topic = depart_section

    # ----------------------
    # body elements -- lists
    # ----------------------

    def _apply_leading_list_item_offets(self, node, attribs):
        # Confluence's provided styles remove first-child elements leading
        # margins. This causes some unexpected styling issues when list entries
        # which contain other block elements do not style appropriately. This
        # extensions attempts to maintain compact list item entries; however,
        # for a list which contains non-compact entries (e.x. multiple
        # paragraphs), instead, each list item will be applied a respective
        # margin offset.
        #
        # Previously, a pattern such as the following would occur:
        #
        #  - line
        #    (spacing)
        #    line
        #    - line
        #    - line
        #    (spacing)
        #    line
        #  - line
        #    (spacing)
        #    line
        #
        # To prevent this from happening, a margin applied to non-compact
        # entries will render as:
        #
        #  - line
        #    (spacing)
        #    line
        #    (spacing) <-- spacing between complex list item
        #    - line    <-- no spacing for compact list (desired)
        #    - line
        #    (spacing)
        #    line
        #    (spacing) <-- spacing between complex list item
        #  - line
        #    (spacing)
        #    line
        #

        # If any item in this list contains two or more children (with the
        # exception of a "paragraph" + list pair), consider the entire list a
        # complex one and flag each list item to include a margin.
        has_complex = False
        for child in node.children: # list items
            if len(child.children) > 2 or (len(child.children) == 2
                    and not isinstance(child.children[1],
                        (nodes.bullet_list, nodes.enumerated_list))):
                has_complex = True
                break

        if has_complex:
            for child in node.children:
                child.__confluence_list_item_margin = True

        # If this list is nested inside a complex list, ensure this list starts
        # off with a margin (to offset it's position inside the complex list).
        if isinstance(node.parent, nodes.list_item):
            try:
                if node.parent.__confluence_list_item_margin:
                    attribs['style'] = 'margin-top: {}px;'.format(FCMMO)
            except AttributeError:
                pass

    def visit_bullet_list(self, node):
        attribs = {}
        self._apply_leading_list_item_offets(node, attribs)

        self.body.append(self._start_tag(node, 'ul', suffix=self.nl, **attribs))
        self.context.append(self._end_tag(node))

    def depart_bullet_list(self, node):
        self.body.append(self.context.pop()) # ul

    def visit_enumerated_list(self, node):
        attribs = {}
        self._apply_leading_list_item_offets(node, attribs)

        # note: - Not all Confluence versions (if any) support populating the
        #         'type' attribute of an ordered list tag; however, the 'style'
        #         attribute is accepted.
        #       - Not all Confluence versions (if any) support populating the
        #         'start' attribute of an ordered list tag; limiting to
        #         auto-enumeration items only.
        list_style_type = None
        if node['enumtype'] == 'upperalpha':
            list_style_type = 'upper-alpha'
        elif node['enumtype'] == 'loweralpha':
            list_style_type = 'lower-alpha'
        elif node['enumtype'] == 'upperroman':
            list_style_type = 'upper-roman'
        elif node['enumtype'] == 'lowerroman':
            list_style_type = 'lower-roman'
        elif node['enumtype'] == 'arabic':
            list_style_type = 'decimal'
        else:
            ConfluenceLogger.warn(
                'unknown enumerated list type: {}'.format(node['enumtype']))

        if 'style' not in attribs:
            attribs['style'] = ''
        attribs['style'] = '{}list-style-type: {};'.format(
            attribs['style'], list_style_type)

        self.body.append(self._start_tag(node, 'ol', suffix=self.nl, **attribs))
        self.context.append(self._end_tag(node))

    def depart_enumerated_list(self, node):
        self.body.append(self.context.pop()) # ol

    def visit_list_item(self, node):
        # apply margin offset if flagged (see _apply_leading_list_item_offets)
        attribs = {}
        try:
            if node.__confluence_list_item_margin:
                attribs['style'] = 'margin-top: {}px;'.format(FCMMO)
        except AttributeError:
            pass

        self.body.append(self._start_tag(node, 'li', suffix=self.nl, **attribs))
        self.context.append(self._end_tag(node))

    def depart_list_item(self, node):
        self.body.append(self.context.pop()) # li

    # ---------------------------------
    # body elements -- definition lists
    # ---------------------------------

    def visit_definition_list(self, node):
        self.body.append(self._start_tag(node, 'dl', suffix=self.nl))
        self.context.append(self._end_tag(node))

    def depart_definition_list(self, node):
        self.body.append(self.context.pop()) # dl

    def visit_definition_list_item(self, node):
        # When processing a definition list item (an entry), multiple terms may
        # exist for the given entry (e.x. when using a glossary). Before
        # displaying an actual definition of one or more terms, there may exist
        # classifiers for a given entry. On the last term for an entry, all
        # classifier information will be displayed in the definition-type. In
        # order to achieve this, a list entry will be tracked to see if a term
        # has been processed for an entry. If a new term is detected, the
        # previous term's tag will be closed off. On the final term, the tag is
        # not closed off until the definition (visit_definition) is processed.
        # This allows classifier information to be populated into the last term
        # element.
        self._has_term = False

    def depart_definition_list_item(self, node):
        self._has_term = False

    def visit_term(self, node):
        # close of previous term (see visit_definition_list_item)
        if self._has_term:
            self.body.append(self.context.pop()) # dt

        if 'ids' in node and self.can_anchor:
            for id in node['ids']:
                self.body.append(self._start_ac_macro(node, 'anchor'))
                self.body.append(self._build_ac_parameter(node, '', id))
                self.body.append(self._end_ac_macro(node))

        self.body.append(self._start_tag(node, 'dt'))
        self.context.append(self._end_tag(node))
        self._has_term = True

    def depart_term(self, node):
        # note: Do not pop the context populated from 'visit_term'. The last
        #       entry may need to hold classifier information inside it. Either
        #       next term or a term's definition will pop the context.
        pass

    def visit_classifier(self, node):
        self.body.append(' : ')
        self.body.append(self._start_tag(node, 'em'))
        self.context.append(self._end_tag(node, suffix=''))

    def depart_classifier(self, node):
        self.body.append(self.context.pop()) # em

    def visit_definition(self, node):
        self.body.append(self.context.pop()) # dt

        self.body.append(self._start_tag(node, 'dd', suffix=self.nl))
        self.context.append(self._end_tag(node))

    def depart_definition(self, node):
        self.body.append(self.context.pop()) # dd

    def visit_termsep(self, node):
        raise nodes.SkipNode

    # ----------------------------
    # body elements -- field lists
    # ----------------------------

    def visit_field_list(self, node):
        self.body.append(self._start_tag(node, 'table', suffix=self.nl))
        self.context.append(self._end_tag(node))
        self.body.append(self._start_tag(node, 'tbody', suffix=self.nl))
        self.context.append(self._end_tag(node))

    def depart_field_list(self, node):
        self.body.append(self.context.pop()) # tbody
        self.body.append(self.context.pop()) # table

    def visit_field(self, node):
        self.body.append(self._start_tag(node, 'tr', suffix=self.nl))
        self.context.append(self._end_tag(node))

    def depart_field(self, node):
        self.body.append(self.context.pop()) # tr

    def visit_field_name(self, node):
        self.body.append(self._start_tag(node, 'td',
            **{'style': 'border: none'}))
        self.context.append(self._end_tag(node))

        self.body.append(self._start_tag(node, 'strong'))
        self.context.append(self._end_tag(node, suffix=''))

    def depart_field_name(self, node):
        self.body.append(':')
        self.body.append(self.context.pop()) # strong
        self.body.append(self.context.pop()) # td

    def visit_field_body(self, node):
        self.body.append(self._start_tag(node, 'td',
            **{'style': 'border: none'}))
        self.context.append(self._end_tag(node))

    def depart_field_body(self, node):
        self.body.append(self.context.pop()) # td

    # -----------------------------
    # body elements -- option lists
    # -----------------------------

    def visit_option_list(self, node):
        self.body.append(self._start_tag(node, 'table', suffix=self.nl))
        self.context.append(self._end_tag(node))
        self.body.append(self._start_tag(node, 'tbody', suffix=self.nl))
        self.context.append(self._end_tag(node))

    def depart_option_list(self, node):
        self.body.append(self.context.pop()) # tbody
        self.body.append(self.context.pop()) # table

    def visit_option_list_item(self, node):
        self.body.append(self._start_tag(node, 'tr', suffix=self.nl))
        self.context.append(self._end_tag(node))

    def depart_option_list_item(self, node):
        self.body.append(self.context.pop()) # tr

    def visit_option_group(self, node):
        self._first_option = True
        self.body.append(self._start_tag(node, 'td',
            **{'style': 'border: none'}))
        self.context.append(self._end_tag(node))

    def depart_option_group(self, node):
        self.body.append(self.context.pop()) # td

    def visit_option(self, node):
        if self._first_option:
            self._first_option = False
        else:
            self.body.append(', ')

    def depart_option(self, node):
        pass

    def visit_option_string(self, node):
        pass

    def depart_option_string(self, node):
        pass

    def visit_option_argument(self, node):
        self.body.append(node['delimiter'])

    def depart_option_argument(self, node):
        pass

    def visit_description(self, node):
        self.body.append(self._start_tag(node, 'td',
            **{'style': 'border: none'}))
        self.context.append(self._end_tag(node))

    def depart_description(self, node):
        self.body.append(self.context.pop()) # td

    # -------------------------------
    # body elements -- literal blocks
    # -------------------------------

    def visit_literal_block(self, node):
        is_parsed_literal = node.rawsource != node.astext()
        if is_parsed_literal:
            self.body.append(self._start_tag(node, 'div', suffix=self.nl,
                **{'class': 'panel pdl'}))
            self.context.append(self._end_tag(node))
            self.body.append(self._start_tag(node, 'pre',
                **{'class': 'panelContent'}))
            self.context.append(self._end_tag(node))
            self.body.append(self._start_tag(node, 'code'))
            self.context.append(self._end_tag(node))
            return

        lang = node.get('language', self._highlight).lower()
        if self.builder.lang_transform:
            lang = self.builder.lang_transform(lang)
        elif lang in LITERAL2LANG_MAP.keys():
            lang = LITERAL2LANG_MAP[lang]
        else:
            if lang not in self._tracked_unknown_code_lang:
                ConfluenceLogger.warn('unknown code language: {}'.format(lang))
                self._tracked_unknown_code_lang.append(lang)
            lang = LITERAL2LANG_MAP[DEFAULT_HIGHLIGHT_STYLE]

        data = self.nl.join(node.astext().splitlines())

        if node.get('linenos', False) == True:
            num = 'true'
        elif data.count('\n') >= self._linenothreshold:
            num = 'true'
        else:
            num = 'false'

        if self.can_code:
            self.body.append(self._start_ac_macro(node, 'code'))
            self.body.append(self._build_ac_parameter(node, 'language', lang))
            self.body.append(self._build_ac_parameter(node, 'linenumbers', num))
            self.body.append(self._start_ac_plain_text_body_macro(node))
            self.body.append(self._escape_cdata(data))
            self.body.append(self._end_ac_plain_text_body_macro(node))
            self.body.append(self._end_ac_macro(node))
        else:
            self.body.append(self._start_tag(
                node, 'hr', suffix=self.nl, empty=True))
            self.body.append(self._start_tag(node, 'pre'))
            self.body.append(self._escape_sf(data))
            self.body.append(self._end_tag(node))
            self.body.append(self._start_tag(
                node, 'hr', suffix=self.nl, empty=True))

        raise nodes.SkipNode

    def depart_literal_block(self, node):
        # note: depart is only invoked for parsed-literals
        self.body.append(self.context.pop()) # code
        self.body.append(self.context.pop()) # pre
        self.body.append(self.context.pop()) # div

    def visit_highlightlang(self, node):
        self._highlight = node.get('lang', DEFAULT_HIGHLIGHT_STYLE)
        self._linenothreshold = node.get('linenothreshold', sys.maxsize)
        raise nodes.SkipNode

    def visit_doctest_block(self, node):
        data = self.nl.join(node.astext().splitlines())

        if self.can_code:
            self.body.append(self._start_ac_macro(node, 'code'))
            self.body.append(self._build_ac_parameter(
                node, 'language', 'python')) # python-specific
            self.body.append(self._start_ac_plain_text_body_macro(node))
            self.body.append(self._escape_cdata(data))
            self.body.append(self._end_ac_plain_text_body_macro(node))
            self.body.append(self._end_ac_macro(node))
        else:
            self.body.append(self._start_tag(
                node, 'hr', suffix=self.nl, empty=True))
            self.body.append(self._start_tag(node, 'pre'))
            self.body.append(self._escape_sf(data))
            self.body.append(self._end_tag(node))
            self.body.append(self._start_tag(
                node, 'hr', suffix=self.nl, empty=True))

        raise nodes.SkipNode

    # -----------------------------
    # body elements -- block quotes
    # -----------------------------

    def visit_block_quote(self, node):
        if node.traverse(nodes.attribution):
            self.body.append(self._start_tag(node, 'blockquote'))
            self.context.append(self._end_tag(node))
        else:
            self._quote_level += 1
            style = ''

            # Confluece's WYSIWYG, when indenting paragraphs, will produce
            # paragraphs will margin values offset by 30 pixels units. The same
            # indentation is applied here via a style value (multiplied by the
            # current quote level).
            indent_val = INDENT * self._quote_level
            style += 'margin-left: {}px;'.format(indent_val)

            # Confluence's provided styles remove first-child elements leading
            # margins. This causes some unexpected styling issues when various
            # indentation patterns are applied (between div elements and
            # multiple paragraphs). To overcome this, the indent container being
            # added will be given a top-padding-offset matching Confluence's
            # common non-first-child element top-margins (i.e. 10 pixels).
            #
            # Note that this offset does not style well when multiple
            # indentations are observed; sub-level containers can result in
            # stacked padding (not desired). For example:
            #
            #     first-line
            #         (10px of padding)
            #             (10px of padding)
            #             first-line
            #         first-line
            #
            # To prevent this from happening, if the next child container is
            # another block quote, no padding is added:
            #
            #     first-line
            #             (10px of padding)
            #             first-line
            #         first-line
            #
            # Ideally, a padding-offset is not desired (as it may required
            # tweaking if Confluence's themes change); however, the quirk works
            # for now.
            firstchild_margin = True
            next_child = node.traverse(include_self=False)
            if next_child and isinstance(next_child[0], nodes.block_quote):
                firstchild_margin = False

            if firstchild_margin:
                style += 'padding-top: {}px;'.format(FCMMO)

            self.body.append(self._start_tag(node, 'div', suffix=self.nl,
                **{'style': style}))
            self.context.append(self._end_tag(node))

    def depart_block_quote(self, node):
        if node.traverse(nodes.attribution):
            self.body.append(self.context.pop()) # blockquote
        else:
            self._quote_level -= 1
            self.body.append(self.context.pop()) # div

    def visit_attribution(self, node):
        self.body.append('-- ')

    def depart_attribution(self, node):
        pass

    # -----------
    # admonitions
    # -----------

    def _visit_admonition(self, node, atype, title=None):
        if self.can_admonition:
            self.body.append(self._start_ac_macro(node, atype))
            if title:
                self.body.append(self._build_ac_parameter(node, 'title', title))
            self.body.append(self._start_ac_rich_text_body_macro(node))
            self.context.append(self._end_ac_rich_text_body_macro(node) +
                self._end_ac_macro(node))
        else:
            self.body.append(self._start_tag(node, 'blockquote'))
            self.context.append(self._end_tag(node))

    def _depart_admonition(self, node):
        self.body.append(self.context.pop()) # macro (or blockquote)

    def _visit_info(self, node):
        self._visit_admonition(node, 'info')

    def _visit_note(self, node):
        self._visit_admonition(node, 'note')

    def _visit_tip(self, node):
        self._visit_admonition(node, 'tip')

    def _visit_warning(self, node):
        self._visit_admonition(node, 'warning')

    visit_attention = _visit_note
    depart_attention = _depart_admonition
    visit_caution = _visit_note
    depart_caution = _depart_admonition
    visit_danger = _visit_warning
    depart_danger = _depart_admonition
    visit_error = _visit_warning
    depart_error = _depart_admonition
    visit_hint = _visit_tip
    depart_hint = _depart_admonition
    visit_important = _visit_warning
    depart_important = _depart_admonition
    visit_note = _visit_info
    depart_note = _depart_admonition
    visit_tip = _visit_tip
    depart_tip = _depart_admonition
    visit_warning = _visit_warning
    depart_warning = _depart_admonition

    # ------
    # tables
    # ------

    def visit_table(self, node):
        title_node = node.traverse(nodes.title)
        if title_node:
            self.body.append(self._start_tag(node, 'p'))
            self.body.append(self._start_tag(node, 'strong'))
            self.body.append(self._escape_sf(title_node[0].astext()))
            self.body.append(self._end_tag(node))
            self.body.append(self._end_tag(node))

        self.body.append(self._start_tag(node, 'table', suffix=self.nl))
        self.context.append(self._end_tag(node))

        # track the thead context
        #
        # When writing a table cell (visit_entry), it needs to be known if the
        # cell is in the header (th) or is a data cell (td). A "thead context"
        # keeps track of whether or not an cell/entry being written is of the
        # proper type. A context list is needed to support nested tables.
        self._thead_context.append(False)

    def depart_table(self, node):
        self.body.append(self.context.pop()) # table
        self._thead_context.pop()

    def visit_tgroup(self, node):
        pass

    def depart_tgroup(self, node):
        pass

    def visit_thead(self, node):
        self._thead_context.append(True) # thead context (see visit_table)
        self.body.append(self._start_tag(node, 'thead', suffix=self.nl))
        self.context.append(self._end_tag(node))

    def depart_thead(self, node):
        self.body.append(self.context.pop()) # thead context (see visit_table)
        self._thead_context.pop()

    def visit_tbody(self, node):
        self.body.append(self._start_tag(node, 'tbody', suffix=self.nl))
        self.context.append(self._end_tag(node))

    def depart_tbody(self, node):
        self.body.append(self.context.pop()) # tbody

    def visit_row(self, node):
        self.body.append(self._start_tag(node, 'tr', suffix=self.nl))
        self.context.append(self._end_tag(node))

    def depart_row(self, node):
        self.body.append(self.context.pop()) # tr

    def visit_entry(self, node):
        if self._thead_context[-1]:
            target_tag = 'th'
        else:
            target_tag = 'td'

        attribs = {}
        if 'morecols' in node:
            attribs['colspan'] = node['morecols'] + 1
        if 'morerows' in node:
            attribs['rowspan'] = node['morerows'] + 1

        self.body.append(self._start_tag(node, target_tag, **attribs))
        self.context.append(self._end_tag(node))

    def depart_entry(self, node):
        self.body.append(self.context.pop()) # td/th

    def visit_tabular_col_spec(self, node):
        raise nodes.SkipNode

    def visit_colspec(self, node):
        raise nodes.SkipNode

    # -------------------
    # references - common
    # -------------------

    def visit_reference(self, node):
        # nested references should never happen
        assert(not self._reference_context)

        if 'iscurrent' in node:
            pass
        elif ((not 'internal' in node or not node['internal'])
                and 'refuri' in node):
            # If a document provides an anchor target directly in the reference,
            # attempt to extract the anchor value and pass it into the internal
            # reference processing instead.
            if node['refuri'].startswith('#'):
                node['refid'] = node['refuri'][1:]
                del node['refuri']
                self._visit_reference_intern_id(node)
            else:
                self._visit_reference_extern(node)
        elif 'refid' in node:
            self._visit_reference_intern_id(node)
        elif 'refuri' in node:
            self._visit_reference_intern_uri(node)

    def _visit_reference_extern(self, node):
        uri = node['refuri']
        uri = self._escape_sf(uri)

        self.body.append(self._start_tag(node, 'a', **{'href': uri}))
        self._reference_context.append(self._end_tag(node, suffix=''))

    def _visit_reference_intern_id(self, node):
        anchor = ''.join(node['refid'].split())

        # check if this target is reachable without an anchor; if so, use the
        # identifier value instead
        target_name = '{}#{}'.format(self.docname, anchor)
        target = ConfluenceState.target(target_name)
        if target:
            anchor_value = target
            anchor_value = self._escape_sf(anchor_value)
        elif not self.can_anchor:
            anchor_value = None
        else:
            anchor_value = anchor

        is_citation = ('ids' in node and node['ids']
            and 'internal' in node and node['internal'])

        if is_citation and anchor_value:
            # build an anchor for back reference
            self.body.append(self._start_ac_macro(node, 'anchor'))
            self.body.append(self._build_ac_parameter(node, '', node['ids'][0]))
            self.body.append(self._end_ac_macro(node))

        if is_citation:
            self.body.append(self._start_tag(node, 'sup'))

        if anchor_value:
            # build link to internal anchor (on the same page)
            #  Note: plain-text-link body cannot have inline markup; content
            #        will be added into body already and skip-children should be
            #        invoked for this use case.
            self.body.append(self._start_ac_link(node, anchor_value))
            self.body.append(self._start_ac_link_body(node))
            self._reference_context.append(self._end_ac_link_body(node))
            self._reference_context.append(self._end_ac_link(node))

        if is_citation:
            self._reference_context.append(self._end_tag(node, suffix='')) # sup

    def _visit_reference_intern_uri(self, node):
        docname = posixpath.normpath(
            self.docparent + path.splitext(node['refuri'].split('#')[0])[0])
        doctitle = ConfluenceState.title(docname)
        if not doctitle:
            ConfluenceLogger.warn('unable to build link to document due to '
                'missing title (in {}): {}'.format(self.docname, docname))

            # build a broken link
            self.body.append(self._start_tag(node, 'a', **{'href': '#'}))
            self._reference_context.append(self._end_tag(node, suffix=''))
            return

        anchor_value = None
        if '#' in node['refuri']:
            anchor = node['refuri'].split('#')[1]
            target_name = '{}#{}'.format(docname, anchor)

            # check if this target is reachable without an anchor; if so, use
            # the identifier value instead
            target = ConfluenceState.target(target_name)
            if target:
                anchor_value = target
                anchor_value = self._escape_sf(anchor_value)
            elif self.can_anchor:
                anchor_value = anchor

        # build link to internal anchor (on another page)
        #  Note: plain-text-link body cannot have inline markup; add the node
        #        contents into body and skip processing the rest of this node.
        doctitle = self._escape_sf(doctitle)
        self.body.append(self._start_ac_link(node, anchor_value))
        self.body.append(self._start_tag(node, 'ri:page',
            suffix=self.nl, empty=True, **{'ri:content-title': doctitle}))
        self.body.append(self._start_ac_link_body(node))
        self._reference_context.append(self._end_ac_link_body(node))
        self._reference_context.append(self._end_ac_link(node))

    def depart_reference(self, node):
        for element in self._reference_context:
            self.body.append(element)
        self._reference_context = []

    def visit_target(self, node):
        if 'refid' in node and self.can_anchor:
            anchor = ''.join(node['refid'].split())

            # only build an anchor if required (e.x. is a reference label
            # already provided by a build section element)
            target_name = '{}#{}'.format(self.docname, anchor)
            target = ConfluenceState.target(target_name)
            if not target:
                self.body.append(self._start_ac_macro(node, 'anchor'))
                self.body.append(self._build_ac_parameter(node, '', anchor))
                self.body.append(self._end_ac_macro(node))

        raise nodes.SkipNode

    # --------------------------------
    # references - footnotes/citations
    # --------------------------------

    def visit_footnote(self, node):
        label_node = node.next_node()
        if not isinstance(label_node, nodes.label):
            raise nodes.SkipNode

        # if the first foonote/citation, start building a table
        if not self._building_footnotes:
            self.body.append(self._start_tag(node, 'table', suffix=self.nl))
            self.context.append(self._end_tag(node))
            self.body.append(self._start_tag(node, 'tbody', suffix=self.nl))
            self.context.append(self._end_tag(node))
            self._building_footnotes = True

        label_text = label_node.astext()

        self.body.append(self._start_tag(node, 'tr', suffix=self.nl))
        self.context.append(self._end_tag(node))

        self.body.append(self._start_tag(node, 'td'))

        # footnote anchor
        if self.can_anchor:
            self.body.append(self._start_ac_macro(node, 'anchor'))
            self.body.append(self._build_ac_parameter(node, '', node['ids'][0]))
            self.body.append(self._end_ac_macro(node))

        # footnote label and back reference(s)
        if (not self.can_anchor
                or 'backrefs' not in node or not node['backrefs']):
            label_text = self._escape_sf(label_text)
            self.body.append(label_text)
        elif len(node['backrefs']) > 1:
            label_text = self._escape_sf(label_text)
            self.body.append(label_text)

            self.body.append(self._start_tag(node, 'div'))
            self.body.append(self._start_tag(node, 'em'))
            self.body.append('(')

            for idx, backref in enumerate(node['backrefs']):
                if idx != 0:
                    self.body.append(', ')
                self.body.append(self._start_ac_link(node, backref))
                self.body.append(
                    self._start_ac_plain_text_link_body_macro(node))
                self.body.append(self._escape_cdata(str(idx + 1)))
                self.body.append(self._end_ac_plain_text_link_body_macro(node))
                self.body.append(self._end_ac_link(node))
            self.body.append(')')
            self.body.append(self._end_tag(node, suffix='')) # em
            self.body.append(self._end_tag(node)) # div
        else:
            self.body.append(self._start_ac_link(node, node['backrefs'][0]))
            self.body.append(self._start_ac_plain_text_link_body_macro(node))
            self.body.append(self._escape_cdata(label_text))
            self.body.append(self._end_ac_plain_text_link_body_macro(node))
            self.body.append(self._end_ac_link(node))
        self.body.append(self._end_tag(node))

        self.body.append(self._start_tag(node, 'td'))
        self.context.append(self._end_tag(node))

    def depart_footnote(self, node):
        self.body.append(self.context.pop()) # td
        self.body.append(self.context.pop()) # tr

        # if next entry is not another footnote or citation, close off the table
        next_sibling = node.traverse(
            include_self=False, descend=False, siblings=True)
        if not next_sibling or not isinstance(
                next_sibling[0], (nodes.citation, nodes.footnote)):
            self.body.append(self.context.pop()) # tbody
            self.body.append(self.context.pop()) # table
            self._building_footnotes = False

    def visit_footnote_reference(self, node):
        text = "[{}]".format(node.astext())

        if not self.can_anchor:
            self.body.append(self._start_tag(node, 'sup'))
            self.body.append(self._escape_sf(text))
            self.body.append(self._end_tag(node, suffix='')) # sup
            raise nodes.SkipNode

        # build an anchor for back reference
        self.body.append(self._start_ac_macro(node, 'anchor'))
        self.body.append(self._build_ac_parameter(node, '', node['ids'][0]))
        self.body.append(self._end_ac_macro(node))

        # link to anchor
        target_anchor = ''.join(node['refid'].split())

        self.body.append(self._start_tag(node, 'sup'))
        self.body.append(self._start_ac_link(node, target_anchor))
        self.body.append(self._start_ac_plain_text_link_body_macro(node))
        self.body.append(self._escape_cdata(text))
        self.body.append(self._end_ac_plain_text_link_body_macro(node))
        self.body.append(self._end_ac_link(node))
        self.body.append(self._end_tag(node, suffix='')) # sup
        raise nodes.SkipNode

    def visit_label(self, node):
        # Label entries are skipped as their context has been already processed
        # from within footnote/citation processing (see visit_footnote).
        raise nodes.SkipNode

    visit_citation = visit_footnote
    depart_citation = depart_footnote

    # -------------
    # inline markup
    # -------------

    def visit_emphasis(self, node):
        self.body.append(self._start_tag(node, 'em'))
        self.context.append(self._end_tag(node, suffix=''))

    def depart_emphasis(self, node):
        self.body.append(self.context.pop()) # em

    def visit_literal(self, node):
        self.body.append(self._start_tag(node, 'code'))
        self.context.append(self._end_tag(node, suffix=''))

    def depart_literal(self, node):
        self.body.append(self.context.pop()) # code

    def visit_strong(self, node):
        self.body.append(self._start_tag(node, 'strong'))
        self.context.append(self._end_tag(node, suffix=''))

    def depart_strong(self, node):
        self.body.append(self.context.pop()) # strong

    def visit_subscript(self, node):
        self.body.append(self._start_tag(node, 'sub'))
        self.context.append(self._end_tag(node, suffix=''))

    def depart_subscript(self, node):
        self.body.append(self.context.pop()) # sub

    def visit_superscript(self, node):
        self.body.append(self._start_tag(node, 'sup'))
        self.context.append(self._end_tag(node, suffix=''))

    def depart_superscript(self, node):
        self.body.append(self.context.pop()) # sup

    visit_literal_emphasis = visit_emphasis
    depart_literal_emphasis = depart_emphasis
    visit_literal_strong = visit_strong
    depart_literal_strong = depart_strong
    visit_title_reference = visit_emphasis
    depart_title_reference = depart_emphasis

    # -------------
    # images markup
    # -------------

    def visit_caption(self, node):
        attribs = {}
        if 'align' in node.parent and node.parent['align'] == 'center':
            attribs['style'] = 'text-align: center;'

        self.body.append(self._start_tag(node, 'p', **attribs))
        self.context.append(self._end_tag(node))

    def depart_caption(self, node):
        self.body.append(self.context.pop()) # p

    def visit_figure(self, node):
        if self.can_admonition:
            self.body.append(self._start_ac_macro(node, 'info'))
            self.body.append(self._build_ac_parameter(node, 'icon', 'false'))
            self.body.append(self._start_ac_rich_text_body_macro(node))
            self.context.append(self._end_ac_rich_text_body_macro(node) +
                self._end_ac_macro(node))
        else:
            self.body.append(self._start_tag(
                node, 'hr', suffix=self.nl, empty=True))
            self.body.append(self._start_tag(node, 'div'))
            self.context.append(self._end_tag(node) + self._start_tag(
                node, 'hr', suffix=self.nl, empty=True))

    def depart_figure(self, node):
        self.body.append(self.context.pop()) # <dynamic>

    def visit_image(self, node):
        uri = node['uri']
        uri = self._escape_sf(uri)

        attribs = {}

        alignment = None
        if 'align' in node:
            alignment = node['align']
        elif isinstance(node.parent, nodes.figure) and 'align' in node.parent:
            alignment = node.parent['align']

        if alignment:
            alignment = self._escape_sf(alignment)
            attribs['ac:align'] = alignment
            if alignment == 'right':
                attribs['ac:style'] = 'float: right;'

        if 'alt' in node:
            alt = node['alt']
            alt = self._escape_sf(alt)
            attribs['ac:alt'] = alt

        if 'height' in node:
            self.warn('height value for image is unsupported in confluence')

        if 'width' in node:
            width = node['width']
            attribs['ac:width'] = width

            if not width.endswith('px'):
                self.warn('unsupported unit type for confluence: ' + width)

        if uri.find('://') != -1 or uri.startswith('data:'):
            # an external or embedded image
            #
            # Note: it would be rare that embedded images will be detected at
            #       this stage as Sphinx's post-transform processor would
            #       translate these images into embedded images. Nonetheless an
            #       embedded image is still stacked into Confluence image
            #       entity (although, currently, some (if not all) Confluence
            #       versions do not consider embedded images as valid URI values
            #       so users might see a "broken images" block).
            self.body.append(self._start_ac_image(node, **attribs))
            self.body.append(self._start_tag(node, 'ri:url',
                suffix=self.nl, empty=True, **{'ri:value': uri}))
            self.body.append(self._end_ac_image(node))
        else:
            image_key, _ = self.assets.interpretAssetKeyPath(node)
            hosting_docname = self.assets.asset2docname(image_key)
            hosting_doctitle = ConfluenceState.title(hosting_docname)
            hosting_doctitle = self._escape_sf(hosting_doctitle)

            self.body.append(self._start_ac_image(node, **attribs))
            self.body.append(self._start_ri_attachment(node, image_key))
            if hosting_docname != self.docname:
                self.body.append(self._start_tag(node, 'ri:page',
                   suffix=self.nl, empty=True,
                   **{'ri:content-title': hosting_doctitle}))
            self.body.append(self._end_ri_attachment(node))
            self.body.append(self._end_ac_image(node))

        raise nodes.SkipNode

    visit_legend = visit_paragraph
    depart_legend = depart_paragraph

    # ------------------
    # sphinx -- download
    # ------------------

    def visit_download_reference(self, node):
        uri = node['reftarget']
        uri = self._escape_sf(uri)

        if uri.find('://') != -1:
            self.body.append(self._start_tag(node, 'a', **{'href': uri}))
            self.context.append(self._end_tag(node, suffix=''))
        else:
            file_key, _ = self.assets.interpretAssetKeyPath(node)
            hosting_docname = self.assets.asset2docname(file_key)
            hosting_doctitle = ConfluenceState.title(hosting_docname)
            hosting_doctitle = self._escape_sf(hosting_doctitle)

            # If the view-file macro is permitted along with it not being an
            # explicitly referenced asset.
            if self.can_viewfile and (not 'refexplicit' in node or
                    not node['refexplicit']):
                # a 'view-file' macro takes an attachment tag as a body; build
                # the tags in an interim list
                attachment = []
                attachment.append(self._start_ri_attachment(node, file_key))
                if hosting_docname != self.docname:
                    attachment.append(self._start_tag(node, 'ri:page',
                       suffix=self.nl, empty=True,
                       **{'ri:content-title': hosting_doctitle}))
                attachment.append(self._end_ri_attachment(node))

                self.body.append(self._start_ac_macro(node, 'view-file'))
                self.body.append(self._build_ac_parameter(
                    node, 'name', ''.join(attachment)))
                self.body.append(self._end_ac_macro(node))
            else:
                self.body.append(self._start_ac_link(node))
                self.body.append(self._start_ri_attachment(node, file_key))
                if hosting_docname != self.docname:
                    self.body.append(self._start_tag(node, 'ri:page',
                       suffix=self.nl, empty=True,
                       **{'ri:content-title': hosting_doctitle}))
                self.body.append(self._end_ri_attachment(node))
                self.body.append(
                    self._start_ac_plain_text_link_body_macro(node))
                self.body.append(self._escape_cdata(node.astext()))
                self.body.append(self._end_ac_plain_text_link_body_macro(node))
                self.body.append(self._end_ac_link(node))

        raise nodes.SkipNode

    # ------------------
    # sphinx -- glossary
    # ------------------

    def visit_glossary(self, node):
        # ignore glossary wrapper; glossary is built with definition_list
        pass

    def depart_glossary(self, node):
        pass

    def visit_index(self, node):
        # glossary index information is not needed; skipped
        raise nodes.SkipNode

    # -----------------
    # sphinx -- manpage
    # -----------------

    def visit_manpage(self, node):
        self.visit_emphasis(node)
        if self._manpage_url:
            node['refuri'] = self._manpage_url.format(**node.attributes)
            self._visit_reference_extern(node)

    def depart_manpage(self, node):
        if self._manpage_url:
            self.depart_reference(node)
        self.depart_emphasis(node)

    # --------------
    # sphinx -- math
    # --------------

    def visit_math(self, node):
        # unsupported
        raise nodes.SkipNode

    def visit_displaymath(self, node):
        # unsupported
        raise nodes.SkipNode

    def visit_eqref(self, node):
        # unsupported
        raise nodes.SkipNode

    # -------------------------
    # sphinx -- production list
    # -------------------------

    def visit_productionlist(self, node):
        max_len = max(len(production['tokenname']) for production in node)

        self.body.append(self._start_tag(node, 'pre'))

        for production in node:
            if production['tokenname']:
                formatted_token = production['tokenname'].ljust(max_len)
                formatted_token = self._escape_sf(formatted_token)
                self.body.append('{} ::='.format(formatted_token))
                lastname = production['tokenname']
            else:
                self.body.append('{}    '.format(' ' * len(lastname)))
            text = production.astext()
            text = self._escape_sf(text)
            self.body.append(text + self.nl)

        self.body.append(self._end_tag(node))
        raise nodes.SkipNode

    # -----------------
    # sphinx -- toctree
    # -----------------

    def visit_compound(self, node):
        # If this has not been a manipulated toctree (refer to hierarchy mode
        # and see builder's process_tree_structure) and the invoker wishes to
        # use Confluence children macro instead, swap out of the toctree for the
        # macro.
        if 'toctree-wrapper' in node['classes']:
            if self.apply_hierarchy_children_macro:
                self.body.append(self._start_ac_macro(node, 'children'))
                if self._tocdepth:
                    self.body.append(self._build_ac_parameter(
                        node, 'depth', str(self._tocdepth)))
                else:
                    self.body.append(self._build_ac_parameter(
                        node, 'all', 'true'))
                self.body.append(self._end_ac_macro(node))
                raise nodes.SkipNode

    def depart_compound(self, node):
        pass

    # -----------------------
    # sphinx -- miscellaneous
    # -----------------------

    def visit_rubric(self, node):
        self.body.append(self._start_tag(node, 'h{}'.format(self._title_level)))
        self.context.append(self._end_tag(node))

    def depart_rubric(self, node):
        self.body.append(self.context.pop()) # h<x>

    def visit_seealso(self, node):
        self._visit_admonition(node, 'info', admonitionlabels['seealso'])

    depart_seealso = _depart_admonition

    def visit_versionmodified(self, node):
        if node['type'] == 'deprecated' or node['type'] == 'versionchanged':
            self._visit_note(node)
        elif node['type'] == 'versionadded':
            self._visit_info(node)
        else:
            ConfluenceLogger.warn('unsupported version modification type: '
                '{}'.format(node['type']))
            self._visit_info(node)

    depart_versionmodified = _depart_admonition

    # ------------------------------
    # sphinx -- extension -- autodoc
    # ------------------------------

    def visit_desc(self, node):
        self.body.append(self._start_tag(node, 'dl', suffix=self.nl))
        self.context.append(self._end_tag(node))

    def depart_desc(self, node):
        self.body.append(self.context.pop()) # dl

    def visit_desc_signature(self, node):
        self.body.append(self._start_tag(node, 'dt'))
        self.context.append(self._end_tag(node))

    def depart_desc_signature(self, node):
        self.body.append(self.context.pop()) # dt

    def visit_desc_annotation(self, node):
        self.body.append(self._start_tag(node, 'em'))
        self.context.append(self._end_tag(node, suffix=''))

    def depart_desc_annotation(self, node):
        self.body.append(self.context.pop()) # em

    def visit_desc_addname(self, node):
        self.body.append(self._start_tag(node, 'code'))
        self.context.append(self._end_tag(node, suffix=''))

    def depart_desc_addname(self, node):
        self.body.append(self.context.pop()) # code

    def visit_desc_name(self, node):
        self.body.append(self._start_tag(node, 'strong'))
        self.context.append(self._end_tag(node, suffix=''))
        self.body.append(self._start_tag(node, 'code'))
        self.context.append(self._end_tag(node, suffix=''))

    def depart_desc_name(self, node):
        self.body.append(self.context.pop()) # code
        self.body.append(self.context.pop()) # strong

    def visit_desc_type(self, node):
        pass

    def depart_desc_type(self, node):
        pass

    def visit_desc_returns(self, node):
        self.body.append(' -&gt; ')

    def depart_desc_returns(self, node):
        pass

    def visit_desc_optional(self, node):
        self.body.append('[')

    def depart_desc_optional(self, node):
        self.body.append(']')

    def visit_desc_parameterlist(self, node):
        self._first_desc_parameter = True
        self.body.append('(')

    def depart_desc_parameterlist(self, node):
        self.body.append(')')

    def visit_desc_parameter(self, node):
        if self._first_desc_parameter:
            self._first_desc_parameter = False
        else:
            self.body.append(', ')

        self.body.append(self._start_tag(node, 'em'))
        self.context.append(self._end_tag(node, suffix=''))

    def depart_desc_parameter(self, node):
        self.body.append(self.context.pop()) # em

    def visit_desc_content(self, node):
        self.body.append(self._start_tag(node, 'dd'))
        self.context.append(self._end_tag(node))

    def depart_desc_content(self, node):
        self.body.append(self.context.pop()) # dd

    # -----------------------------------------------------
    # docutils handling "to be completed" marked directives
    # -----------------------------------------------------

    def visit_citation_reference(self, node):
        raise nodes.SkipNode

    def visit_compact_paragraph(self, node):
        pass

    def depart_compact_paragraph(self, node):
        pass

    def visit_container(self, node):
        pass

    def depart_container(self, node):
        pass

    def visit_generated(self, node):
        pass

    def depart_generated(self, node):
        pass

    def visit_pending_xref(self, node):
        raise nodes.SkipNode

    def visit_problematic(self, node):
        raise nodes.SkipNode

    def visit_system_message(self, node):
        raise nodes.SkipNode

    # -------------
    # miscellaneous
    # -------------

    def visit_abbreviation(self, node):
        attribs = {}
        if 'explanation' in node:
            title_value = node['explanation']
            title_value = self._escape_sf(title_value)
            attribs['title'] = title_value

        self.body.append(self._start_tag(node, 'abbr', **attribs))
        self.context.append(self._end_tag(node, suffix=''))

    def depart_abbreviation(self, node):
        self.body.append(self.context.pop()) # abbr

    def visit_acks(self, node):
        raise nodes.SkipNode

    def visit_acronym(self, node):
        # Note: docutils indicates this directive is "to be completed"

        self.body.append(self._start_tag(node, 'acronym'))
        self.context.append(self._end_tag(node, suffix=''))

    def depart_acronym(self, node):
        self.body.append(self.context.pop()) # acronym

    def visit_centered(self, node):
        # centered is deprecated; ignore
        pass

    def depart_centered(self, node):
        pass

    def visit_comment(self, node):
        raise nodes.SkipNode

    def visit_hlist(self, node):
        # unsupported
        raise nodes.SkipNode

    def visit_inline(self, node):
        # ignoring; no need to handle specific inline entries
        pass

    def depart_inline(self, node):
        pass

    def visit_line(self, node):
        # ignoring; no need to handle specific line entries
        pass

    def depart_line(self, node):
        pass

    def visit_line_block(self, node):
        self.body.append(self._start_tag(node, 'p'))
        self.context.append(self._end_tag(node))

    def depart_line_block(self, node):
        self.body.append(self.context.pop()) # p

    def visit_raw(self, node):
        if 'confluence' in node.get('format', '').split():
            self.body.append(self.nl.join(node.astext().splitlines()))
        raise nodes.SkipNode

    def visit_sidebar(self, node):
        # unsupported
        raise nodes.SkipNode

    def visit_substitution_definition(self, node):
        raise nodes.SkipNode

    def visit_start_of_file(self, node):
        # ignore managing state of inlined documents
        pass

    def depart_start_of_file(self, node):
        pass

    # ##########################################################################
    # #                                                                        #
    # # helpers                                                                #
    # #                                                                        #
    # ##########################################################################

    def _start_tag(self, node, tag, suffix=None, empty=False, **kwargs):
        """
        generates start tag content for a given node

        A helper used to return content to be appended to a document which
        initializes the start of a storage format element (i.e. generates a
        start tag). The element of type `tag` will be initialized. This method
        may use provided `node` to tweak the final content.

        Args:
            node: the node processing the start-tag
            tag: the type of tag
            suffix (optional): the suffix to add (defaults to nothing)
            empty (optional): tag will not hold child nodes (defaults to False)
            **kwargs (optional): dictionary of attributes to include in the tag

        Returns:
            the content
        """
        tag = tag.lower()
        data = [tag]

        attribs = {}
        for key, value in kwargs.items():
            attribs[key.lower()] = value

        for key, value in sorted(attribs.items()):
            data.append('{}="{}"'.format(key, value))

        if suffix is None:
            suffix = ''

        suffix = '>' + suffix
        if empty:
            suffix = ' /' + suffix
        else:
            try:
                node.__confluence_tag.append(tag)
            except AttributeError:
                node.__confluence_tag = [tag]

        return '<{}{}'.format(' '.join(data), suffix)

    def _end_tag(self, node, suffix=None):
        """
        generates end tag content for a given node

        A helper used to return content to be appended to a document which
        finalizes a storage format element (i.e. generates an end tag). This
        method should* be used to help close a _start_tag call (*with the
        exception of when _start_tag is invoked with empty=True).

        Args:
            node: the node processing the end-tag
            suffix (optional): the suffix to add (defaults to newline)

        Returns:
            the content
        """
        try:
            tag = node.__confluence_tag.pop()
        except:
            raise ConfluenceError('end tag invoke without matching start tag')

        if suffix is None:
            suffix = self.nl

        return '</{}>{}'.format(tag, suffix)

    def _build_ac_parameter(self, node, name, value):
        """
        generates a confluence parameter element

        A helper used to return content to be appended to a document which
        builds a complete storage format parameter element. The 'ac:parameter'
        element will be built. This method may use provided `node` to tweak the
        final content.

        Args:
            node: the node processing the parameter
            name: the parameter name
            value: the value for the parameter

        Returns:
            the content
        """
        return (self._start_tag(node, 'ac:parameter', **{'ac:name': name}) +
            value + self._end_tag(node))

    def _start_ac_image(self, node, **kwargs):
        """
        generates a confluence image start tag

        A helper used to return content to be appended to a document which
        initializes the start of a storage format image element. The 'ac:image'
        element will be initialized. This method may use provided `node` to
        tweak the final content.

        Args:
            node: the node processing the image

        Returns:
            the content
        """
        return self._start_tag(node, 'ac:image', suffix=self.nl, **kwargs)

    def _end_ac_image(self, node):
        """
        generates confluence image end tag content for a node

        A helper used to return content to be appended to a document which
        finalizes a storage format image element. This method should be used to
        help close a _start_ac_image call.

        Args:
            node: the node processing the image

        Returns:
            the content
        """
        return self._end_tag(node, suffix='')

    def _start_ac_link(self, node, anchor=None):
        """
        generates a confluence link start tag

        A helper used to return content to be appended to a document which
        initializes the start of a storage format link element of a specific
        `type`. The 'ac:link' element will be initialized. This method may use
        provided `node` to tweak the final content.

        Args:
            node: the node processing the link
            anchor (optional): the anchor value to use (defaults to None)

        Returns:
            the content
        """
        attribs = {}
        if anchor:
            attribs['ac:anchor'] = anchor
        return self._start_tag(node, 'ac:link', suffix=self.nl, **attribs)

    def _end_ac_link(self, node):
        """
        generates confluence link end tag content for a node

        A helper used to return content to be appended to a document which
        finalizes a storage format link element. This method should be used to
        help close a _start_ac_link call.

        Args:
            node: the node processing the link

        Returns:
            the content
        """
        return self._end_tag(node, suffix='')

    def _start_ac_macro(self, node, type, empty=False):
        """
        generates a confluence macro start tag

        A helper used to return content to be appended to a document which
        initializes the start of a storage format macro element of a specific
        `type`. The 'ac:structured-macro' element will be initialized. This
        method may use provided `node` to tweak the final content.

        Args:
            node: the node processing the macro
            type: the type of macro
            empty (optional): tag will not hold child nodes (defaults to False)

        Returns:
            the content
        """
        return self._start_tag(node, 'ac:structured-macro',
            suffix=self.nl, empty=empty, **{'ac:name': type})

    def _end_ac_macro(self, node):
        """
        generates confluence macro end tag content for a node

        A helper used to return content to be appended to a document which
        finalizes a storage format macro element. This method should* be used to
        help close a _start_ac_macro call (*with the exception of when
        _start_ac_macro is invoked with empty=True).

        Args:
            node: the node processing the macro

        Returns:
            the content
        """
        return self._end_tag(node)

    def _start_ac_link_body(self, node):
        """
        generates a confluence link-body start tag

        A helper used to return content to be appended to a document which
        initializes the start of a storage format link-body element. The
        'ac:link-body' element will be initialized. This method may use provided
        `node` to tweak the final content.

        Args:
            node: the node processing the macro

        Returns:
            the content
        """
        return self._start_tag(node, 'ac:link-body')

    def _end_ac_link_body(self, node):
        """
        generates confluence link-body end tag content for a node

        A helper used to return content to be appended to a document which
        finalizes a storage format link-body element. This method should be used
        to help close a _start_ac_link_body call.

        Args:
            node: the node processing the macro

        Returns:
            the content
        """
        return self._end_tag(node)

    def _start_ac_rich_text_body_macro(self, node):
        """
        generates a confluence rich-text-body start tag

        A helper used to return content to be appended to a document which
        initializes the start of a storage format rich-text-body element. The
        'ac:rich-text-body' element will be initialized. This method may use
        provided `node` to tweak the final content.

        Args:
            node: the node processing the macro

        Returns:
            the content
        """
        return self._start_tag(node, 'ac:rich-text-body', suffix=self.nl)

    def _end_ac_rich_text_body_macro(self, node):
        """
        generates confluence rich-text-body end tag content for a node

        A helper used to return content to be appended to a document which
        finalizes a storage format rich-text-body element. This method should
        be used to help close a _start_ac_rich_text_body_macro call.

        Args:
            node: the node processing the macro

        Returns:
            the content
        """
        return self._end_tag(node)

    def _start_ac_plain_text_body_macro(self, node):
        """
        generates a confluence plain-text-body start tag

        A helper used to return content to be appended to a document which
        initializes the start of a storage format plain-text-body element. The
        'ac:plain-text-body' element will be initialized. This method may use
        provided `node` to tweak the final content.

        Args:
            node: the node processing the macro

        Returns:
            the content
        """
        return self._start_tag(node, 'ac:plain-text-body', suffix='<![CDATA[')

    def _end_ac_plain_text_body_macro(self, node):
        """
        generates confluence plain-text-body end tag content for a node

        A helper used to return content to be appended to a document which
        finalizes a storage format plain-text-body element. This method should
        be used to help close a _start_ac_plain_text_body_macro call.

        Args:
            node: the node processing the macro

        Returns:
            the content
        """
        return ']]>' + self._end_tag(node)

    def _start_ac_plain_text_link_body_macro(self, node):
        """
        generates a confluence plain-text-link-body start tag

        A helper used to return content to be appended to a document which
        initializes the start of a storage format plain-text-body element. The
        'ac:plain-text-body' element will be initialized. This method may use
        provided `node` to tweak the final content.

        Args:
            node: the node processing the macro

        Returns:
            the content
        """
        return self._start_tag(node, 'ac:plain-text-link-body',
            suffix='<![CDATA[')

    def _end_ac_plain_text_link_body_macro(self, node):
        """
        generates confluence plain-text-link-body end tag content for a node

        A helper used to return content to be appended to a document which
        finalizes a storage format plain-text-link-body element. This method
        should be used to help close a _start_ac_plain_text_link_body_macro
        call.

        Args:
            node: the node processing the macro

        Returns:
            the content
        """
        return ']]>' + self._end_tag(node)

    def _start_ri_attachment(self, node, filename):
        """
        generates a confluence attachment start tag

        A helper used to return content to be appended to a document which
        initializes the start of a storage format attachment element. The
        'ri:attachment' element will be initialized. This method may use
        provided `node` to tweak the final content.

        Args:
            node: the node processing the attachment
            filename: the filename of the attachment

        Returns:
            the content
        """
        return self._start_tag(node, 'ri:attachment',
            **{'ri:filename': filename})

    def _end_ri_attachment(self, node):
        """
        generates confluence attachment end tag content for a node

        A helper used to return content to be appended to a document which
        finalizes a storage format attachment element. This method should be
        used to help close a _start_ri_attachment call.

        Args:
            node: the node processing the attachment

        Returns:
            the content
        """
        return self._end_tag(node)

    def _escape_cdata(self, data):
        """
        escapes text to be inserted into a cdata

        A helper used to return content that has been properly escaped and can
        be directly placed inside a CDATA container.

        Args:
            data: the text

        Returns:
            the escaped text
        """
        return data.replace(']]>', ']]]]><![CDATA[>')

    def _escape_sf(self, data):
        """
        escapes text to be inserted directly into a storage format area

        A helper used to return content that has been properly escaped and can
        be directly placed inside a Confluence storage-format-prepared document.

        Args:
            data: the text

        Returns:
            the escaped text
        """
        STORAGE_FORMAT_REPLACEMENTS = {
            ('<', '&lt;'),
            ('>', '&gt;'),
            ('"', '&quot;'),
            ("'", '&apos;'),
        }

        # first pass needs to handle ampersand
        data = data.replace('&', '&amp;')

        for find, encoded in STORAGE_FORMAT_REPLACEMENTS:
            data = data.replace(find, encoded)
        return data
