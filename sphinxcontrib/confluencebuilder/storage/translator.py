# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)
# Copyright 2018-2020 by the Sphinx team (sphinx-doc/sphinx#AUTHORS)

from __future__ import annotations
from contextlib import suppress
from docutils import nodes
from functools import wraps
from pathlib import Path
from sphinx import addnodes
from sphinx.locale import _ as SL
from sphinx.locale import admonitionlabels
from sphinxcontrib.confluencebuilder.compat import docutils_findall as findall
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceError
from sphinxcontrib.confluencebuilder.locale import L
from sphinxcontrib.confluencebuilder.nodes import confluence_parameters_fetch as PARAMS
from sphinxcontrib.confluencebuilder.std.confluence import CONFLUENCE_DEFAULT_V2_TABLE_WIDTH
from sphinxcontrib.confluencebuilder.std.confluence import CONFLUENCE_MAX_WIDTH
from sphinxcontrib.confluencebuilder.std.confluence import FALLBACK_HIGHLIGHT_STYLE
from sphinxcontrib.confluencebuilder.std.confluence import FCMMO
from sphinxcontrib.confluencebuilder.std.confluence import INDENT
from sphinxcontrib.confluencebuilder.std.confluence import LITERAL2LANG_FBMAP_V1
from sphinxcontrib.confluencebuilder.std.confluence import LITERAL2LANG_FBMAP_V2
from sphinxcontrib.confluencebuilder.std.confluence import LITERAL2LANG_MAP_V1
from sphinxcontrib.confluencebuilder.std.confluence import LITERAL2LANG_MAP_V2
from sphinxcontrib.confluencebuilder.std.confluence import SUPPORTED_CODE_BLOCK_THEMES
from sphinxcontrib.confluencebuilder.std.sphinx import DEFAULT_HIGHLIGHT_STYLE
from sphinxcontrib.confluencebuilder.storage import encode_storage_format
from sphinxcontrib.confluencebuilder.storage import intern_uri_anchor_value
from sphinxcontrib.confluencebuilder.translator import ConfluenceBaseTranslator
from sphinxcontrib.confluencebuilder.util import convert_length
from sphinxcontrib.confluencebuilder.util import extract_length
from sphinxcontrib.confluencebuilder.util import first
import json
import posixpath
import re
import sys


def visit_auto_context_decorator():
    """
    node visit decorator

    Prepares a context for a given node type that can help populate a list
    of completion tags which a depart implementation can automatically append
    when using the ``depart_auto_context_decorator``. A visiting node will
    include this decorator and use ``auto_append`` in the translator to queue
    any tags that should be automatically added. For a node's depart call,
    if applied the ``depart_auto_context_decorator`` decorator, the queued
    tags will be applied to the body.
    """
    def _decorator(func):
        @wraps(func)
        def _wrapper(self, *args, **kwargs):
            self._auto_context.append([])

            try:
                return func(self, *args, **kwargs)
            except nodes.SkipNode:
                self._auto_context.pop()
                raise

        return _wrapper
    return _decorator


def depart_auto_context_decorator():
    """
    depart visit decorator

    To help automatically apply pending tags to the body. See
    ``visit_auto_context_decorator`` for more information.
    """
    def _decorator(func):
        @wraps(func)
        def _wrapper(self, *args, **kwargs):
            rv = func(self, *args, **kwargs)
            ctx = self._auto_context.pop()
            for element in reversed(ctx):
                self.body.append(element)
            return rv

        return _wrapper
    return _decorator


class ConfluenceStorageFormatTranslator(ConfluenceBaseTranslator):
    __tracked_deprecated = False
    _tracked_unknown_code_lang: list[str] = []

    """
    confluence storage format extension translator

    A storage format-specific translator instance for the Confluence extension
    for Sphinx.

    Args:
        document: the document being translated
        builder: the sphinx builder instance
    """
    def __init__(self, document, builder):
        ConfluenceBaseTranslator.__init__(self, document, builder)
        config = builder.config
        metadata = builder.metadata.get(self.docname, {})

        self.add_secnumbers = config.confluence_add_secnumbers
        self.editor = config.confluence_editor
        self.confluence_full_width = config.confluence_full_width
        self.numfig = config.numfig
        self.numfig_format = config.numfig_format
        self.secnumber_suffix = config.confluence_secnumber_suffix
        self.todo_include_todos = getattr(config, 'todo_include_todos', None)
        self._auto_context = []
        self._building_footnotes = False
        self._figure_context = []
        self._indent_level = 0
        self._list_context = ['']
        self._manpage_url = getattr(config, 'manpages_url', None)
        self._needs_navnode_spacing = False
        self._reference_context = []
        self._thead_context = []
        self._v2_header_added = False
        self.colspecs = []
        self._tocdepth = self.state.toctree_depth(self.docname)

        # override editor if the document specifies another
        editor_override = metadata.get('editor')
        if editor_override and self.builder.name != 'singleconfluence':
            self.editor = editor_override

        # override full-width option if the document hints to override
        fw_override = metadata.get('fullWidth')
        if fw_override and self.builder.name != 'singleconfluence':
            self.confluence_full_width = (fw_override == 'true')

        # helper to track a v2 editor
        self.v2 = self.editor == 'v2'

    def encode(self, text):
        text = encode_storage_format(text)
        return ConfluenceBaseTranslator.encode(self, text)

    # ---------
    # structure
    # ---------

    def auto_append(self, entity):
        self._auto_context[-1].append(entity)

    def get_secnumber(self, node):
        if node.get('secnumber'):
            return node['secnumber']

        if isinstance(node.parent, nodes.section):
            if self.builder.name == 'singleconfluence':
                docname = self._docnames[-1]
                raw_anchor = node.parent['ids'][0]
                anchorname = f'{docname}/#{raw_anchor}'
                if anchorname not in self.builder.secnumbers:
                    anchorname = f'{raw_anchor}/'
            else:
                anchorname = '#' + node.parent['ids'][0]
                if anchorname not in self.builder.secnumbers:
                    anchorname = ''

            if self.builder.secnumbers.get(anchorname):
                return self.builder.secnumbers[anchorname]

        return None

    def build_secnumber(self, node):
        if not self.add_secnumbers:
            return ''

        secnumber = self.get_secnumber(node)
        if not secnumber:
            return ''

        return '.'.join(map(str, secnumber)) + self.secnumber_suffix

    def add_secnumber(self, node):
        secnumber = self.build_secnumber(node)
        if secnumber:
            self.body.append(secnumber)

    def build_fignumber(self, node):
        if not self.numfig or not node['ids']:
            return ''

        figtype = self.builder.env.domains['std'].get_enumerable_node_type(node)
        if not figtype:
            return ''

        if self.builder.name == 'singleconfluence':
            key = f'{self._docnames[-1]}/{figtype}'
        else:
            key = figtype

        figid = first(node['ids'])
        if figid in self.builder.fignumbers.get(key, {}):
            prefix = self.numfig_format.get(figtype)
            if prefix:
                numbers = self.builder.fignumbers[key][figid]
                return prefix % '.'.join(map(str, numbers)) + ' '

        return ''

    def add_fignumber(self, node):
        fignumber = self.build_fignumber(node)
        if fignumber:
            self.body.append(fignumber)

    def visit_start_of_file(self, node):
        ConfluenceBaseTranslator.visit_start_of_file(self, node)

        # ensure document target exists for singleconfluence
        #
        # When references to individual documents are built, they will use the
        # target mapping which should (in theory) be the section title generated
        # for the specific document. In the event that a page does not have a
        # title, there will be no target to map to. The fallback for these
        # references is to just link to the anchor point on a page matching the
        # target document's docname value. If it is detected that there is no
        # target registered for a given document (since it's titleless), build
        # an anchor point with the name matching the title (which allows the
        # fallback link to jump to the desired point in a document).
        if self.builder.name == 'singleconfluence':
            doc_anchorname = '/#' + node['docname']
            doc_target = self.state.target(doc_anchorname)
            if not doc_target:
                doc_id = node['docname']
                self._build_anchor(node, doc_id)

    def pre_body_data(self):
        data = ''

        # Confluence's v1 editor ignores a full-width page style on
        # publication (most likely since the concept of page width was
        # developed for v2 and newer). To emulate a non-full-width state with
        # a v1 editor, apply a layout around the page contents.
        if not self.v2 and self.confluence_full_width is False:
            if self.builder.cloud:
                data += '<ac:layout>'
                data += '<ac:layout-section ac:type="fixed-width">'
                data += '<ac:layout-cell>'
            else:
                max_width = f'{CONFLUENCE_MAX_WIDTH}px'
                data += f'<div style="max-width: {max_width}; margin: 0 auto;">'

        return data

    def post_body_data(self):
        data = ''

        if not self.v2 and self.confluence_full_width is False:
            if self.builder.cloud:
                data += '</ac:layout-cell>'
                data += '</ac:layout-section>'
                data += '</ac:layout>'
            else:
                data += '</div>'

        return data

    def visit_title(self, node):
        if isinstance(node.parent, (nodes.section, nodes.topic)):
            new_targets = []

            self.body.append(self.start_tag(node, f'h{self._title_level}'))

            if self.builder.name == 'singleconfluence':
                docname = self._docnames[-1]
            else:
                docname = self.docname

            # For v2, will will generate section anchors inside the title
            # area for the following reasons:
            # - We want to create inside the header inside if we input anchors
            #    before the header, it increase the space above the anchor
            #    due to how v2 styles a page.
            # - We are generating compatible anchor links (prefixed with the
            #    repsective document name) which helps allow `ac:link` macros
            #    properly link when coming from v1 or v2 editor pages.
            if self.v2 and 'names' in node.parent:
                for name in node.parent['names']:
                    anchor = name.replace(' ', '-')
                    target_name = f'{docname}/#{anchor}'
                    target = self.state.target(target_name)
                    if target and target not in new_targets:
                        self._build_anchor(node, target)
                        new_targets.append(target)

            # For MyST sections with an auto-generated slug, we will use this
            # slug to build an anchor target for anchor links defined in a
            # Markdown page.
            slug = node.parent.get('slug')
            if slug:
                target_name = f'{docname}/#{slug}'
                target = self.state.target(target_name)
                if target and target not in new_targets:
                    self._build_anchor(node, target)
                    new_targets.append(target)

            self.add_secnumber(node)
            self.add_fignumber(node.parent)
            self.context.append(self.end_tag(node))

            # if title points to a section and does not already contain a
            # reference, create a link to it
            if 'refid' in node and not node.next_node(nodes.reference):
                anchor_value = ''.join(node['refid'].split())
                self.body.append(self.start_ac_link(node, anchor_value))
                self.body.append(self.start_ac_link_body(node))
                self.context.append(self.end_ac_link_body(node) +
                    self.end_ac_link(node))
        elif (isinstance(node.parent, addnodes.compact_paragraph) and
                node.parent.get('toctree')):
            self.visit_caption(node)
        else:
            # Only render section/topic titles in headers. For all other nodes,
            # they must explicitly manage their own title entries.
            raise nodes.SkipNode

    def depart_title(self, node):
        if isinstance(node.parent, (nodes.section, nodes.topic)):
            if 'refid' in node and not node.next_node(nodes.reference):
                self.body.append(self.context.pop())  # link

            self.body.append(self.context.pop())  # h<x>
        elif (isinstance(node.parent, addnodes.compact_paragraph) and
                node.parent.get('toctree')):
            self.depart_caption(node)

    def visit_paragraph(self, node):
        attribs = {}
        style = ''

        # if this is a v2 editor, apply the left margin offset now directly
        # on the paragraph since the v2 editor does not permit nesting
        # block elements for indentation
        if self.v2 and self._indent_level > 0:
            offset = INDENT * self._indent_level
            style += f'margin-left: {offset}px;'

        # MyST-Parser will inject text-align hints in the node's classes
        # attribute; if set, attempt to apply the style
        if isinstance(node.parent, nodes.entry):
            for class_ in node.parent.get('classes', []):
                if class_ == 'text-center':
                    style += 'text-align: center;'
                elif class_ == 'text-right':
                    style += 'text-align: right;'
                # (legacy)
                elif class_.startswith('text-align:'):
                    style += self.encode(class_)
                    break

        if style:
            attribs['style'] = style

        self.body.append(self.start_tag(node, 'p', **attribs))

        # build anchors for ids which references may want to link to
        #
        # This was originally handled in `visit_target`, but moved into this
        # section since in v2, anchors need to be inside paragraphs to prevent
        # any undesired extra spacing above the paragraph (before or after for
        # v1, there is no difference). We also used to use `names` over `ids`
        # which worked for most things; however, some autodocs links seemed to
        # use some id-only targets instead.
        self._build_id_anchors(node)

        self.context.append(self.end_tag(node, suffix=''))

    def depart_paragraph(self, node):
        self.body.append(self.context.pop())  # p

    def visit_transition(self, node):
        self.body.append(self.start_tag(
            node, 'hr', suffix=self.nl, empty=True))
        raise nodes.SkipNode

    # ----------------------
    # body elements -- lists
    # ----------------------

    def _apply_leading_list_item_offets(self, node, attribs):
        # Confluence's provided styles remove first-child elements leading
        # margins. This causes some unexpected styling issues when list entries
        # which contain other block elements do not style appropriately. This
        # extensions attempts to maintain compact list item entries; however,
        # for a list which contains non-compact entries (e.g. multiple
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
        for child in node.children:  # list items
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
                    attribs['style'] = f'margin-top: {FCMMO}px;'
            except AttributeError:
                pass

    def visit_bullet_list(self, node):
        # [sphinx-gallery] if a list item is build with sphinx-gallery providing
        # a `horizontal` class type, the extension produces html output in an
        # hlist fashion; replicate this here
        if 'sphx-glr-horizontal' in node.get('classes', []):
            self.visit_hlist(node)
            self._list_context.append('sphx-glr-horizontal')
            return

        attribs = {}
        self._apply_leading_list_item_offets(node, attribs)

        self.body.append(self.start_tag(node, 'ul', suffix=self.nl, **attribs))
        self.context.append(self.end_tag(node))
        self._list_context.append('')

    def depart_bullet_list(self, node):
        if self._list_context[-1] == 'sphx-glr-horizontal':
            self.depart_hlist(node)
            return

        self.body.append(self.context.pop())  # ul
        self._list_context.pop()

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
        if 'enumtype' in node:
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
                self.warn('unknown enumerated list type: ' + node['enumtype'])

        if list_style_type:
            if 'style' not in attribs:
                attribs['style'] = ''
            attribs['style'] += f'list-style-type: {list_style_type};'

        self.body.append(self.start_tag(node, 'ol', suffix=self.nl, **attribs))
        self.context.append(self.end_tag(node))

    def depart_enumerated_list(self, node):
        self.body.append(self.context.pop())  # ol

    def visit_list_item(self, node):
        if self._list_context[-1] == 'sphx-glr-horizontal':
            self.visit_hlistcol(node)
            return

        # apply margin offset if flagged (see _apply_leading_list_item_offets)
        attribs = {}
        try:
            if node.__confluence_list_item_margin:
                attribs['style'] = f'margin-top: {FCMMO}px;'
        except AttributeError:
            pass

        self.body.append(self.start_tag(node, 'li', suffix=self.nl, **attribs))
        self.context.append(self.end_tag(node))

    def depart_list_item(self, node):
        if self._list_context[-1] == 'sphx-glr-horizontal':
            self.depart_hlistcol(node)
            return

        self.body.append(self.context.pop())  # li

    # ---------------------------------
    # body elements -- definition lists
    # ---------------------------------

    def visit_definition_list(self, node):
        # v2 editors do not support dl/dt/dd entries; skip building these
        # tags -- we will try to emulate these lists by utilizing indentation
        # tracking to hint are indenting detected terms
        if self.v2:
            self._indent_level += 1
            return

        self.body.append(self.start_tag(node, 'dl', suffix=self.nl))
        self.context.append(self.end_tag(node))

    def depart_definition_list(self, node):
        if self.v2:
            self._indent_level -= 1
            return

        self.body.append(self.context.pop())  # dl

    def visit_definition_list_item(self, node):
        # When processing a definition list item (an entry), multiple terms may
        # exist for the given entry (e.g. when using a glossary). Before
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
            self.body.append(self.context.pop())  # dt/p

        if self.v2:
            offset = INDENT * self._indent_level
            self.body.append(self.start_tag(node, 'p',
                **{'style': f'margin-left: {offset}px;'}))
            self.context.append(self.end_tag(node))

        self._build_id_anchors(node)

        if not self.v2:
            self.body.append(self.start_tag(node, 'dt'))
            self.context.append(self.end_tag(node))
        self._has_term = True

    def depart_term(self, node):
        # note: Do not pop the context populated from 'visit_term'. The last
        #       entry may need to hold classifier information inside it. Either
        #       next term or a term's definition will pop the context.
        pass

    def visit_classifier(self, node):
        self.body.append(' : ')
        self.body.append(self.start_tag(node, 'em'))
        self.context.append(self.end_tag(node, suffix=''))

    def depart_classifier(self, node):
        self.body.append(self.context.pop())  # em

    def visit_definition(self, node):
        if self._has_term:
            self.body.append(self.context.pop())  # dt/p
            self._has_term = False

        if self.v2:
            self._indent_level += 1
        else:
            self.body.append(self.start_tag(node, 'dd', suffix=self.nl))
            self.context.append(self.end_tag(node))

    def depart_definition(self, node):
        if self.v2:
            self._indent_level -= 1
        else:
            self.body.append(self.context.pop())  # dd

    def visit_termsep(self, node):
        raise nodes.SkipNode

    # ----------------------------
    # body elements -- field lists
    # ----------------------------

    def visit_field_list(self, node):
        if not self.v2:
            self.body.append(self.start_tag(node, 'table', suffix=self.nl))
            self.context.append(self.end_tag(node))
            self.body.append(self.start_tag(node, 'tbody', suffix=self.nl))
            self.context.append(self.end_tag(node))

    def depart_field_list(self, node):
        if not self.v2:
            self.body.append(self.context.pop())  # tbody
            self.body.append(self.context.pop())  # table

    def visit_field(self, node):
        if not self.v2:
            self.body.append(self.start_tag(node, 'tr', suffix=self.nl))
            self.context.append(self.end_tag(node))

    def depart_field(self, node):
        if not self.v2:
            self.body.append(self.context.pop())  # tr

    def visit_field_name(self, node):
        if not self.v2:
            self.body.append(self.start_tag(node, 'td',
                **{'style': 'border: none'}))
            self.context.append(self.end_tag(node))

        self.body.append(self.start_tag(node, 'strong'))
        self.context.append(self.end_tag(node, suffix=''))

    def depart_field_name(self, node):
        self.body.append(':')
        self.body.append(self.context.pop())  # strong

        if not self.v2:
            self.body.append(self.context.pop())  # td

    def visit_field_body(self, node):
        if not self.v2:
            self.body.append(self.start_tag(node, 'td',
                **{'style': 'border: none'}))
            self.context.append(self.end_tag(node))

    def depart_field_body(self, node):
        if not self.v2:
            self.body.append(self.context.pop())  # td

    # -----------------------------
    # body elements -- option lists
    # -----------------------------

    def visit_option_list(self, node):
        if not self.v2:
            self.body.append(self.start_tag(node, 'table', suffix=self.nl))
            self.context.append(self.end_tag(node))
            self.body.append(self.start_tag(node, 'tbody', suffix=self.nl))
            self.context.append(self.end_tag(node))

    def depart_option_list(self, node):
        if not self.v2:
            self.body.append(self.context.pop())  # tbody
            self.body.append(self.context.pop())  # table

    def visit_option_list_item(self, node):
        if self.v2:
            self.body.append(self.start_tag(node, 'ac:layout'))
            self.context.append(self.end_tag(node))

            self.body.append(self.start_tag(node, 'ac:layout-section',
                **{
                    'ac:type': 'two_left_sidebar',
                    'ac:breakout-mode': 'default',
                }))
            self.context.append(self.end_tag(node))
        else:
            self.body.append(self.start_tag(node, 'tr', suffix=self.nl))
            self.context.append(self.end_tag(node))

    def depart_option_list_item(self, node):
        if self.v2:
            self.body.append(self.context.pop())  # ac:layout-section
            self.body.append(self.context.pop())  # ac:layout
        else:
            self.body.append(self.context.pop())  # tr

    def visit_option_group(self, node):
        self._first_option = True

        if self.v2:
            self.body.append(self.start_tag(node, 'ac:layout-cell'))
            self.context.append(self.end_tag(node))
        else:
            self.body.append(self.start_tag(node, 'td',
                **{'style': 'border: none'}))
            self.context.append(self.end_tag(node))
            self.body.append(self.start_tag(node, 'code'))
            self.context.append(self.end_tag(node, suffix=''))

    def depart_option_group(self, node):
        if self.v2:
            self.body.append(self.context.pop())  # ac:layout-cell
        else:
            self.body.append(self.context.pop())  # code
            self.body.append(self.context.pop())  # td

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
        self.body.append(self.start_tag(node, 'em'))
        self.context.append(self.end_tag(node, suffix=''))

    def depart_option_argument(self, node):
        self.body.append(self.context.pop())  # em

    def visit_description(self, node):
        if self.v2:
            self.body.append(self.start_tag(node, 'ac:layout-cell'))
        else:
            self.body.append(self.start_tag(node, 'td',
                **{'style': 'border: none'}))

        self.context.append(self.end_tag(node))

    def depart_description(self, node):
        self.body.append(self.context.pop())  # td.ac:layout-cell

    # -------------------------------
    # body elements -- literal blocks
    # -------------------------------

    def visit_literal_block(self, node):
        lang = None
        lang_map = LITERAL2LANG_MAP_V2 if self.v2 else LITERAL2LANG_MAP_V1
        fb_map = LITERAL2LANG_FBMAP_V2 if self.v2 else LITERAL2LANG_FBMAP_V1

        # non-raw literal
        if node.rawsource != node.astext():
            # include marked with a literal flag; ignore parsed literals for
            # v2 editor since they are no longer supported
            if 'source' in node or self.v2:
                lang = 'none'
            # parsed literal
            else:
                self._literal = True
                self.body.append(self.start_tag(node, 'div', suffix=self.nl,
                    **{'class': 'panel pdl'}))
                self.context.append(self.end_tag(node))
                self.body.append(self.start_tag(node, 'pre',
                    **{'class': 'panelContent'}))
                self.context.append(self.end_tag(node))
                self.body.append(self.start_tag(node, 'code'))
                self.context.append(self.end_tag(node))
                return

        if not lang:
            lang = node.get('language', self._highlight).lower()

        translated_lang = None
        if self.builder.lang_transform:
            translated_lang = self.builder.lang_transform(lang)

        if translated_lang:
            lang = translated_lang
        elif lang in lang_map:
            lang = lang_map[lang]
        else:
            if lang not in self._tracked_unknown_code_lang:
                self.warn('unsupported code language for confluence: ' + lang,
                    subtype='unsupported_code_lang')
                self._tracked_unknown_code_lang.append(lang)
            lang = fb_map.get(lang, FALLBACK_HIGHLIGHT_STYLE)

        data = self.nl.join(node.astext().splitlines())

        title = node.get('scb-caption', None)
        if title:
            title = self.encode(title)

        if node.get('linenos', False):
            num = 'true'
        elif data.count('\n') >= self._linenothreshold:
            num = 'true'
        else:
            num = 'false'

        firstline = None
        if num == 'true':
            with suppress(KeyError):
                firstline = node.attributes['highlight_args']['linenostart']

        self.body.append(self.start_ac_macro(node, 'code'))
        self.body.append(self.build_ac_param(node, 'language', lang))
        self.body.append(self.build_ac_param(node, 'linenumbers', num))

        theme = self.builder.config.confluence_code_block_theme
        theme = theme.lower() if theme else None
        theme_map = SUPPORTED_CODE_BLOCK_THEMES

        for class_ in node.get('classes', []):
            if class_.startswith('confluence-theme-'):
                theme = class_[len('confluence-theme-'):].lower()
                if theme not in theme_map:
                    self.warn('confluence-theme-* defined an unknown theme: ' +
                        theme)
                break

        theme_id = theme_map.get(theme)
        if theme_id:
            self.body.append(self.build_ac_param(node, 'theme', theme_id))

        if firstline is not None and firstline > 1:
            self.body.append(self.build_ac_param(node, 'firstline', firstline))

        if title:
            self.body.append(self.build_ac_param(node, 'title', title))

        if 'collapse' in node.get('classes', []):
            self.body.append(self.build_ac_param(node, 'collapse', 'true'))

        self.body.append(self.start_ac_plain_text_body_macro(node))
        self.body.append(self.escape_cdata(data))
        self.body.append(self.end_ac_plain_text_body_macro(node))
        self.body.append(self.end_ac_macro(node))

        raise nodes.SkipNode

    def depart_literal_block(self, node):
        self._literal = False

        # note: depart is only invoked for parsed-literals
        self.body.append(self.context.pop())  # code
        self.body.append(self.context.pop())  # pre
        self.body.append(self.context.pop())  # div

    def visit_highlightlang(self, node):
        self._highlight = node.get('lang', DEFAULT_HIGHLIGHT_STYLE)
        self._linenothreshold = node.get('linenothreshold', sys.maxsize)
        raise nodes.SkipNode

    def visit_doctest_block(self, node):
        data = self.nl.join(node.astext().splitlines())

        self.body.append(self.start_ac_macro(node, 'code'))
        self.body.append(self.build_ac_param(
            node, 'language', 'python'))  # python-specific
        self.body.append(self.start_ac_plain_text_body_macro(node))
        self.body.append(self.escape_cdata(data))
        self.body.append(self.end_ac_plain_text_body_macro(node))
        self.body.append(self.end_ac_macro(node))

        raise nodes.SkipNode

    # -----------------------------
    # body elements -- block quotes
    # -----------------------------

    def visit_block_quote(self, node):
        if first(findall(node, nodes.attribution)):
            if self.v2:
                self.body.append(self.start_tag(node, 'blockquote'))
            else:
                # older editor updates no longer render blockquotes as
                # expected; emulate the legacy and v2 editor style
                style = 'margin: 10px 0px 10px 19px;'
                style += 'border-left: 1px solid #ccc;'
                style += 'padding: 10px 20px;'
                style += 'color: #707070;'
                self.body.append(self.start_tag(node, 'div', suffix=self.nl,
                    **{'style': style}))

            self.context.append(self.end_tag(node))
        elif self.v2:
            self._indent_level += 1
        else:
            style = ''

            # Confluence's WYSIWYG, when indenting paragraphs, will produce
            # paragraphs will margin values offset by 30 pixels units. The same
            # indentation is applied here via a style value.
            style += f'margin-left: {INDENT}px;'

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

            next_child = first(findall(node, include_self=False))
            if isinstance(next_child, nodes.block_quote):
                firstchild_margin = False

            if firstchild_margin:
                style += f'padding-top: {FCMMO}px;'

            self.body.append(self.start_tag(node, 'div', suffix=self.nl,
                **{'style': style}))
            self.context.append(self.end_tag(node))

    def depart_block_quote(self, node):
        if first(findall(node, nodes.attribution)) or not self.v2:
            self.body.append(self.context.pop())  # blockquote/div
        else:
            self._indent_level -= 1

    def visit_attribution(self, node):
        # see `visit_block_quote` fallback case
        if not self.v2:
            self.body.append('<br />')
        self.body.append('— ')

    def depart_attribution(self, node):
        pass

    # -----------
    # admonitions
    # -----------

    def _visit_admonition(self, node, atype, title=None, logo=True):
        self.body.append(self.start_ac_macro(node, atype))
        if title:
            self.body.append(self.build_ac_param(node, 'title', title))
        if not logo:
            self.body.append(
                self.build_ac_param(node, 'icon', 'false'))
        self.body.append(self.start_ac_rich_text_body_macro(node))
        self.context.append(self.end_ac_rich_text_body_macro(node) +
            self.end_ac_macro(node))

    def _depart_admonition(self, node):
        self.body.append(self.context.pop())  # macro (or blockquote)

    def _visit_admonition_adf(self, node, atype, title=None, logo=True):
        self.body.append(self.start_adf_extension(node))
        self.context.append(self.end_adf_extension(node))

        self.body.append(self.start_adf_node(node, 'panel'))
        self.context.append(self.end_adf_node(node))

        self.body.append(self.build_adf_attribute(node, 'panel-type', atype))

        self.body.append(self.start_adf_content(node))
        self.context.append(self.end_adf_content(node))

    def _depart_admonition_adf(self, node):
        self.body.append(self.context.pop())  # adf-content
        self.body.append(self.context.pop())  # adf-node
        self.body.append(self.context.pop())  # adf-extension

    def _visit_info(self, node):
        self._visit_admonition(node, 'info')

    def _visit_note(self, node):
        self._visit_admonition(node, 'note')

    def _visit_tip(self, node):
        self._visit_admonition(node, 'tip')

    def _visit_todo_node(self, node):
        if not self.todo_include_todos:
            raise nodes.SkipNode

        if self.v2:
            self._visit_admonition_adf(node, 'note')
            self.body.append(self.start_tag(node, 'h3'))

        if node.get('ids'):
            self._build_anchor(node, node['ids'][0])

        if self.v2:
            self.body.append(SL('Todo'))
            self.body.append(self.end_tag(node))
        else:
            self._visit_admonition(node, 'info', title=SL('Todo'))

    def _visit_warning(self, node):
        self._visit_admonition(node, 'warning')

    def visit_admonition(self, node):
        title_node = first(findall(node, nodes.title))

        if self.v2:
            self._visit_admonition_adf(node, 'note')

            if title_node:
                title = title_node.astext()
                self.body.append(self.start_tag(node, 'h3'))
                self.body.append(title)
                self.body.append(self.end_tag(node))
        else:
            if title_node:
                title = title_node.astext()
                self._visit_admonition(node, 'info', title, logo=False)
            else:
                self._visit_admonition(node, 'info', logo=False)

    def depart_admonition(self, node):
        if self.v2:
            self._depart_admonition_adf(node)
        else:
            self._depart_admonition(node)

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
    visit_todo_node = _visit_todo_node
    depart_todo_node = depart_admonition
    visit_warning = _visit_warning
    depart_warning = _depart_admonition

    # ------
    # tables
    # ------

    def visit_table(self, node):
        title_node = first(findall(node, nodes.title))
        if title_node:
            self.body.append(self.start_tag(node, 'p'))
            self.body.append(self.start_tag(node, 'strong'))
            self.add_fignumber(node)
            self.body.append(self.encode(title_node.astext()))
            self.body.append(self.end_tag(node))
            self.body.append(self.end_tag(node))

        table_classes = node.get('classes', [])
        attribs = {}

        # For v2 editor, if we have given explicit widths for columns in the
        # table (e.g. CSV table), we need to apply a data table width or the
        # editor will ignore the column-specific widths. If widths are
        # detected, apply the default table width observed when using the v2
        # editor.
        if self.v2 and 'colwidths-given' in table_classes:
            attribs['data-table-width'] = CONFLUENCE_DEFAULT_V2_TABLE_WIDTH

        # [sphinxcontrib-needs]
        # force needs tables to a maximum width
        # (do not for v2 editor, as it will already use the page's width)
        needs_styles = ['need', 'NEEDS_TABLE', 'NEEDS_DATATABLES']
        node.__needs_table = any(ns in table_classes for ns in needs_styles)
        if node.__needs_table and not self.v2:
            attribs['style'] = 'width: 100%;'

        self.body.append(self.start_tag(
            node, 'table', suffix=self.nl, **attribs))
        self.context.append(self.end_tag(node))

        # track the thead context
        #
        # When writing a table cell (visit_entry), it needs to be known if the
        # cell is in the header (th) or is a data cell (td). A "thead context"
        # keeps track of whether or not an cell/entry being written is of the
        # proper type. A context list is needed to support nested tables.
        self._thead_context.append(False)

    def depart_table(self, node):
        self.body.append(self.context.pop())  # table
        self._thead_context.pop()

        # [sphinxcontrib-needs]
        # inject a newline on v1 editor for needs tables, to help space out
        # different requirements; note v2 editor tables already force some
        # level of spacing
        if node.__needs_table and not self.v2:
            self.body.append(self.start_tag(
                node, 'br', suffix=self.nl, empty=True))

    def visit_tgroup(self, node):
        node.stubs = []

        apply_colwidths = False
        table_classes = node.parent.get('classes', [])

        # if column widths are explicitly given, apply specific column widths
        if 'colwidths-given' in table_classes:
            apply_colwidths = True

        # [sphinxcontrib-needs]
        # force applying column widths if this is a needs table
        if node.parent.__needs_table:
            apply_colwidths = True

        if apply_colwidths:
            has_colspec = False
            for colspec in findall(node, nodes.colspec):
                if not has_colspec:
                    self.body.append(self.start_tag(node, 'colgroup'))
                    has_colspec = True

                # apply a width percentage based on the configured colwidth
                # value; however, if this is a v2 editor and it is detected
                # that the configured width is set to 100%, do not apply any
                # styling, v2 tables are already 100% by default, and
                # configuring it explicitly may break the editor's page
                # width configuration
                attribs = {}
                colwidth = colspec['colwidth']
                if colwidth != 100 or not self.v2:
                    attribs['style'] = f'width: {colwidth}%'

                self.body.append(self.start_tag(
                    node, 'col', empty=True, **attribs))

            if has_colspec:
                self.body.append(self.end_tag(node))

    def depart_tgroup(self, node):
        pass

    def visit_thead(self, node):
        self._thead_context.append(True)  # thead context (see visit_table)
        self.body.append(self.start_tag(node, 'thead', suffix=self.nl))
        self.context.append(self.end_tag(node))

    def depart_thead(self, node):
        self.body.append(self.context.pop())  # thead context (see visit_table)
        self._thead_context.pop()

    def visit_tbody(self, node):
        self.body.append(self.start_tag(node, 'tbody', suffix=self.nl))
        self.context.append(self.end_tag(node))

    def depart_tbody(self, node):
        self.body.append(self.context.pop())  # tbody

    def visit_row(self, node):
        node.column = 0
        self.body.append(self.start_tag(node, 'tr', suffix=self.nl))
        self.context.append(self.end_tag(node))

    def depart_row(self, node):
        self.body.append(self.context.pop())  # tr

    def visit_entry(self, node):
        row = node.parent
        tgroup = row.parent.parent
        table = tgroup.parent

        if self._thead_context[-1]:
            target_tag = 'th'
        elif node.parent.parent.parent.stubs[row.column]:
            target_tag = 'th'
        else:
            target_tag = 'td'

        row.column += 1

        attribs = {}
        if 'morecols' in node:
            attribs['colspan'] = node['morecols'] + 1
        if 'morerows' in node:
            attribs['rowspan'] = node['morerows'] + 1

        # [sphinxcontrib-needs]
        # if this is entry in a needs table, apply various styling
        if table.__needs_table:
            if 'head' in row.get('classes', []):
                target_tag = 'th'
            if 'head_center' in node.get('classes', []):
                attribs['style'] = 'text-align: center;'
            if 'head_right' in node.get('classes', []):
                attribs['style'] = 'text-align: right;'
            if 'footer_right' in node.get('classes', []):
                attribs['style'] = 'text-align: right;'

        self.body.append(self.start_tag(node, target_tag, **attribs))
        self.context.append(self.end_tag(node))

        # [sphinxcontrib-needs]
        # for meta-like fields, attempt to make the font smaller
        node.__needs_table_extra = False
        entry_classes = node.get('classes', [])
        sup_styles = ['meta', 'head_right', 'head_left',
                      'footer_left', 'footer_right']
        if table.__needs_table:
            if any(ns in entry_classes for ns in sup_styles):
                self.body.append(self.start_tag(node, 'sup'))
                self.context.append(self.end_tag(node, suffix=''))
                node.__needs_table_extra = True

    def depart_entry(self, node):
        if node.__needs_table_extra:
            self.body.append(self.context.pop())  # sup

        self.body.append(self.context.pop())  # td/th

    def visit_tabular_col_spec(self, node):
        raise nodes.SkipNode

    def visit_colspec(self, node):
        self.colspecs.append(node)
        node.parent.stubs.append(node.attributes.get('stub'))

    def depart_colspec(self, node):
        pass

    # -------------------
    # references - common
    # -------------------

    def visit_reference(self, node):
        # ignore reference if it is wrapped by another reference; observed
        # when a local table of contents contains a section name which is a
        # reference to another document
        if self._reference_context:
            self.verbose('skipping nested reference container')
            return

        if 'iscurrent' in node:
            pass
        elif 'top-reference' in node:
            self._visit_reference_top(node)
        elif 'refuri' in node:
            # If a document provides an anchor target directly in the reference,
            # attempt to extract the anchor value and pass it into the internal
            # reference processing instead.
            if node['refuri'].startswith('#'):
                node['refid'] = node['refuri'][1:]
                del node['refuri']
                self._visit_reference_intern_id(node)
            elif 'refdocname' in node or node.get('internal'):
                self._visit_reference_intern_uri(node)
            else:
                self._visit_reference_extern(node)
        elif 'refid' in node:
            self._visit_reference_intern_id(node)

    def _visit_reference_extern(self, node):
        uri = node['refuri']
        uri = self.encode(uri)

        attribs = {}
        attribs['href'] = uri

        next_child = first(findall(node, include_self=False))
        if isinstance(next_child, nodes.inline):
            if 'viewcode-link' in next_child.get('classes', []):
                if self.v2:
                    self.body.append(' ')
                else:
                    self.body.append(self.start_tag(node, 'div',
                        **{'style': 'float: right'}))
                    self._reference_context.append(self.end_tag(node))

        if 'reftitle' in node:
            title = node['reftitle']
            title = self.encode(title)
            attribs['title'] = title

        self.body.append(self.start_tag(node, 'a', **attribs))
        self._reference_context.append(self.end_tag(node, suffix=''))

    def _visit_reference_intern_id(self, node):
        raw_anchor = ''.join(node['refid'].split())

        if self.builder.name == 'singleconfluence':
            docname = self._docnames[-1]
        else:
            docname = self.docname

        anchor_value = self._resolve_anchor(docname, raw_anchor)

        is_citation = ('ids' in node and node['ids']
            and 'internal' in node and node['internal'])

        if anchor_value and (is_citation or self._topic) and 'ids' in node:
            for id_ in node['ids']:
                self._build_anchor(node, id_)

        if is_citation:
            self.body.append(self.start_tag(node, 'sup'))
            self._reference_context.append(self.end_tag(node, suffix=''))

        if anchor_value:
            if self.v2:
                attribs = {
                    'href': f'#{anchor_value}',
                }

                self.body.append(self.start_tag(node, 'a', **attribs))
                self._reference_context.append(self.end_tag(node, suffix=''))
            else:
                # build link to internal anchor (on the same page)
                #  Note: plain-text-link body cannot have inline markup; content
                #        will be added into body already and skip-children
                #        should be invoked for this use case.
                self.body.append(self.start_ac_link(node, anchor_value))
                self._reference_context.append(self.end_ac_link(node))

                self.body.append(self.start_ac_link_body(node))
                self._reference_context.append(self.end_ac_link_body(node))

    def _visit_reference_intern_uri(self, node):
        doc_path = Path(node['refuri'].split('#')[0])
        doc_raw_id = Path(self.docparent) / doc_path.parent / doc_path.stem
        docname = posixpath.normpath(doc_raw_id.as_posix())
        doctitle = self.state.title(docname)
        if not doctitle:
            self.warn('unable to build link to document due to '
                f'missing title (in {self.docname}): {docname}')

            # build a broken link
            self.body.append(self.start_tag(node, 'a', **{'href': '#'}))
            self._reference_context.append(self.end_tag(node, suffix=''))
            return

        raw_anchor = intern_uri_anchor_value(docname, node['refuri'])
        anchor_value = self._resolve_anchor(docname, raw_anchor)

        navnode = getattr(node, 'cbe_navnode', False)

        if navnode:
            if self.v2:
                # closed off header row? close out this layout and
                # build a new one
                if self._v2_header_added:
                    self.body.append(self.context.pop())  # ac:layout-section
                    self.body.append(self.context.pop())  # ac:layout

                    self.body.append(self.start_tag(node, 'ac:layout'))
                    self.context.append(self.end_tag(node))

                    self.body.append(self.start_tag(node, 'ac:layout-section',
                        **{
                            'ac:type': 'two_equal',
                            'ac:breakout-mode': 'default',
                        }))
                    self.context.append(self.end_tag(node))

                    self._v2_header_added = False

                self.body.append(self.start_tag(node, 'ac:layout-cell'))
                self._reference_context.append(self.end_tag(node))
                self._v2_marginals_partial = not node.cbe_navnode_next

                if node.cbe_navnode_next:
                    self.body.append(self.start_tag(node, 'p',
                        **{'style': 'text-align: right'}))
                    self._reference_context.append(self.end_tag(node))
            else:
                if self._needs_navnode_spacing:
                    self.body.append(self.start_tag(node, 'p', empty=True,
                        **{'style': 'clear: both'}))
                    self._needs_navnode_spacing = False

                float_ = 'right' if node.cbe_navnode_next else 'left'
                self.body.append(self.start_tag(node, 'div',
                    **{'style': 'float: ' + float_ + ';'}))
                self._reference_context.append(self.end_tag(node))

        # build link to internal anchor (on another page)
        #  Note: plain-text-link body cannot have inline markup; add the node
        #        contents into body and skip processing the rest of this node.
        doctitle = self.encode(doctitle)
        self.body.append(self.start_ac_link(node, anchor_value))
        self._reference_context.append(self.end_ac_link(node))

        self.body.append(self.start_tag(node, 'ri:page',
            suffix=self.nl, empty=True, **{'ri:content-title': doctitle}))

        self.body.append(self.start_ac_link_body(node))
        self._reference_context.append(self.end_ac_link_body(node))

        # style navigation references with an aui-button look
        if navnode:
            self.body.append(self.start_tag(
                node, 'span', **{'class': 'aui-button'}))
            self._reference_context.append(self.end_tag(node, suffix=''))

        if self.add_secnumbers and node.get('secnumber'):
            self.body.append('.'.join(map(str, node['secnumber'])) +
                self.secnumber_suffix)

    def _visit_reference_top(self, node):
        self.body.append(self.start_tag(node, 'a', **{'href': '#top'}))
        self._reference_context.append(self.end_tag(node, suffix=''))

    def depart_reference(self, node):
        for element in reversed(self._reference_context):
            self.body.append(element)
        self._reference_context = []

    def visit_target(self, node):
        # for any target identifiers that do not have a reference uri (e.g.
        # sections which will have automatically created targets), we will
        # build an anchor link for them; example cases include documentation
        # which generate a custom anchor link inside a paragraph
        if 'ids' in node and 'refuri' not in node:
            self._build_id_anchors(node)
            self.body.append(self.encode(node.astext()))

        raise nodes.SkipNode

    def _resolve_anchor(self, docname, raw_anchor):
        if not raw_anchor:
            return None

        anchorname = f'{docname}/#{raw_anchor}'

        # check if this target is reachable without an anchor; if so, use the
        # identifier value instead
        target = self.state.target(anchorname)

        # if a target could not be found, check if it was registered from
        # a "global name"
        if not target:
            alt_anchorname = f'/#{raw_anchor}'
            target = self.state.target(alt_anchorname)

        if target:
            self.verbose(
                f'found target for anchor ({docname}): '
                f'{anchorname} -> {target}'  # noqa: COM812
            )
            anchor_value = target
            anchor_value = self.encode(anchor_value)
        else:
            self.verbose(f'no target for anchor ({docname}): {anchorname}')
            anchor_value = raw_anchor

        return anchor_value

    # --------------------------------
    # references - footnotes/citations
    # --------------------------------

    def visit_footnote(self, node):
        label_node = node.next_node()
        if not isinstance(label_node, nodes.label):
            raise nodes.SkipNode

        # if the first foonote/citation, start building a table; except for
        # the v2 editor, which we do not add tables since they cannot be
        # styled
        if not self._building_footnotes:
            if self.v2:
                self._indent_level += 1

                self.body.append(self.start_tag(
                    node, 'hr', suffix=self.nl, empty=True))
            else:
                self.body.append(self.start_tag(node, 'table', suffix=self.nl))
                self.context.append(self.end_tag(node))
                self.body.append(self.start_tag(node, 'tbody', suffix=self.nl,
                    **{'style': 'border: none'}))
                self.context.append(self.end_tag(node))
            self._building_footnotes = True

        label_text = '[' + label_node.astext() + ']'

        if not self.v2:
            self.body.append(self.start_tag(node, 'tr', suffix=self.nl))
            self.context.append(self.end_tag(node))

            self.body.append(self.start_tag(node, 'td',
                **{'style': 'border: none'}))

        # footnote anchor
        self._build_anchor(node, node['ids'][0])

        # footnote label and back reference(s)
        if 'backrefs' not in node or not node['backrefs']:
            label_text = self.encode(label_text)
            self.body.append(label_text)
        elif len(node['backrefs']) > 1:
            label_text = self.encode(label_text)
            self.body.append(label_text)

            if self.v2:
                self.body.append(' ')
            else:
                self.body.append(self.start_tag(node, 'div'))
            self.body.append(self.start_tag(node, 'em'))
            self.body.append('(')

            for idx, backref in enumerate(node['backrefs']):
                if idx != 0:
                    self.body.append(', ')

                if self.v2:
                    attribs = {
                        'href': f'#{backref}',
                    }

                    self.body.append(self.start_tag(node, 'a', **attribs))
                    self.body.append(self.escape_cdata(str(idx + 1)))
                    self.body.append(self.end_tag(node, suffix=''))
                else:
                    self.body.append(self.start_ac_link(node, backref))
                    self.body.append(
                        self.start_ac_plain_text_link_body_macro(node))
                    self.body.append(self.escape_cdata(str(idx + 1)))
                    self.body.append(self.end_ac_plain_text_link_body_macro(node))
                    self.body.append(self.end_ac_link(node))
            self.body.append(')')
            self.body.append(self.end_tag(node, suffix=''))  # em
            if not self.v2:
                self.body.append(self.end_tag(node))  # div
        elif self.v2:
            attribs = {
                'href': '#' + node['backrefs'][0],
            }

            self.body.append(self.start_tag(node, 'a', **attribs))
            self.body.append(self.escape_cdata(label_text))
            self.body.append(self.end_tag(node, suffix=''))
        else:
            self.body.append(self.start_ac_link(node, node['backrefs'][0]))
            self.body.append(self.start_ac_plain_text_link_body_macro(node))
            self.body.append(self.escape_cdata(label_text))
            self.body.append(self.end_ac_plain_text_link_body_macro(node))
            self.body.append(self.end_ac_link(node))

        if not self.v2:
            self.body.append(self.end_tag(node))

            self.body.append(self.start_tag(node, 'td',
                **{'style': 'border: none'}))
            self.context.append(self.end_tag(node))

    def depart_footnote(self, node):
        if not self.v2:
            self.body.append(self.context.pop())  # td
            self.body.append(self.context.pop())  # tr

        # if next entry is not another footnote or citation, close off the table
        next_sibling = first(findall(node,
            include_self=False, descend=False, siblings=True))
        if not isinstance(next_sibling, (nodes.citation, nodes.footnote)):
            if self.v2:
                self._indent_level -= 1
                self.body.append(self.start_tag(
                    node, 'hr', suffix=self.nl, empty=True))
            else:
                self.body.append(self.context.pop())  # tbody
                self.body.append(self.context.pop())  # table
            self._building_footnotes = False

    def visit_footnote_reference(self, node):
        text = f"[{node.astext()}]"

        # build an anchor for back reference
        self._build_anchor(node, node['ids'][0])

        # link to anchor
        target_anchor = ''.join(node['refid'].split())

        self.body.append(self.start_tag(node, 'sup'))
        self.body.append(self.start_ac_link(node, target_anchor))
        self.body.append(self.start_ac_plain_text_link_body_macro(node))
        self.body.append(self.escape_cdata(text))
        self.body.append(self.end_ac_plain_text_link_body_macro(node))
        self.body.append(self.end_ac_link(node))
        self.body.append(self.end_tag(node, suffix=''))  # sup
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
        self.body.append(self.start_tag(node, 'em'))
        self.context.append(self.end_tag(node, suffix=''))

    def depart_emphasis(self, node):
        self.body.append(self.context.pop())  # em

    def visit_literal(self, node):
        self.body.append(self.start_tag(node, 'code'))
        self.context.append(self.end_tag(node, suffix=''))

    def depart_literal(self, node):
        self.body.append(self.context.pop())  # code

    def visit_strong(self, node):
        self.body.append(self.start_tag(node, 'strong'))
        self.context.append(self.end_tag(node, suffix=''))

    def depart_strong(self, node):
        self.body.append(self.context.pop())  # strong

    def visit_subscript(self, node):
        self.body.append(self.start_tag(node, 'sub'))
        self.context.append(self.end_tag(node, suffix=''))

    def depart_subscript(self, node):
        self.body.append(self.context.pop())  # sub

    def visit_superscript(self, node):
        self.body.append(self.start_tag(node, 'sup'))
        self.context.append(self.end_tag(node, suffix=''))

    def depart_superscript(self, node):
        self.body.append(self.context.pop())  # sup

    def visit_inline(self, node):
        has_added = False

        classes = node.get('classes', [])
        if classes in [['guilabel']]:
            self.body.append(self.start_tag(node, 'em'))
            has_added = True
        elif classes in [['accelerator']]:
            self.body.append(self.start_tag(node, 'u'))
            has_added = True
        elif classes in [['strike']]:
            self.body.append(self.start_tag(node, 's'))
            has_added = True
        # [sphinx-design]
        # badges
        elif 'sd-badge' in classes:
            color = None
            subtle = False

            if 'sd-bg-danger' in classes or 'sd-outline-danger' in classes:
                color = 'red'
                subtle = 'sd-outline-red' in classes
            elif 'sd-bg-success' in classes or 'sd-outline-success' in classes:
                color = 'green'
                subtle = 'sd-outline-success' in classes
            elif 'sd-bg-warning' in classes or 'sd-outline-warning' in classes:
                color = 'yellow'
                subtle = 'sd-outline-warning' in classes
            elif ('sd-bg-primary' in classes or
                    'sd-outline-primary' in classes or
                    'sd-bg-info' in classes or
                    'sd-outline-info' in classes):
                color = 'blue'
                subtle = ('sd-outline-primary' in classes or
                    'sd-outline-info' in classes)
            elif ('sd-bg-dark' not in classes and
                    'sd-bg-secondary' not in classes):
                subtle = True

            self.body.append(self.start_ac_macro(node, 'status'))
            if color:
                self.body.append(self.build_ac_param(node, 'colour', color))
            if subtle:
                self.body.append(self.build_ac_param(node, 'subtle', 'true'))
            self.body.append(self.build_ac_param(node, 'title', node.astext()))
            self.body.append(self.end_ac_macro(node))
            raise nodes.SkipNode
        # [sphinxcontrib-needs]
        # ignore collapse buttons, since they will not work in Confluence
        elif 'needs_collapse' in classes:
            raise nodes.SkipNode
        # [sphinxcontrib-needs]
        # strong text any title content
        elif 'needs_title' in classes:
            self.body.append(self.start_tag(node, 'strong'))
            has_added = True
        elif isinstance(node.parent, addnodes.desc_parameter):
            # check if an identifier in signature
            if classes in [['n']]:
                self.body.append(self.start_tag(node, 'em'))
                has_added = True

        if has_added:
            self.context.append(self.end_tag(node, suffix=''))
        else:
            # ignoring; no special handling of other inline entries
            self.context.append('')

    def depart_inline(self, node):
        self.body.append(self.context.pop())

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
        # skip any already-processed caption nodes
        if self.v2:
            with suppress(AttributeError):
                if node.__skip_caption:
                    raise nodes.SkipNode

        # if a caption for a literal block, pass the caption data to it can be
        # rendered in the macro's title field
        next_sibling = first(findall(node,
            include_self=False, descend=False, siblings=True))
        if isinstance(next_sibling, nodes.literal_block):
            # anything that is not a parsed literals
            if next_sibling.rawsource == next_sibling.astext() or \
                    'source' in next_sibling:
                next_sibling['scb-caption'] = \
                    self.build_secnumber(node) + \
                    self.build_fignumber(node.parent) + \
                    node.astext()
                raise nodes.SkipNode

        attribs = {}
        attribs['style'] = 'clear: both;'
        self._figure_context.append('')

        alignment = self._fetch_alignment(node)
        if alignment and alignment != 'left':
            attribs['style'] += f'text-align: {alignment};'

        self.body.append(self.start_tag(node, 'p', **attribs))
        self.add_fignumber(node.parent)
        self.context.append(self.end_tag(node))

    def depart_caption(self, node):
        self.body.append(self.context.pop())  # p

    def visit_figure(self, node):
        self.body.append(self.start_tag(node, 'p'))
        self.context.append(self.end_tag(node))

    def depart_figure(self, node):
        self.body.append(self.context.pop())  # p

        # force clear from a floating confluence image if not handled in caption
        if self._figure_context:
            self._figure_context.pop()
        else:
            self.body.append('<div style="clear: both"> </div>\n')

    def _visit_image(self, node, opts):
        node.__confluence_wrapped_img = False

        dochost = opts['dochost']
        height = opts['height']
        hu = opts['hu']
        width = opts['width']
        wu = opts['wu']

        # offset vertical image to align with paragraph
        if not self.v2 and node.get('from_math') and node.get('math_depth'):
            math_depth = node['math_depth']
            offset = -1 * math_depth
            self.body.append(self.start_tag(node, 'span',
                **{'style': f'vertical-align: {offset}px'}))
            self.context.append(self.end_tag(node))

        node.math_number = None
        if node.get('from_math') and node.get('number'):
            if self.builder.config.math_numfig and self.builder.config.numfig:
                figtype = 'displaymath'
                if self.builder.name == 'singleconfluence':
                    key = f'{self._docnames[-1]}/{figtype}'
                else:
                    key = figtype

                id_ = node['ids'][0]
                number = self.builder.fignumbers.get(key, {}).get(id_, ())
                node.math_number = '.'.join(map(str, number))
            else:
                node.math_number = node['number']

        if not self.v2 and node.math_number:
            self.body.append(self.start_tag(node, 'div',
                **{'style': 'float: right'}))
            self.body.append(f'({node.math_number})')
            self.body.append(self.end_tag(node))

        attribs = {}

        alignment = self._fetch_alignment(node)
        if alignment:
            attribs['ac:align'] = alignment
            if alignment == 'right':
                attribs['ac:style'] = 'float: right;'
        elif self.v2:
            # ideally, images will be inlined but recent v2 editor will
            # restrict sizing to the line; restrict the feature using a
            # configuration option for now
            if self.builder.config.confluence_adv_inlined_images:
                attribs['ac:inline'] = 'true'

        if 'alt' in node:
            alt = node['alt']
            alt = self.encode(alt)
            attribs['ac:alt'] = alt

        # if this in an internal (attached image) and a percentage is applied,
        # these length cannot be applied to the ac:width/height fields or a
        # macro render error can occur; instead, wrap the image around
        if opts['key'] and (hu == '%' or wu == '%'):
            style = 'display: inline-block;'

            if hu == '%':
                style += f'height: {height}%;'
                height = None
                hu = None

            if wu == '%':
                style += f'width: {width}%;'
                width = None
                wu = None

            self.body.append(self.start_tag(node, 'div', **{'style': style}))
            self.context.append(self.end_tag(node))
            node.__confluence_wrapped_img = True

        # apply width/height fields on the image macro
        if height:
            attribs['ac:height'] = height
        if width:
            attribs['ac:width'] = width

        # if this node has a math number assigned to it, build an anchor so
        # that we can link to this image
        if node.math_number:
            if self.v2:
                self.body.append(self.start_tag(node, 'ac:layout'))
                self.context.append(self.end_tag(node))

                self.body.append(self.start_tag(node, 'ac:layout-section',
                    **{
                        'ac:type': 'three_with_sidebars',
                        'ac:breakout-mode': 'default',
                    }))
                self.context.append(self.end_tag(node))

                self.body.append(self.start_tag(node, 'ac:layout-cell'))

            self._build_id_anchors(node)

            if self.v2:
                self.body.append(self.end_tag(node))

                self.body.append(self.start_tag(node, 'ac:layout-cell'))
                self.context.append(self.end_tag(node))

        if not opts['key']:
            # an external or embedded image
            #
            # Note: it would be rare that embedded images will be detected at
            #       this stage as Sphinx's post-transform processor would
            #       translate these images into embedded images. Nonetheless an
            #       embedded image is still stacked into Confluence image
            #       entity (although, currently, some (if not all) Confluence
            #       versions do not consider embedded images as valid URI values
            #       so users might see a "broken images" block).
            uri = self.encode(node['uri'])
            self.body.append(self.start_ac_image(node, **attribs))
            self.body.append(self.start_tag(node, 'ri:url',
                suffix=self.nl, empty=True, **{'ri:value': uri}))
        else:
            hosted_doctitle = self.state.title(dochost, dochost)
            hosted_doctitle = self.encode(hosted_doctitle)

            self.body.append(self.start_ac_image(node, **attribs))
            self.body.append(self.start_ri_attachment(node, opts['key']))
            if dochost != self.docname:
                self.body.append(self.start_tag(node, 'ri:page', empty=True,
                   **{'ri:content-title': hosted_doctitle}))
            self.body.append(self.end_ri_attachment(node))

        if self.v2:
            next_sibling = first(findall(node,
                include_self=False, descend=False, siblings=True))
            if isinstance(next_sibling, nodes.caption):
                self.body.append(self.start_tag(node, 'ac:caption'))
                next_sibling.__skip_caption = True
                for child in next_sibling.children:
                    child.walkabout(self)
                self.body.append(self.end_tag(node))

        self.body.append(self.end_ac_image(node))

    def depart_image(self, node):
        if node.__confluence_wrapped_img:
            self.body.append(self.context.pop())  # (inlined) div

        if not self.v2 and node.get('from_math') and node.get('math_depth'):
            self.body.append(self.context.pop())  # span

        if self.v2 and node.math_number:
            self.body.append(self.context.pop())  # layout-cell
            self.body.append(self.start_tag(node, 'ac:layout-cell'))

            self.body.append(self.start_tag(node, 'p',
                **{'style': 'text-align: right'}))
            self.body.append(f'({node.math_number})')
            self.body.append(self.end_tag(node))

            self.body.append(self.end_tag(node))  # layout-cell
            self.body.append(self.context.pop())  # ac:layout-section
            self.body.append(self.context.pop())  # ac:layout

    def visit_legend(self, node):
        attribs = {}
        alignment = self._fetch_alignment(node)
        if alignment and alignment != 'left':
            attribs['style'] = f'text-align: {alignment};'

        self.body.append(self.start_tag(node, 'div', **attribs))
        self.context.append(self.end_tag(node))

    def depart_legend(self, node):
        self.body.append(self.context.pop())  # div

    # ------------------
    # sphinx -- download
    # ------------------

    def visit_download_reference(self, node):
        reftarget = node['reftarget']
        uri = self.encode(reftarget)

        if uri.find('://') != -1:
            self.body.append(self.start_tag(node, 'strong'))
            self.context.append(self.end_tag(node, suffix=''))
            self.body.append(self.start_tag(node, 'a', **{'href': uri}))
            self.context.append(self.end_tag(node, suffix=''))
        else:
            asset_docname = None
            if self.builder.name == 'singleconfluence':
                asset_docname = self.docname

            file_key, hosting_docname, _ = \
                self.assets.fetch(node, docname=asset_docname)

            # if this file has not already be processed (injected at a later
            # stage in the sphinx process); try processing it now
            if not file_key:
                if not asset_docname:
                    asset_docname = self.docname

                file_key, hosting_docname, _ = \
                    self.assets.process_file_node(
                        node, asset_docname, standalone=True)

            if not file_key:
                self.warn(f'unable to find download: {reftarget}')
                raise nodes.SkipNode

            hosting_doctitle = self.state.title(hosting_docname)
            hosting_doctitle = self.encode(hosting_doctitle)

            # If the view-file macro is permitted along with it not being an
            # explicitly referenced asset.
            if 'refexplicit' not in node or not node['refexplicit']:
                # a 'view-file' macro takes an attachment tag as a body; build
                # the tags in an interim list
                attachment = []
                attachment.append(self.start_ri_attachment(node, file_key))
                if hosting_docname != self.docname:
                    attachment.append(self.start_tag(node, 'ri:page',
                       empty=True, **{'ri:content-title': hosting_doctitle}))
                attachment.append(self.end_ri_attachment(node))

                self.body.append(self.start_ac_macro(node, 'view-file'))
                self.body.append(self.build_ac_param(
                    node, 'name', ''.join(attachment)))
                self.body.append(self.end_ac_macro(node))
            else:
                self.body.append(self.start_ac_link(node))
                self.body.append(self.start_ri_attachment(node, file_key))
                if hosting_docname != self.docname:
                    self.body.append(self.start_tag(node, 'ri:page',
                       empty=True, **{'ri:content-title': hosting_doctitle}))
                self.body.append(self.end_ri_attachment(node))
                self.body.append(
                    self.start_ac_plain_text_link_body_macro(node))
                self.body.append(self.escape_cdata(node.astext()))
                self.body.append(self.end_ac_plain_text_link_body_macro(node))
                self.body.append(self.end_ac_link(node))

            raise nodes.SkipNode

    def depart_download_reference(self, node):
        self.body.append(self.context.pop())  # a
        self.body.append(self.context.pop())  # strong

    # ---------------
    # sphinx -- hlist
    # ---------------

    def visit_hlist(self, node):
        # cannot make borderless tables in the new editor; instead, we will
        # try to use the layout capability to manage lists -- although we will
        # be limited to a three columns maximum
        if self.v2:
            self.body.append(self.start_tag(node, 'ac:layout'))
            self.context.append(self.end_tag(node))

            self.body.append(self.start_tag(node, 'ac:layout-section',
                **{
                    'ac:type': 'three_equal',
                    'ac:breakout-mode': 'default',
                }))
            self.context.append(self.end_tag(node))

            self._hlist_columns_left = 3
        else:
            self.body.append(self.start_tag(node, 'table', suffix=self.nl))
            self.context.append(self.end_tag(node))
            self.body.append(self.start_tag(node, 'tbody', suffix=self.nl,
                **{'style': 'border: none'}))
            self.context.append(self.end_tag(node))
            self.body.append(self.start_tag(node, 'tr', suffix=self.nl))
            self.context.append(self.end_tag(node))

    def depart_hlist(self, node):
        if self.v2:
            # add empty sections to complete the three column requirement
            for _ in range(self._hlist_columns_left % 3):
                self.body.append(self.start_tag(node, 'ac:layout-cell'))
                self.body.append(self.end_tag(node))

            self.body.append(self.context.pop())  # ac:layout-section
            self.body.append(self.context.pop())  # ac:layout
        else:
            self.body.append(self.context.pop())  # tr
            self.body.append(self.context.pop())  # tbody
            self.body.append(self.context.pop())  # table

    def visit_hlistcol(self, node):
        if self.v2:
            # if not more free columns, create a new section
            if self._hlist_columns_left == 0:
                self.body.append(self.context.pop())  # ac:layout-section
                self.body.append(self.context.pop())  # ac:layout

                self.body.append(self.start_tag(node, 'ac:layout'))
                self.context.append(self.end_tag(node))

                self.body.append(self.start_tag(node, 'ac:layout-section',
                    **{
                        'ac:type': 'three_equal',
                        'ac:breakout-mode': 'default',
                    }))
                self.context.append(self.end_tag(node))

                self._hlist_columns_left = 3

            self.body.append(self.start_tag(node, 'ac:layout-cell'))
            self.context.append(self.end_tag(node))

            self._hlist_columns_left -= 1
        else:
            self.body.append(self.start_tag(node, 'td',
                **{'style': 'border: none'}))
            self.context.append(self.end_tag(node))

    def depart_hlistcol(self, node):
        if self.v2:
            self.body.append(self.context.pop())  # ac:layout-cell
        else:
            self.body.append(self.context.pop())  # td

    # -----------------
    # sphinx -- manpage
    # -----------------

    def visit_manpage(self, node):
        self.visit_emphasis(node)
        if self._manpage_url:
            node['refuri'] = self._manpage_url.format(**node.attributes)
            self.visit_reference(node)

    def depart_manpage(self, node):
        if self._manpage_url:
            self.depart_reference(node)
        self.depart_emphasis(node)

    # -------------------------
    # sphinx -- production list
    # -------------------------

    def visit_productionlist(self, node):
        max_len = max(len(production['tokenname']) for production in node)

        self.body.append(self.start_tag(node, 'pre'))

        for production in node:
            if production['tokenname']:
                formatted_token = production['tokenname'].ljust(max_len)
                formatted_token = self.encode(formatted_token)
                self.body.append(f'{formatted_token} ::=')
                lastname = production['tokenname']
            else:
                prefix = ' ' * len(lastname)
                self.body.append(f'{prefix}    ')
            text = production.astext()
            text = self.encode(text)
            self.body.append(text + self.nl)

        self.body.append(self.end_tag(node))
        raise nodes.SkipNode

    # -----------------
    # sphinx -- toctree
    # -----------------

    def visit_compound(self, node):
        pass

    def depart_compound(self, node):
        pass

    # -----------------
    # sphinx -- domains
    # -----------------

    def visit_desc(self, node):
        if self.v2:
            self.body.append(self.start_ac_macro(node, 'panel'))
            self.body.append(self.build_ac_param(node, 'bgColor', 'unset'))
            self.body.append(self.start_ac_rich_text_body_macro(node))
            self.context.append(self.end_ac_rich_text_body_macro(node) +
                self.end_ac_macro(node))
        else:
            self.body.append(self.start_tag(node, 'dl', suffix=self.nl))
            self.context.append(self.end_tag(node))

    def depart_desc(self, node):
        self.body.append(self.context.pop())  # dl/macro

    def visit_desc_signature(self, node):
        # capture ids which anchors can be generated and placed into the first
        # dt tag (since multiple may be generated)
        self._desc_sig_ids = node.attributes.get('ids', [])

        if not self.v2:
            self.body.append(self.start_tag(node, 'dt'))
            self.context.append(self.end_tag(node))

        if not node.get('is_multiline'):
            self.visit_desc_signature_line(node)

    def depart_desc_signature(self, node):
        if not node.get('is_multiline'):
            self.depart_desc_signature_line(node)

        if not self.v2:
            self.body.append(self.context.pop())  # dt

    def visit_desc_signature_line(self, node):
        if self._desc_sig_ids:
            for id_ in self._desc_sig_ids:
                self._build_anchor(node, id_)

        if self._desc_sig_ids is None:
            self.body.append(self.start_tag(
                node, 'br', suffix=self.nl, empty=True))

        self._desc_sig_ids = None

    def depart_desc_signature_line(self, node):
        pass

    def visit_desc_annotation(self, node):
        self.body.append(self.start_tag(node, 'em'))
        self.context.append(self.end_tag(node, suffix=''))

    def depart_desc_annotation(self, node):
        self.body.append(self.context.pop())  # em

    def visit_desc_addname(self, node):
        if not self.v2:
            self.body.append(self.start_tag(node, 'code'))
            self.context.append(self.end_tag(node, suffix=''))

    def depart_desc_addname(self, node):
        if not self.v2:
            self.body.append(self.context.pop())  # code

    def visit_desc_name(self, node):
        self.body.append(self.start_tag(node, 'strong'))
        self.context.append(self.end_tag(node, suffix=''))
        if not self.v2:
            self.body.append(self.start_tag(node, 'code'))
            self.context.append(self.end_tag(node, suffix=''))

    def depart_desc_name(self, node):
        if not self.v2:
            self.body.append(self.context.pop())  # code
        self.body.append(self.context.pop())  # strong

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

        if not node.get('noemph'):
            self.body.append(self.start_tag(node, 'em'))
            self.context.append(self.end_tag(node, suffix=''))

    def depart_desc_parameter(self, node):
        if not node.get('noemph'):
            self.body.append(self.context.pop())  # em

    def visit_desc_content(self, node):
        if self.v2:
            self.body.append(self.start_ac_macro(node, 'panel'))
            self.body.append(self.build_ac_param(node, 'bgColor', 'unset'))
            self.body.append(self.start_ac_rich_text_body_macro(node))
            self.context.append(self.end_ac_rich_text_body_macro(node) +
                self.end_ac_macro(node))
        else:
            self.body.append(self.start_tag(node, 'dd'))
            self.context.append(self.end_tag(node))

    def depart_desc_content(self, node):
        self.body.append(self.context.pop())  # dd/macro

    # -----------------------
    # sphinx -- miscellaneous
    # -----------------------

    def visit_centered(self, node):
        self.body.append(self.start_tag(node, 'h2',
            **{'style': 'text-align: center'}))
        self.context.append(self.end_tag(node))
        self.body.append(self.start_tag(node, 'strong'))
        self.context.append(self.end_tag(node, suffix=''))

    def depart_centered(self, node):
        self.body.append(self.context.pop())  # strong
        self.body.append(self.context.pop())  # h2

    def visit_rubric(self, node):
        # [sphinx-design]
        # ignore rubrics inside drop downs that have already been used
        sdc = node.parent.get('design_component')
        if sdc == 'dropdown':
            raise nodes.SkipNode

        # styling hints on paragraphs for rubrics do not work in v2;
        # we'll try to emulate a rubric the best we can
        if self.v2:
            self.body.append(self.start_tag(node, 'p'))  # extra for spacing
            self.body.append(self.end_tag(node))
            self.body.append(self.start_tag(node, 'p'))
            self.context.append(self.end_tag(node))
            self.body.append(self.start_tag(node, 'strong'))
            self.context.append(self.end_tag(node))
        else:
            self.body.append(self.start_tag(node, 'p',
                **{'style': 'font-weight: bold; margin-top: 30px'}))
            self.context.append(self.end_tag(node))

    def depart_rubric(self, node):
        if self.v2:
            self.body.append(self.context.pop())  # strong
            self.body.append(self.context.pop())  # p
        else:
            self.body.append(self.context.pop())  # p

    def visit_seealso(self, node):
        self._visit_admonition(node, 'info', admonitionlabels['seealso'])

    depart_seealso = _depart_admonition

    def visit_versionmodified(self, node):
        if node['type'] == 'deprecated' or node['type'] == 'versionchanged':
            self._visit_note(node)
        elif node['type'] == 'versionadded':
            self._visit_info(node)
        else:
            self.warn('unsupported version modification type: ' + node['type'])
            self._visit_info(node)

    depart_versionmodified = _depart_admonition

    # -----------------------------------------
    # sphinx -- extension -- confluence builder
    # -----------------------------------------

    def visit_confluence_excerpt(self, node):
        self.body.append(self.start_ac_macro(node, 'excerpt'))
        for k, v in sorted(PARAMS(node).items()):
            self.body.append(self.build_ac_param(node, k, v))
        self.body.append(self.start_ac_rich_text_body_macro(node))
        self.context.append(self.end_ac_rich_text_body_macro(node) +
            self.end_ac_macro(node, suffix=''))

    def depart_confluence_excerpt(self, node):
        self.body.append(self.context.pop())  # macro

    def visit_confluence_excerpt_include(self, node):
        doclink = node['doclink']
        space_key = None

        # if prefixed with an exclamation, document is refering to another
        # Sphinx document -- find the respective title based off the captured
        # state
        if doclink.startswith('!'):
            docname = doclink[1:]
            doctitle = self.state.title(docname)
            if not doctitle:
                self.warn('unable to build excerpt include to document since '
                    'document is missing or is missing title '
                    f'(in {self.docname}): {docname}')
                raise nodes.SkipNode
        elif ':' in doclink:
            space_key, doctitle = doclink.split(':', 1)
        else:
            doctitle = doclink

        self.body.append(self.start_ac_macro(node, 'excerpt-include'))
        for k, v in sorted(PARAMS(node).items()):
            self.body.append(self.build_ac_param(node, k, v))

        attribs = {
            'ri:content-title': doctitle,
        }
        if space_key:
            attribs['ri:space-key'] = space_key

        doctitle = self.encode(doctitle)
        param_value = self.start_ac_link(node) + \
            self.start_tag(node, 'ri:page', suffix=self.nl,
                empty=True, **attribs) + \
            self.end_ac_link(node)
        self.body.append(self.build_ac_param(node, '', param_value))

        self.body.append(self.end_ac_macro(node))

        raise nodes.SkipNode

    def visit_confluence_expand(self, node):
        self.body.append(self.start_ac_macro(node, 'expand'))
        if 'title' in node:
            self.body.append(
                self.build_ac_param(node, 'title', node['title']))
        self.body.append(self.start_ac_rich_text_body_macro(node))
        self.context.append(self.end_ac_rich_text_body_macro(node) +
            self.end_ac_macro(node))

    def depart_confluence_expand(self, node):
        self.body.append(self.context.pop())  # macro

    def visit_confluence_footer(self, node):
        if self.v2:
            self.body.append(self.start_tag(
                node, 'hr', suffix=self.nl, empty=True))

            self.body.append(self.start_tag(node, 'ac:layout'))
            self.context.append(self.end_tag(node, suffix=''))

            self.body.append(self.start_tag(node, 'ac:layout-section',
                **{
                    'ac:type': 'two_equal',
                    'ac:breakout-mode': 'default',
                }))
            self.context.append(self.end_tag(node))

            # keep track of if the layout section is incomplete (only one
            # cell has been formed), to help hint at injecting additional
            # cells if some header capabilites are not enabled
            self._v2_marginals_partial = False
        else:
            self.body.append(self.start_tag(
                node, 'hr', suffix=self.nl, empty=True,
                **{'style': 'padding-bottom: 10px; margin-top: 30px'}))

    def depart_confluence_footer(self, node):
        if self.v2:
            # inject an empty cell if the footer has not filled
            if self._v2_marginals_partial:
                self.body.append(self.start_tag(node, 'ac:layout-cell'))
                self.body.append(self.end_tag(node))
                self._v2_marginals_partial = False

            self.body.append(self.context.pop())  # ac:layout-section
            self.body.append(self.context.pop())  # ac:layout
        else:
            self.body.append('<div style="clear: both"> </div>\n')

    def visit_confluence_header(self, node):
        if self.v2:
            self.body.append(self.start_tag(node, 'ac:layout'))
            self.context.append(self.end_tag(node, suffix=''))

            self.body.append(self.start_tag(node, 'ac:layout-section',
                **{
                    'ac:type': 'two_equal',
                    'ac:breakout-mode': 'default',
                }))
            self.context.append(self.end_tag(node))

            # keep track of if the layout section is incomplete (only one
            # cell has been formed), to help hint at injecting additional
            # cells if some header capabilites are not enabled
            self._v2_header_added = False
            self._v2_marginals_partial = False

    def depart_confluence_header(self, node):
        if self.v2:
            # inject an empty cell if the header has not filled
            if self._v2_marginals_partial:
                self.body.append(self.start_tag(node, 'ac:layout-cell'))
                self.body.append(self.end_tag(node))
                self._v2_marginals_partial = False

            self._v2_header_added = False

            self.body.append(self.context.pop())  # ac:layout-section
            self.body.append(self.context.pop())  # ac:layout

            self.body.append(self.start_tag(
                node, 'hr', suffix=self.nl, empty=True))
        else:
            self.body.append(self.start_tag(
                node, 'hr', suffix=self.nl, empty=True,
                **{'style':
                    'clear: both; padding-top: 10px; margin-bottom: 30px'}))

    def visit_confluence_html(self, node):
        html_macro = 'html'
        if self.builder.config.confluence_html_macro:
            html_macro = self.builder.config.confluence_html_macro

        html_content = node.rawsource

        self.body.append(self.start_ac_macro(node, html_macro))
        self.body.append(self.start_ac_plain_text_body_macro(node))
        self.body.append(self.escape_cdata(html_content))
        self.body.append(self.end_ac_plain_text_body_macro(node))
        self.body.append(self.end_ac_macro(node))

        raise nodes.SkipNode

    def visit_confluence_newline(self, node):
        self.body.append(self.start_tag(
            node, 'br', suffix=self.nl, empty=True))

        raise nodes.SkipNode

    def visit_confluence_page_generation_notice(self, node):
        if self.v2:
            assert not self._v2_marginals_partial
            self.body.append(self.start_tag(node, 'ac:layout-cell'))

            # v2: does not support font-size assignment; use sup tag
            # to make small
            self.body.append(self.start_tag(node, 'span', **{
                'style': 'color: #707070;',
            }))
            self.body.append(self.start_tag(node, 'sup'))
        else:
            self.body.append(self.start_tag(node, 'div', **{
                'style': 'color: #707070; font-size: 12px;',
            }))

        if self.builder.config.confluence_page_generation_notice is True:
            msg = L('This page has been automatically generated.')
        else:
            msg = L(self.builder.config.confluence_page_generation_notice)

        self.body.append(self.encode(msg))

        if self.v2:
            self.body.append(self.end_tag(node, suffix=''))  # sup
            self.body.append(self.end_tag(node, suffix=''))  # span
            self.body.append(self.end_tag(node))  # ac:layout-cell
            self._v2_header_added = True
            self._v2_marginals_partial = True
        else:
            self.body.append(self.end_tag(node, suffix=''))  # div

            # flag that if any navnodes are created, additional
            # spacing is needed
            self._needs_navnode_spacing = True

        raise nodes.SkipNode

    def visit_confluence_source_link(self, node):
        uri = PARAMS(node)['url']

        docname = self.docname
        docpath = str(self.builder.env.doc2path(docname, base=None))
        suffix = docpath[len(docname):]
        uri = uri.format(page=docname, suffix=suffix, **PARAMS(node))

        source_text = PARAMS(node).get('text', L('Edit Source'))
        uri = self.encode(uri)

        if self.v2:
            # add an empty leading cell, if no content has been provided
            # (since we right-align this content)
            if not self._v2_marginals_partial:
                self.body.append(self.start_tag(node, 'ac:layout-cell'))
                self.body.append(self.end_tag(node))

            self.body.append(self.start_tag(node, 'ac:layout-cell'))
            self.body.append(self.start_tag(node, 'p', **{
                'style': 'text-align: right;',
            }))
            self.body.append(self.start_tag(node, 'a', **{'href': uri}))
            self.body.append(self.encode(source_text))  # visible text
            self.body.append(self.end_tag(node))  # a
            self.body.append(self.end_tag(node))  # p
            self.body.append(self.end_tag(node))  # ac:layout-cell
            self._v2_header_added = True
            self._v2_marginals_partial = False
        else:
            # if a header file is defined, ensure the source link does
            # not overlap with any user-defined header data
            if self.builder.config.confluence_header_file is not None:
                self.body.append('<div style="clear: both"> </div>\n')

            self.body.append(self.start_tag(node, 'div', **{
                'style': 'float: right; padding-bottom: 4px',
            }))
            self.body.append(self.start_tag(node, 'a', **{'href': uri}))
            self.body.append(self.start_tag(node, 'span', **{
                'class': 'aui-icon aui-icon-small '
                         'aui-iconfont-edit-small aui-iconfont-edit-filled',
            }))
            self.body.append(self.encode(source_text))  # span-icon-content
            self.body.append(self.end_tag(node, suffix=''))  # span
            self.body.append(self.encode(source_text))  # visible text
            self.body.append(self.end_tag(node))  # a
            self.body.append(self.end_tag(node))  # div

            # flag that if any navnodes are created, additional
            # spacing is needed
            self._needs_navnode_spacing = True

        raise nodes.SkipNode

    # ------------------------------------------
    # confluence-builder -- enhancements -- card
    # ------------------------------------------

    def visit_confluence_doc_card(self, node):
        # v1 editor does not support cards; contain in a panel to emulate a
        # block feel
        if not self.v2:
            self.body.append(self.start_ac_macro(node, 'panel'))
            self.body.append(self.start_ac_rich_text_body_macro(node))

        doc_path = Path(PARAMS(node)['href'].split('#')[0])
        doc_raw_id = Path(self.docparent) / doc_path.parent / doc_path.stem
        docname = posixpath.normpath(doc_raw_id.as_posix())
        doctitle = self.state.title(docname)
        if doctitle:
            attribs = {}

            if 'data-card-appearance' in PARAMS(node):
                attribs['ac:card-appearance'] = \
                    PARAMS(node)['data-card-appearance']

            if 'data-layout' in PARAMS(node):
                attribs['ac:layout'] = PARAMS(node)['data-layout']

            if 'data-width' in PARAMS(node):
                attribs['ac:width'] = PARAMS(node)['data-width']

            doctitle = self.encode(doctitle)
            self.body.append(self.start_tag(node, 'ac:link', **attribs))
            self.body.append(self.start_tag(node, 'ri:page',
                suffix=self.nl, empty=True, **{'ri:content-title': doctitle}))
            self.body.append(self.end_tag(node, suffix=''))
        else:
            self.warn('unable to build link to document card due to '
                f'missing title (in {self.docname}): {docname}')
            self.body.append(node.astext())

        if not self.v2:
            self.body.append(self.end_ac_rich_text_body_macro(node))
            self.body.append(self.end_ac_macro(node))  # panel

        raise nodes.SkipNode

    def visit_confluence_doc_card_inline(self, node):
        doc_path = Path(node['reftarget'].split('#')[0])
        doc_raw_id = Path(self.docparent) / doc_path.parent / doc_path.stem
        docname = posixpath.normpath(doc_raw_id.as_posix())
        doctitle = self.state.title(docname)
        if doctitle:
            doctitle = self.encode(doctitle)
            self.body.append(self.start_ac_link(node, appearance='inline'))
            self.body.append(self.start_tag(node, 'ri:page',
                suffix=self.nl, empty=True, **{'ri:content-title': doctitle}))
            self.body.append(self.start_ac_link_body(node))
            self.body.append(node.astext())
            self.body.append(self.end_ac_link_body(node))
            self.body.append(self.end_ac_link(node))
        else:
            self.warn('unable to build link to document card due to '
                f'missing title (in {self.docname}): {docname}')
            self.body.append(node.astext())

        raise nodes.SkipNode

    def visit_confluence_link_card(self, node):
        options = dict(PARAMS(node))
        url = self.encode(options.pop('href'))
        options['href'] = url

        # v1 editor does not support cards; contain in a panel to emulate a
        # block feel
        if not self.v2:
            self.body.append(self.start_ac_macro(node, 'panel'))
            self.body.append(self.start_ac_rich_text_body_macro(node))

        self.body.append(self.start_tag(node, 'a', **options))
        self.body.append(url)
        self.body.append(self.end_tag(node, suffix=''))

        if not self.v2:
            self.body.append(self.end_ac_rich_text_body_macro(node))
            self.body.append(self.end_ac_macro(node))  # panel

        raise nodes.SkipNode

    def visit_confluence_link_card_inline(self, node):
        # raw href | give it an inline card appearance
        attribs = {
            'data-card-appearance': 'inline',
            'href': self.encode(PARAMS(node)['href']),
        }

        self.body.append(self.start_tag(node, 'a', **attribs))
        self.body.append(attribs['href'])
        self.body.append(self.end_tag(node, suffix=''))

        raise nodes.SkipNode

    # ----------------------------------------------
    # confluence-builder -- enhancements -- emoticon
    # ----------------------------------------------

    def visit_confluence_emoticon_inline(self, node):
        self.body.append(self.start_tag(node, 'ac:emoticon', empty=True,
            **{'ac:name': self.encode(node.rawsource)}))

        raise nodes.SkipNode

    # -------------------------------------------
    # confluence-builder -- enhancements -- latex
    # -------------------------------------------

    def _visit_confluence_latex(self, node, macro, param=None):
        latex_content = node.rawsource

        # if this block is numbered, attempt to align in on the following macro
        if node.get('from_math') and node.get('number'):
            if self.builder.config.math_numfig and self.builder.config.numfig:
                figtype = 'displaymath'
                if self.builder.name == 'singleconfluence':
                    key = f'{self._docnames[-1]}/{figtype}'
                else:
                    key = figtype

                id_ = node['ids'][0]
                number = self.builder.fignumbers.get(key, {}).get(id_, ())
                number = '.'.join(map(str, number))
            else:
                number = node['number']

            self.body.append(self.start_tag(node, 'div',
                **{'style': 'float: right'}))
            self.body.append(f'({number})')
            self.body.append(self.end_tag(node))

        self.body.append(self.start_ac_macro(node, macro))
        if param is not None:
            latex_content = self.encode(latex_content)
            self.body.append(self.build_ac_param(node, param, latex_content))
        else:
            self.body.append(self.start_ac_plain_text_body_macro(node))
            self.body.append(self.escape_cdata(latex_content))
            self.body.append(self.end_ac_plain_text_body_macro(node))
        self.body.append(self.end_ac_macro(node))

        raise nodes.SkipNode

    def visit_confluence_latex_block(self, node):
        if not self.builder.config.confluence_latex_macro:
            self.warn('ignoring node since no latex macro configured')
            raise nodes.SkipNode

        config = self.builder.config.confluence_latex_macro
        macro = config['block-macro']
        self._visit_confluence_latex(node, macro)

    def visit_confluence_latex_inline(self, node):
        if not self.builder.config.confluence_latex_macro:
            self.warn('ignoring node since no latex macro configured')
            raise nodes.SkipNode

        config = self.builder.config.confluence_latex_macro
        macro = config['inline-macro']
        param = config.get('inline-macro-param')
        self._visit_confluence_latex(node, macro, param=param)

    # ---------------------------------------------
    # confluence-builder -- enhancements -- mathjax
    # ---------------------------------------------

    def visit_confluence_mathjax_block(self, node):
        # if this block is numbered, attempt to align in on the following block
        if node.get('from_math') and node.get('number'):
            if self.builder.config.math_numfig and self.builder.config.numfig:
                figtype = 'displaymath'
                if self.builder.name == 'singleconfluence':
                    key = f'{self._docnames[-1]}/{figtype}'
                else:
                    key = figtype

                id_ = node['ids'][0]
                number = self.builder.fignumbers.get(key, {}).get(id_, ())
                number = '.'.join(map(str, number))
            else:
                number = node['number']

            self.body.append(self.start_tag(node, 'div',
                **{'style': 'float: right'}))
            self.body.append(f'({number})')
            self.body.append(self.end_tag(node))

        attribs = {}
        alignment = self._fetch_alignment(node)
        if alignment and alignment != 'left':
            attribs['style'] = f'text-align: {alignment};'

        self.body.append(self.start_tag(node, 'div', **attribs))
        self.body.append(self.encode(node.rawsource))
        self.body.append(self.end_tag(node, suffix=''))
        raise nodes.SkipNode

    def visit_confluence_mathjax_inline(self, node):
        self.body.append(self.start_tag(node, 'span'))
        self.body.append(self.encode(node.rawsource))
        self.body.append(self.end_tag(node, suffix=''))
        raise nodes.SkipNode

    # ----------------------------------------------
    # confluence-builder -- enhancements -- mentions
    # ----------------------------------------------

    def visit_confluence_mention_inline(self, node):
        mappings = self.builder.config.confluence_mentions
        raw_identifier = node.rawsource

        identifier = mappings.get(raw_identifier, raw_identifier)

        # Confluence Cloud account identifier?
        if ':' in identifier:
            key = 'account-id'
        # Confluence server 32-sized user-key hash? (assumed)
        elif len(identifier) == 32:
            key = 'userkey'
        else:
            key = 'username'

        self.body.append(self.start_ac_link(node))
        self.body.append(self.start_tag(node, 'ri:user',
            suffix=self.nl, empty=True,
            **{'ri:' + key: self.encode(identifier)}))
        self.body.append(self.end_ac_link(node))

        raise nodes.SkipNode

    # ------------------------------------------
    # confluence-builder -- enhancements -- jira
    # ------------------------------------------

    def _visit_jira_node(self, node):
        self.body.append(self.start_ac_macro(node, 'jira'))
        for k, v in sorted(PARAMS(node).items()):
            self.body.append(self.build_ac_param(node, k, v))
        self.body.append(self.end_ac_macro(node))

        raise nodes.SkipNode

    visit_jira = _visit_jira_node
    visit_jira_issue = _visit_jira_node

    # --------------------------------------------
    # confluence-builder -- enhancements -- status
    # --------------------------------------------

    def visit_confluence_status_inline(self, node):
        self.body.append(self.start_ac_macro(node, 'status'))
        for k, v in sorted(PARAMS(node).items()):
            self.body.append(self.build_ac_param(node, k, v))
        self.body.append(self.end_ac_macro(node))

        raise nodes.SkipNode

    # -----------------------------------------
    # confluence-builder -- enhancements -- toc
    # -----------------------------------------

    def visit_confluence_toc(self, node):
        self.body.append(self.start_ac_macro(node, 'toc'))
        for k, v in sorted(PARAMS(node).items()):
            self.body.append(self.build_ac_param(node, k, v))
        self.body.append(self.end_ac_macro(node))

        raise nodes.SkipNode

    # ---------------------------------------------------
    # sphinx -- extension (third party) -- jupyter-sphinx
    # ---------------------------------------------------

    def visit_CellInputNode(self, node):
        pass

    def depart_CellInputNode(self, node):
        pass

    def visit_CellOutputNode(self, node):
        pass

    def depart_CellOutputNode(self, node):
        pass

    def visit_JupyterCellNode(self, node):
        pass

    def depart_JupyterCellNode(self, node):
        pass

    def visit_MimeBundleNode(self, node):
        # note: do not promote svgs first in v2, since the v2 editor does not
        #       display SVGs as nice as v1 editor does
        if self.v2:
            preferred_mimetypes = ['image/png', 'image/jpeg', 'image/svg+xml']
        else:
            preferred_mimetypes = ['image/svg+xml', 'image/png', 'image/jpeg']

        mimetypes = node.get('mimetypes', [])
        for mimetype in mimetypes:
            if mimetype in preferred_mimetypes:
                idx = node['mimetypes'].index(mimetype)
                self.visit_image(node[idx])
                self.depart_image(node[idx])
                raise nodes.SkipNode

        if 'text/plain' in mimetypes:
            idx = node['mimetypes'].index('text/plain')
            self.body.append(self.encode(node[idx].astext()))

        raise nodes.SkipNode

    # ---------------------------------------------
    # sphinx -- extension (third party) -- nbsphinx
    # ---------------------------------------------

    def visit_AdmonitionNode(self, node):
        if 'warning' in node.get('classes', []):
            self._visit_warning(node)
        else:
            self._visit_info(node)

    depart_AdmonitionNode = _depart_admonition

    def visit_CodeAreaNode(self, node):
        # if nbsphinx provides a prompt for a code block, use it for the title
        # values (since we cannot gracefully inject it on the side of the
        # block)
        prompt = node.get('prompt', None)
        if prompt:
            next_child = first(findall(node, include_self=False))
            if isinstance(next_child, nodes.literal_block):
                next_child['scb-caption'] = re.escape(prompt)

    def depart_CodeAreaNode(self, node):
        pass

    def visit_FancyOutputNode(self, node):
        pass

    def depart_FancyOutputNode(self, node):
        pass

    # -------------------------------------------------------
    # sphinx -- extension (third party) -- sphinx-data-viewer
    # -------------------------------------------------------

    def visit_DataViewerNode(self, node):
        data = json.dumps(json.loads(node['data']), indent=4)

        title = node.get('title', None)
        if title:
            title = self.encode(title)

        # use the `none` language type by default; however, if it appears
        # that this configuration supports json rendering, use that instead
        target_lang = 'none'
        if self.builder.lang_transform:
            new_target_lang = self.builder.lang_transform('json')
            if 'json' in new_target_lang:
                target_lang = new_target_lang

        self.body.append(self.start_ac_macro(node, 'code'))
        self.body.append(self.build_ac_param(node, 'language', target_lang))

        if title:
            self.body.append(self.build_ac_param(node, 'title', title))

        expand = node.get('expand', None)
        if not expand:
            self.body.append(self.build_ac_param(node, 'collapse', 'true'))

        self.body.append(self.start_ac_plain_text_body_macro(node))
        self.body.append(self.escape_cdata(data))
        self.body.append(self.end_ac_plain_text_body_macro(node))
        self.body.append(self.end_ac_macro(node))

        raise nodes.SkipNode

    # -------------------------------------------------
    # sphinx -- extension (third party) -- sphinx-needs
    # -------------------------------------------------

    def visit_PassthroughTextElement(self, node):
        pass

    def depart_PassthroughTextElement(self, node):
        pass

    # ---------------------------------------------------
    # sphinx -- extension (third party) -- sphinx-toolbox
    # ---------------------------------------------------

    def visit_ItalicAbbreviationNode(self, node):
        self.body.append(self.start_tag(node, 'i'))
        self.context.append(self.end_tag(node))
        self.visit_abbreviation(node)

    def depart_ItalicAbbreviationNode(self, node):
        self.depart_abbreviation(node)
        self.body.append(self.context.pop())  # i

    # -------------------------------------------------
    # sphinx -- extension (third party) -- sphinx-video
    # -------------------------------------------------

    def visit_video_node(self, node):
        autoplay = node.get('autoplay')
        height, hu = extract_length(node.get('height'))
        width, wu = extract_length(node.get('width'))
        if 'sources' in node:  # v0.2.1+
            sources = node.get('sources', [])
            source_path, _, _ = first(sources) or (None, None, None)
        else:
            source_path, _ = node.get('primary_src') or (None, None)

        if height:
            height = convert_length(height, hu)
            if height is None:
                self.warn('unsupported unit type for confluence: ' + hu)

        if width:
            width = convert_length(width, wu)
            if width is None:
                self.warn('unsupported unit type for confluence: ' + wu)

        video_key, _, _ = self.assets.add(source_path, self.docname)

        if not video_key:
            self.warn(f'Unable to find video name: {source_path}')
            raise nodes.SkipNode

        ri_filename = self.start_ri_attachment(node, video_key) + \
            self.end_ri_attachment(node)

        self.body.append(self.start_tag(node, 'div'))
        self.body.append(self.start_ac_macro(node, 'multimedia'))
        self.body.append(self.build_ac_param(node, 'name', ri_filename))
        if width:
            self.body.append(self.build_ac_param(node, 'width', width))
        if height:
            self.body.append(self.build_ac_param(node, 'height', height))
        if autoplay:
            self.body.append(self.build_ac_param(node, 'autostart', 'true'))
        self.body.append(self.end_ac_macro(node))
        self.body.append(self.end_tag(node))
        raise nodes.SkipNode

    # ---------------------------------------------------
    # sphinx -- extension (third party) -- sphinx-youtube
    # ---------------------------------------------------

    def _visit_video(self, node, uri):
        height, hu = node.get('height') or (None, None)
        width, wu = node.get('width') or (None, None)

        if height:
            height = convert_length(height, hu)
            if height is None:
                self.warn('unsupported unit type for confluence: ' + hu)

        if width:
            width = convert_length(width, wu)
            if width is None:
                self.warn('unsupported unit type for confluence: ' + wu)

        attribs = {}
        alignment = self._fetch_alignment(node)
        if alignment and alignment != 'left':
            attribs['style'] = f'text-align: {alignment};'

        ri_url = self.start_tag(
            node, 'ri:url', empty=True, **{'ri:value': self.encode(uri)})

        self.body.append(self.start_tag(node, 'div', **attribs))
        self.body.append(self.start_ac_macro(node, 'widget'))
        self.body.append(self.build_ac_param(node, 'url', ri_url))
        if height:
            self.body.append(self.build_ac_param(node, 'height', height))
        if width:
            self.body.append(self.build_ac_param(node, 'width', width))
        self.body.append(self.end_ac_macro(node))
        self.body.append(self.end_tag(node))

        raise nodes.SkipNode

    def visit_vimeo(self, node):
        self._visit_video(node, 'https://vimeo.com/' + node['id'])

    def visit_youtube(self, node):
        self._visit_video(node, 'https://www.youtube.com/watch?v=' + node['id'])

    # -------------------------------------------------------
    # sphinx -- extension (third party) -- sphinxnotes-strike
    # -------------------------------------------------------

    def visit_strike_node(self, node):
        self.body.append(self.start_tag(node, 's'))
        self.context.append(self.end_tag(node, suffix=''))

    def depart_strike_node(self, node):
        self.body.append(self.context.pop())  # s

    # -------------
    # miscellaneous
    # -------------

    def visit_abbreviation(self, node):
        attribs = {}
        if 'explanation' in node:
            title_value = node['explanation']
            title_value = self.encode(title_value)
            attribs['title'] = title_value

        self.body.append(self.start_tag(node, 'abbr', **attribs))
        self.context.append(self.end_tag(node, suffix=''))

    def depart_abbreviation(self, node):
        self.body.append(self.context.pop())  # abbr

    def visit_acronym(self, node):
        # Note: docutils indicates this directive is "to be completed"

        self.body.append(self.start_tag(node, 'acronym'))
        self.context.append(self.end_tag(node, suffix=''))

    def depart_acronym(self, node):
        self.body.append(self.context.pop())  # acronym

    @visit_auto_context_decorator()
    def visit_container(self, node):
        # [sphinx-design]
        # check if the container has a sphinx-design component
        sdc = node.get('design_component')

        if 'collapse' in node.get('classes', []) or sdc == 'dropdown':
            self.body.append(self.start_ac_macro(node, 'expand'))
            self.auto_append(self.end_ac_macro(node))

            if sdc == 'dropdown':
                next_child = first(findall(node, include_self=False))
                if isinstance(next_child, nodes.rubric):
                    self.body.append(self.build_ac_param(
                        node, 'title', next_child.astext()))

            self.body.append(self.start_ac_rich_text_body_macro(node))
            self.auto_append(self.end_ac_rich_text_body_macro(node))
        else:
            if sdc == 'card':
                self.body.append(self.start_ac_macro(node, 'panel'))
                self.body.append(self.build_ac_param(node, 'borderWidth', '2'))

                self.auto_append(self.end_ac_macro(node))
                self.body.append(self.start_ac_rich_text_body_macro(node))
                self.auto_append(self.end_ac_rich_text_body_macro(node))

            if sdc == 'card-footer':
                self.body.append(self.start_tag(
                    node, 'hr', suffix=self.nl, empty=True))

            self.body.append(self.start_tag(node, 'div'))
            self.auto_append(self.end_tag(node))

            if sdc == 'card-title':
                self.body.append(self.start_tag(node, 'strong'))
                self.auto_append(self.end_tag(node))

    @depart_auto_context_decorator()
    def depart_container(self, node):
        # [sphinx-design]
        # check if the container has a sphinx-design component
        sdc = node.get('design_component')

        if sdc == 'card-header':
            self.body.append(self.start_tag(
                node, 'hr', suffix=self.nl, empty=True))

    def depart_line(self, node):
        next_sibling = first(findall(node,
            include_self=False, descend=False, siblings=True))
        if isinstance(next_sibling, nodes.line):
            self.body.append('<br />')

    def visit_line_block(self, node):
        attribs = {}
        style = ''

        if self.v2:
            tag = 'p'
        else:
            tag = 'div'

            # if this line-block is not the first element in the parent and the
            # parent is not a line-block, add some separation from a previous
            # sibling element
            if node.parent[0] != node and not isinstance(node.parent, nodes.line_block):
                style += f'padding-top: {FCMMO}px;'

        # indent this line-block if its not the first element in the parent
        # (excluding titles for a new section), or if the parent is
        # also a line-block
        if (node.parent[0] != node and
                not isinstance(node.parent[0], nodes.title)) or \
                isinstance(node.parent, nodes.line_block):

            indent = INDENT

            # if v2, apply additional indentation (if needed)
            # (see "visit_paragraph")
            if self.v2:
                indent = INDENT * (self._indent_level + 1)

            style += f'margin-left: {indent}px;'
        elif self.v2:
            # (see "visit_paragraph")
            offset = INDENT * self._indent_level
            style += f'margin-left: {offset}px;'

        if style:
            attribs['style'] = style

        self.body.append(self.start_tag(node, tag, **attribs))
        self.context.append(self.end_tag(node))

    def depart_line_block(self, node):
        self.body.append(self.context.pop())  # div

    def visit_raw(self, node):
        # providing an advanced option to allow raw html injection in the output
        #
        # This is not always guaranteed to work; the raw html content may not
        # be compatible with Atlassian's storage format. Results may fail to
        # publish or contents may be suppressed on the Confluence instance. This
        # is provided to help users wanted to somewhat support raw HTML content
        # generated from Markdown sources.
        permit_raw_html = self.builder.config.confluence_permit_raw_html
        if permit_raw_html:
            if 'html' in node.get('format', '').split():
                raw_html = self.nl.join(node.astext().splitlines())

                # boolean flag -- raw injection of html
                if isinstance(permit_raw_html, bool):
                    self.body.append(raw_html)
                # string value -- placed in an supported HTML macro available
                # on the user's Confluence instance
                else:
                    macro = permit_raw_html
                    self.body.append(self.start_ac_macro(node, macro))
                    self.body.append(self.start_ac_plain_text_body_macro(node))
                    self.body.append(self.escape_cdata(raw_html))
                    self.body.append(self.end_ac_plain_text_body_macro(node))
                    self.body.append(self.end_ac_macro(node))

                raise nodes.SkipNode

        if 'confluence_storage' in node.get('format', '').split():
            self.body.append(self.nl.join(node.astext().splitlines()))
        else:
            # support deprecated 'confluence' format for an interim
            ConfluenceBaseTranslator.visit_raw(self, node)
        raise nodes.SkipNode

    # ##########################################################################
    # #                                                                        #
    # # helpers                                                                #
    # #                                                                        #
    # ##########################################################################

    def _build_id_anchors(self, node):
        """
        build anchors for a node that has any ids

        A node may define one more more identifiers through an `ids` list.
        For some nodes, it may be ideal to generate anchor links for each
        identifier listed, which may be used by other nodes to link to. For
        example, a paragraph may have multiple identifiers assigned to it,
        which features like autotools may want to jump to said paragraph.

        Note all use cases where a node has an identifier will need to build
        an anchor (so, it is not done automatically). This call can be used
        to explicitly build anchors on nodes that require it.

        Args:
            node: the node to generate anchors on
        """

        if 'ids' in node:
            for id_ in node['ids']:
                self._build_anchor(node, id_)

    def _build_anchor(self, node, anchor):
        """
        build an anchor on a page

        A helper is used to build a anchor on a current page. Using the
        provided anchor value, an anchor macro will be added to the body of
        the page.

        In addition, for v2 editor, an additional macro will be created to
        emulate the original Confluence design of document-prefixed anchors.
        While we would like to move away from this format, ac:links to other
        pages with anchors requires the prefixes to properly link (since they
        expect the prefix to exist; see `_visit_reference_intern_uri`).

        Args:
            node: the node adding the anchor
            anchor: the name of the anchor to create
        """

        self.verbose(f'build anchor ({self.docname}): {anchor}')
        self.body.append(self.start_ac_macro(node, 'anchor'))
        self.body.append(self.build_ac_param(node, '', anchor))
        self.body.append(self.end_ac_macro(node, suffix=''))

        if self.v2:
            doctitle = self.state.title(self.docname)
            doctitle = self.encode(doctitle.replace(' ', ''))

            compat_anchor = f'{doctitle}-{anchor}'
            self.verbose(f'build anchor ({self.docname}): {compat_anchor}')
            self.body.append(self.start_ac_macro(node, 'anchor'))
            self.body.append(self.build_ac_param(node, '', compat_anchor))
            self.body.append(self.end_ac_macro(node, suffix=''))

    def start_tag(self, node, tag, suffix=None, empty=False, **kwargs):
        """
        generates start tag content for a given node

        A helper used to return content to be appended to a document which
        initializes the start of a storage format element (i.e. generates a
        start tag). The element of type ``tag`` will be initialized. This
        method may use the provided ``node`` to tweak the final content.
        Non-empty tags should be used with a respective :func:`end_tag` call.

        .. code-block:: python

            def visit_custom_node(self, node):
                self.body.append(self.start_tag(node, 'p'))
                self.context.append(self.end_tag(node))

            def depart_custom_node(self, node):
                self.body.append(self.context.pop())

        Args:
            node: the node processing the start-tag
            tag: the type of tag
            suffix (optional): the suffix to add (defaults to nothing)
            empty (optional): tag will not hold child nodes (defaults to
                              ``False``)
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
            data.append(f'{key}="{value}"')

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

        prefix = ' '.join(data)
        return f'<{prefix}{suffix}'

    def end_tag(self, node, suffix=None):
        """
        generates end tag content for a given node

        A helper used to return content to be appended to a document which
        finalizes a storage format element (i.e. generates an end tag). This
        method should be used to help close a :func:`start_tag` call (with the
        exception of when :func:`start_tag` is invoked with ``empty=True``).

        Args:
            node: the node processing the end-tag
            suffix (optional): the suffix to add (defaults to newline)

        Returns:
            the content
        """
        try:
            tag = node.__confluence_tag.pop()
        except IndexError as ex:
            msg = 'end tag invoke without matching start tag'
            raise ConfluenceError(msg) from ex

        if suffix is None:
            suffix = self.nl

        return f'</{tag}>{suffix}'

    def build_ac_param(self, node, name, value):
        """
        generates a confluence parameter element

        A helper used to return content to be appended to a document which
        builds a complete storage format parameter element. The
        ``ac:parameter`` element will be built. This method may use provided
        ``node`` to tweak the final content.

        Args:
            node: the node processing the parameter
            name: the parameter name
            value: the value for the parameter

        Returns:
            the content
        """
        return (self.start_tag(node, 'ac:parameter', **{'ac:name': name}) +
            str(value) + self.end_tag(node))

    def start_ac_image(self, node, **kwargs):
        """
        generates a confluence image start tag

        A helper used to return content to be appended to a document which
        initializes the start of a storage format image element. The
        ``ac:image`` element will be initialized. This method may use provided
        ``node`` to tweak the final content. This call should be used with a
        respective :func:`end_ac_image` call.

        Args:
            node: the node processing the image

        Returns:
            the content
        """
        return self.start_tag(node, 'ac:image', suffix=self.nl, **kwargs)

    def end_ac_image(self, node):
        """
        generates confluence image end tag content for a node

        A helper used to return content to be appended to a document which
        finalizes a storage format image element. This method should be used to
        help close a :func:`start_ac_image` call.

        Args:
            node: the node processing the image

        Returns:
            the content
        """
        return self.end_tag(node, suffix='')

    def start_ac_link(self, node, anchor=None, appearance=None):
        """
        generates a confluence link start tag

        A helper used to return content to be appended to a document which
        initializes the start of a storage format link element of a specific
        ``type``. The ``ac:link`` element will be initialized. This method may
        use provided ``node`` to tweak the final content. This call should be
        used with a respective :func:`end_ac_link` call.

        Args:
            node: the node processing the link
            anchor (optional): the anchor value to use (defaults to ``None``)
            appearance (optional): card appearance to use (defaults to ``None``)

        Returns:
            the content
        """
        attribs = {}
        if anchor:
            attribs['ac:anchor'] = anchor
        if appearance:
            attribs['ac:card-appearance'] = appearance
        return self.start_tag(node, 'ac:link', suffix=self.nl, **attribs)

    def end_ac_link(self, node):
        """
        generates confluence link end tag content for a node

        A helper used to return content to be appended to a document which
        finalizes a storage format link element. This method should be used to
        help close a :func:`start_ac_link` call.

        Args:
            node: the node processing the link

        Returns:
            the content
        """
        return self.end_tag(node, suffix='')

    def start_ac_macro(self, node, type_, empty=False):
        """
        generates a confluence macro start tag

        A helper used to return content to be appended to a document which
        initializes the start of a storage format macro element of a specific
        ``type``. The ``ac:structured-macro`` element will be initialized. This
        method may use provided `node` to tweak the final content. This call
        should be used with a respective :func:`end_ac_macro` call.

        Args:
            node: the node processing the macro
            type_: the type of macro
            empty (optional): tag will not hold child nodes (defaults to
                              ``False``)

        Returns:
            the content
        """
        return self.start_tag(node, 'ac:structured-macro',
            suffix=self.nl, empty=empty, **{'ac:name': type_})

    def end_ac_macro(self, node, suffix=None):
        """
        generates confluence macro end tag content for a node

        A helper used to return content to be appended to a document which
        finalizes a storage format macro element. This method should be used to
        help close a :func:`start_ac_macro` call (with the exception of when
        :func:`start_ac_macro` is invoked with ``empty=True``).

        Args:
            node: the node processing the macro
            suffix (optional): the suffix to add (defaults to newline)

        Returns:
            the content
        """
        return self.end_tag(node, suffix=suffix)

    def start_ac_link_body(self, node):
        """
        generates a confluence link-body start tag

        A helper used to return content to be appended to a document which
        initializes the start of a storage format link-body element. The
        ``ac:link-body`` element will be initialized. This method may use
        provided ``node`` to tweak the final content. This call should be used
        with a respective :func:`end_ac_link_body` call.

        Args:
            node: the node processing the macro

        Returns:
            the content
        """
        return self.start_tag(node, 'ac:link-body')

    def end_ac_link_body(self, node):
        """
        generates confluence link-body end tag content for a node

        A helper used to return content to be appended to a document which
        finalizes a storage format link-body element. This method should be
        used to help close a :func:`start_ac_link_body` call.

        Args:
            node: the node processing the macro

        Returns:
            the content
        """
        return self.end_tag(node)

    def start_ac_rich_text_body_macro(self, node):
        """
        generates a confluence rich-text-body start tag

        A helper used to return content to be appended to a document which
        initializes the start of a storage format rich-text-body element. The
        ``ac:rich-text-body`` element will be initialized. This method may use
        provided ``node`` to tweak the final content. This call should be used
        with a respective :func:`end_ac_rich_text_body_macro` call.

        Args:
            node: the node processing the macro

        Returns:
            the content
        """
        return self.start_tag(node, 'ac:rich-text-body')

    def end_ac_rich_text_body_macro(self, node):
        """
        generates confluence rich-text-body end tag content for a node

        A helper used to return content to be appended to a document which
        finalizes a storage format rich-text-body element. This method should
        be used to help close a :func:`start_ac_rich_text_body_macro` call.

        Args:
            node: the node processing the macro

        Returns:
            the content
        """
        return self.end_tag(node)

    def start_ac_plain_text_body_macro(self, node):
        """
        generates a confluence plain-text-body start tag

        A helper used to return content to be appended to a document which
        initializes the start of a storage format plain-text-body element. The
        ``ac:plain-text-body`` element will be initialized. This method may use
        provided ``node`` to tweak the final content. This call should be used
        with a respective :func:`end_ac_plain_text_body_macro` call.

        Args:
            node: the node processing the macro

        Returns:
            the content
        """
        return self.start_tag(node, 'ac:plain-text-body', suffix='<![CDATA[')

    def end_ac_plain_text_body_macro(self, node):
        """
        generates confluence plain-text-body end tag content for a node

        A helper used to return content to be appended to a document which
        finalizes a storage format plain-text-body element. This method should
        be used to help close a :func:`start_ac_plain_text_body_macro` call.

        Args:
            node: the node processing the macro

        Returns:
            the content
        """
        return ']]>' + self.end_tag(node)

    def start_ac_plain_text_link_body_macro(self, node):
        """
        generates a confluence plain-text-link-body start tag

        A helper used to return content to be appended to a document which
        initializes the start of a storage format plain-text-body element. The
        ``ac:plain-text-body`` element will be initialized. This method may use
        provided ``node`` to tweak the final content. This call should be used
        with a respective :func:`end_ac_plain_text_link_body_macro` call.

        Args:
            node: the node processing the macro

        Returns:
            the content
        """
        return self.start_tag(node, 'ac:plain-text-link-body',
            suffix='<![CDATA[')

    def end_ac_plain_text_link_body_macro(self, node):
        """
        generates confluence plain-text-link-body end tag content for a node

        A helper used to return content to be appended to a document which
        finalizes a storage format plain-text-link-body element. This method
        should be used to help close a
        :func:`start_ac_plain_text_link_body_macro` call.

        Args:
            node: the node processing the macro

        Returns:
            the content
        """
        return ']]>' + self.end_tag(node)

    def start_ri_attachment(self, node, filename):
        """
        generates a confluence attachment start tag

        A helper used to return content to be appended to a document which
        initializes the start of a storage format attachment element. The
        ``ri:attachment`` element will be initialized. This method may use
        provided ``node`` to tweak the final content.

        Args:
            node: the node processing the attachment
            filename: the filename of the attachment

        Returns:
            the content
        """
        return self.start_tag(node, 'ri:attachment',
            **{'ri:filename': filename})

    def end_ri_attachment(self, node):
        """
        generates confluence attachment end tag content for a node

        A helper used to return content to be appended to a document which
        finalizes a storage format attachment element. This method should be
        used to help close a :func:`start_ri_attachment` call.

        Args:
            node: the node processing the attachment

        Returns:
            the content
        """
        return self.end_tag(node)

    def start_adf_extension(self, node):
        """
        generates a confluence adf-extension start tag

        A helper used to return content to be appended to a document which
        initializes the start of a storage format adf-extension element. The
        ``ac:adf-extension`` element will be initialized. This call should be
        used with a respective :func:`start_adf_extension` call.

        Args:
            node: the node processing the macro

        Returns:
            the content
        """
        return self.start_tag(node, 'ac:adf-extension')

    def end_adf_extension(self, node, suffix=None):
        """
        generates confluence adf-extension end tag content for a node

        A helper used to return content to be appended to a document which
        finalizes a storage format adf-extension element. This method should
        be used to help close a :func:`start_adf_extension` call.

        Args:
            node: the node processing the macro
            suffix (optional): the suffix to add (defaults to newline)

        Returns:
            the content
        """
        return self.end_tag(node, suffix=suffix)

    def start_adf_node(self, node, type_, empty=False):
        """
        generates a confluence adf-node start tag

        A helper used to return content to be appended to a document which
        initializes the start of a storage format adf-node element of a
        specific ``type``. The ``ac:adf-node`` element will be initialized.
        This method may use provided ``node`` to tweak the final content. This
        call should be used with a respective :func:`end_adf_node` call.

        Args:
            node: the node processing the macro

        Returns:
            the content
        """
        return self.start_tag(node, 'ac:adf-node',
            empty=empty, **{'type': type_})

    def end_adf_node(self, node, suffix=None):
        """
        generates confluence adf-node end tag content for a node

        A helper used to return content to be appended to a document which
        finalizes a storage format adf-node element. This method should be
        used to help close a :func:`start_adf_node` call (with the exception
        of when :func:`start_adf_node` is invoked with ``empty=True``).

        Args:
            node: the node processing the macro
            suffix (optional): the suffix to add (defaults to newline)

        Returns:
            the content
        """
        return self.end_tag(node, suffix=suffix)

    def build_adf_attribute(self, node, name, value):
        """
        generates a confluence parameter element

        A helper used to return content to be appended to a document which
        builds a complete storage format parameter element. The
        ``ac:adf-attribute`` element will be built. This method may use
        provided ``node`` to tweak the final content.

        Args:
            node: the node processing the parameter
            name: the parameter name
            value: the value for the parameter

        Returns:
            the content
        """
        return (self.start_tag(node, 'ac:adf-attribute', **{'key': name}) +
            value + self.end_tag(node))

    def start_adf_content(self, node):
        """
        generates a confluence adf-content start tag

        A helper used to return content to be appended to a document which
        initializes the start of a storage format adf-content element. The
        ``ac:adf-content`` element will be initialized. This method may use
        provided ``node`` to tweak the final content. This call should be used
        with a respective :func:`end_adf_content` call.

        Args:
            node: the node processing the macro

        Returns:
            the content
        """
        return self.start_tag(node, 'ac:adf-content')

    def end_adf_content(self, node, suffix=None):
        """
        generates confluence adf-content end tag content for a node

        A helper used to return content to be appended to a document which
        finalizes a storage format adf-content element. This method should be
        used to help close a :func:`start_adf_content` call.

        Args:
            node: the node processing the macro
            suffix (optional): the suffix to add (defaults to newline)

        Returns:
            the content
        """
        return self.end_tag(node, suffix=suffix)

    def escape_cdata(self, data):
        """
        escapes text to be inserted into a cdata

        A helper used to return content that has been properly escaped and can
        be directly placed inside a CDATA container.

        Args:
            data: the text

        Returns:
            the escaped text
        """

        # workaround for Confluence 8.0.x to 8.2.x series
        # (https://jira.atlassian.com/browse/CONFSERVER-82849)
        #
        # The else case here should be always working; however, in some
        # Confluence instances, there was a window where pages could not
        # be uploaded since Confluence would refuse the EOF sequence for
        # CDATA blocks. This workaround can help a user get their content
        # published at the unfortunate tweak of changing any trailing EOF
        # CDATA blocks to have a space character included.
        if self.builder.config.confluence_adv_quirk_cdata:
            data = data.replace(']]>', ']] >')
        else:
            data = data.replace(']]>', ']]]]><![CDATA[>')

        return ConfluenceBaseTranslator.encode(self, data)

    # ##########################################################################
    # #                                                                        #
    # # deprecated helpers                                                     #
    # #                                                                        #
    # # The following is a series of deprecated helper calls. While these have #
    # # been internal hinted, some users may have attempted to utilize them    #
    # # in their configurations/extensions. Being a bit flexible by still      #
    # # supporting them for a few releases (with a warning) to give users      #
    # # time to update.                                                        #
    # #                                                                        #
    # ##########################################################################

    def _build_ac_param(self, node, name, value):
        self._tracked_deprecated('_build_ac_param', 'build_ac_param')
        return self.build_ac_param(node, name, value)

    def _build_adf_attribute(self, node, name, value):
        self._tracked_deprecated('_build_adf_attribute', 'build_adf_attribute')
        return self.build_adf_attribute(node, name, value)

    def _end_ac_image(self, node):
        self._tracked_deprecated('_end_ac_image', 'end_ac_image')
        return self.end_ac_image(node)

    def _end_ac_link(self, node):
        self._tracked_deprecated('_end_ac_link', 'end_ac_link')
        return self.end_ac_link(node)

    def _end_ac_link_body(self, node):
        self._tracked_deprecated('_end_ac_link_body', 'end_ac_link_body')
        return self.end_ac_link_body(node)

    def _end_ac_macro(self, node, **kwargs):
        self._tracked_deprecated('_end_ac_macro', 'end_ac_macro')
        return self.end_ac_macro(node, **kwargs)

    def _end_ac_plain_text_body_macro(self, node):
        self._tracked_deprecated('_end_ac_plain_text_body_macro',
            'end_ac_plain_text_body_macro')
        return self.end_ac_plain_text_body_macro(node)

    def _end_ac_plain_text_link_body_macro(self, node):
        self._tracked_deprecated('_end_ac_plain_text_link_body_macro',
            'end_ac_plain_text_link_body_macro')
        return self.end_ac_plain_text_link_body_macro(node)

    def _end_ac_rich_text_body_macro(self, node):
        self._tracked_deprecated('_end_ac_rich_text_body_macro',
            'end_ac_rich_text_body_macro')
        return self.end_ac_rich_text_body_macro(node)

    def _end_adf_content(self, node, **kwargs):
        self._tracked_deprecated('_end_adf_content', 'end_adf_content')
        return self.end_adf_content(node, **kwargs)

    def _end_adf_extension(self, node, **kwargs):
        self._tracked_deprecated('_end_adf_extension', 'end_adf_extension')
        return self.end_adf_extension(node, **kwargs)

    def _end_adf_node(self, node, **kwargs):
        self._tracked_deprecated('_end_adf_node', 'end_adf_node')
        return self.end_adf_node(node, **kwargs)

    def _end_ri_attachment(self, node):
        self._tracked_deprecated('_end_ri_attachment', 'end_ri_attachment')
        return self.end_ri_attachment(node)

    def _end_tag(self, node, **kwargs):
        self._tracked_deprecated('_end_tag', 'end_tag')
        return self.end_tag(node, **kwargs)

    def _escape_cdata(self, data):
        self._tracked_deprecated('_escape_cdata', 'escape_cdata')
        return self.escape_cdata(data)

    def _start_ac_image(self, node, **kwargs):
        self._tracked_deprecated('_start_ac_image', 'start_ac_image')
        return self.start_ac_image(node, **kwargs)

    def _start_ac_link(self, node, anchor=None, appearance=None):
        self._tracked_deprecated('_start_ac_link', 'start_ac_link')
        return self.start_ac_link(node, anchor=anchor, appearance=appearance)

    def _start_ac_link_body(self, node):
        self._tracked_deprecated('_start_ac_link_body', 'start_ac_link_body')
        return self.start_ac_link_body(node)

    def _start_ac_macro(self, node, type_, **kwargs):
        self._tracked_deprecated('_start_ac_macro', 'start_ac_macro')
        return self.start_ac_macro(node, type_, **kwargs)

    def _start_ac_plain_text_body_macro(self, node):
        self._tracked_deprecated('_start_ac_plain_text_body_macro',
            'start_ac_plain_text_body_macro')
        return self.start_ac_plain_text_body_macro(node)

    def _start_ac_plain_text_link_body_macro(self, node):
        self._tracked_deprecated('_start_ac_plain_text_link_body_macro',
            'start_ac_plain_text_link_body_macro')
        return self.start_ac_plain_text_link_body_macro(node)

    def _start_ac_rich_text_body_macro(self, node):
        self._tracked_deprecated('_start_ac_rich_text_body_macro',
            'start_ac_rich_text_body_macro')
        return self.start_ac_rich_text_body_macro(node)

    def _start_adf_content(self, node):
        self._tracked_deprecated('_start_adf_content', 'start_adf_content')
        return self.start_adf_content(node)

    def _start_adf_extension(self, node):
        self._tracked_deprecated('_start_adf_extension', 'start_adf_extension')
        return self.start_adf_extension(node)

    def _start_adf_node(self, node, type_, **kwargs):
        self._tracked_deprecated('_start_adf_node', 'start_adf_node')
        return self.start_adf_node(node, type_, **kwargs)

    def _start_ri_attachment(self, node, filename):
        self._tracked_deprecated('_start_ri_attachment', 'start_ri_attachment')
        return self.start_ri_attachment(node, filename)

    def _start_tag(self, node, tag, **kwargs):
        self._tracked_deprecated('_start_tag', 'start_tag')
        return self.start_tag(node, tag, **kwargs)

    def _tracked_deprecated(self, prev, new):
        if not self.__tracked_deprecated:
            self.__tracked_deprecated = True
            self.warn(
                f'(developer) "{prev}" is deprecated; use "{new}" instead',
                subtype='deprecated_develop')
