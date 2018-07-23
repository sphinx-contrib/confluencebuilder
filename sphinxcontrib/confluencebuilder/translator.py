# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2016-2018 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from __future__ import unicode_literals
from .exceptions import ConfluenceError
from .logger import ConfluenceLogger
from .std.confluence import LITERAL2LANG_MAP
from .std.sphinx import DEFAULT_HIGHLIGHT_STYLE
from docutils import nodes
from docutils.nodes import NodeVisitor as BaseTranslator
from os import path
import io
import sys

class ConfluenceTranslator(BaseTranslator):
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

        self.body = []
        self.context = []
        self.nl = '\n'
        self._quote_level = 0
        self._section_level = 1

        if config.highlight_language:
            self._highlight = config.highlight_language
        else:
            self._highlight = DEFAULT_HIGHLIGHT_STYLE
        self._linenothreshold = sys.maxsize

        # helpers for dealing with disabled/unsupported macros
        restricted_macros = config.confluence_adv_restricted_macros
        self.can_admonition = not 'info' in restricted_macros
        self.can_anchor = not 'anchor' in restricted_macros
        self.can_code = not 'code' in restricted_macros

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
        if isinstance(node.parent, nodes.section):
            self.body.append(
                self._start_tag(node, 'h{}'.format(self._title_level)))
            self.context.append(self._end_tag(node))

    def depart_title(self, node):
        if isinstance(node.parent, nodes.section):
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

    # ----------------------
    # body elements -- lists
    # ----------------------

    def visit_bullet_list(self, node):
        self.body.append(self._start_tag(node, 'ul', suffix=self.nl))
        self.context.append(self._end_tag(node))

    def depart_bullet_list(self, node):
        self.body.append(self.context.pop()) # ul

    def visit_enumerated_list(self, node):
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

        attribs = {}
        if list_style_type:
            attribs['style'] = 'list-style-type: {};'.format(list_style_type)

        self.body.append(self._start_tag(node, 'ol', suffix=self.nl, **attribs))
        self.context.append(self._end_tag(node))

    def depart_enumerated_list(self, node):
        self.body.append(self.context.pop()) # ol

    def visit_list_item(self, node):
        self.body.append(self._start_tag(node, 'li', suffix=self.nl))
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
        self.context.append(self._end_tag(node, suffix='')) # strong

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
        lang = node.get('language', self._highlight)
        if self.builder.lang_transform:
            lang = self.builder.lang_transform(lang)
        elif lang in LITERAL2LANG_MAP.keys():
            lang = LITERAL2LANG_MAP[lang]
        else:
            ConfluenceLogger.warn('unknown code language: {}'.format(lang))
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
            CONFLUENCE_DEFAULT_INDENT_VAL = 30;
            indent_val = CONFLUENCE_DEFAULT_INDENT_VAL * self._quote_level
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
            if isinstance(next_child[0], nodes.block_quote):
                firstchild_margin = False

            if firstchild_margin:
                CONFLUENCE_DEFAULT_FCI = 10;
                style += 'padding-top: {}px;'.format(CONFLUENCE_DEFAULT_FCI)

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

        for key, value in attribs.items():
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
