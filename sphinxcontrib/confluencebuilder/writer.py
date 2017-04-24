# -*- coding: utf-8 -*-
"""
    sphinxcontrib.confluencebuilder.writer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2016-2017 by the contributors (see AUTHORS file).
    :license: BSD, see LICENSE.txt for details.
"""

from __future__ import (absolute_import, print_function, unicode_literals)
from .common import ConfluenceDocMap
from .common import ConfluenceLogger
from .experimental import EXPERIMENTAL_QUOTE_KEYWORD
from docutils import nodes, writers
from os import path
from sphinx import addnodes
from sphinx.locale import versionlabels
from sphinx.util.osutil import SEP
from sphinx.writers.text import TextTranslator, MAXWIDTH, STDINDENT
import codecs
import os
import sys
import textwrap
import logging

LANG_MAP = {
    'python': 'py'
}

class LIST_TYPES:
    BULLET = -1
    DEFINITION = -2
    ENUMERATED = 0

class ConfluenceWriter(writers.Writer):
    supported = ('text',)
    settings_spec = ('No options here.', '', ())
    settings_defaults = {}

    output = None

    def __init__(self, builder):
        writers.Writer.__init__(self)
        self.builder = builder

    def translate(self):
        visitor = ConfluenceTranslator(self.document, self.builder)
        self.document.walkabout(visitor)
        self.output = visitor.body

class ConfluenceTranslator(TextTranslator):
    docparent = ''

    def __init__(self, document, builder):
        TextTranslator.__init__(self, document, builder)

        # Determine document's name (if any).
        assert builder.current_docname
        self.docname = builder.current_docname
        if SEP in self.docname:
            self.docparent = self.docname[0:self.docname.rfind(SEP)+1]

        if not 'anchor' in builder.config.confluence_adv_restricted_macros:
            self.can_anchor = True
        else:
            self.can_anchor = False

        newlines = builder.config.text_newlines
        if newlines == 'windows':
            self.nl = '\r\n'
        elif newlines == 'native':
            self.nl = os.linesep
        else:
            self.nl = '\n'
        self.states = [[]]
        self.stateindent = [0]
        self.list_counter = []
        self.sectionlevel = 1
        self.table = None
        self.escape_newlines = 0
        self.quote_level = 0
        if self.builder.config.confluence_indent:
            self.indent = self.builder.config.confluence_indent
        else:
            self.indent = STDINDENT
        self.wrapper = textwrap.TextWrapper(width=STDINDENT,
                                            break_long_words=False,
                                            break_on_hyphens=False)

    def log_unknown(self, type, node):
        logger = logging.getLogger("sphinxcontrib.confluencebuilder.writer")
        if len(logger.handlers) == 0:
            # Logging is not yet configured. Configure it.
            logging.basicConfig(level=logging.INFO,
                                stream=sys.stderr,
                                format='%(levelname)-8s %(message)s')
            logger = logging.getLogger("sphinxcontrib.confluencebuilder.writer")
        logger.warning("%s(%s) unsupported formatting" % (type, node))

    def wrap(self, text, width=STDINDENT):
        self.wrapper.width = width
        return self.wrapper.wrap(text)

    def add_text(self, text):
        self.states[-1].append((-1, text))

    def new_state(self, indent=STDINDENT):
        self.states.append([])
        self.stateindent.append(indent)

    def end_state(self, end=[''], first=None):
        content = self.states.pop()
        maxindent = sum(self.stateindent)
        indent = self.stateindent.pop()
        result = []
        toformat = []

        def do_format():
            if not toformat:
                return
            res = ''.join(toformat).splitlines()
            if end:
                res += end
            result.append((indent, res))
        for itemindent, item in content:
            if itemindent == -1:
                toformat.append(item)
            else:
                do_format()
                result.append((indent + itemindent, item))
                toformat = []
        do_format()
        if first is not None and result:
            itemindent, item = result[0]
            if item:
                result.insert(0, (itemindent - indent, [first + item[0]]))
                result[1] = (itemindent, item[1:])
        self.states[-1].extend(result)

    def visit_document(self, node):
        self.new_state(0)

    def depart_document(self, node):
        self.end_state()
        self.body = "";

        if self.builder.config.confluence_header_file is not None:
            headerFile = path.join(self.builder.env.srcdir,
                self.builder.config.confluence_header_file)
            try:
                f = codecs.open(headerFile, 'r', 'utf-8')
                try:
                    self.body += f.read() + self.nl
                finally:
                    f.close()
            except (IOError, OSError) as err:
                self.builder.warn("error reading file %s: %s" % (headerFile, err))

        self.body += self.nl.join(line and (' '*indent + line)
                                 for indent, lines in self.states[0]
                                 for line in lines)

        if self.builder.config.confluence_footer_file is not None:
            footerFile = path.join(self.builder.env.srcdir,
                self.builder.config.confluence_footer_file)
            try:
                f = codecs.open(footerFile, 'r', 'utf-8')
                try:
                    self.body += f.read() + self.nl
                finally:
                    f.close()
            except (IOError, OSError) as err:
                self.builder.warn("error reading file %s: %s" % (footerFile, err))

    def visit_highlightlang(self, node):
        raise nodes.SkipNode

    def visit_section(self, node):
        level = 6 if self.sectionlevel > 6 else self.sectionlevel
        if self.builder.config.confluence_adv_writer_no_section_cap:
            level = self.sectionlevel
        self._title_char = 'h%i.' % level
        self.sectionlevel += 1

    def depart_section(self, node):
        self.sectionlevel -= 1

    def visit_topic(self, node):
        self.new_state(0)

    def depart_topic(self, node):
        self.end_state()

    visit_sidebar = visit_topic
    depart_sidebar = depart_topic

    def visit_rubric(self, node):
        self.new_state(0)
        self.add_text('-[ ')

    def depart_rubric(self, node):
        self.add_text(' ]-')
        self.end_state()

    def visit_compound(self, node):
        pass

    def depart_compound(self, node):
        pass

    def visit_glossary(self, node):
        pass

    def depart_glossary(self, node):
        pass

    def visit_title(self, node):
        if isinstance(node.parent, nodes.Admonition):
            self.add_text(node.astext()+': ')
            raise nodes.SkipNode
        self.new_state(0)

    def depart_title(self, node):
        if isinstance(node.parent, nodes.section):
            char = self._title_char
        else:
            char = '^'
        text = ''.join(x[1] for x in self.states.pop() if x[0] == -1)
        self.stateindent.pop()
        self.states[-1].append((0, ['%s %s' % (char, text), '']))

    def visit_subtitle(self, node):
        pass

    def depart_subtitle(self, node):
        pass

    def visit_attribution(self, node):
        self.add_text('-- ')

    def depart_attribution(self, node):
        pass

    def visit_desc(self, node):
        self.new_state(0)

    def depart_desc(self, node):
        self.end_state()

    def visit_desc_signature(self, node):
        if node.parent['objtype'] in ('class', 'exception', 'method', 'function'):
            self.add_text('**')
        else:
            self.add_text('``')

    def depart_desc_signature(self, node):
        if node.parent['objtype'] in ('class', 'exception', 'method', 'function'):
            self.add_text('**')
        else:
            self.add_text('``')

    def visit_desc_name(self, node):
        pass

    def depart_desc_name(self, node):
        pass

    def visit_desc_addname(self, node):
        pass

    def depart_desc_addname(self, node):
        pass

    def visit_desc_type(self, node):
        pass

    def depart_desc_type(self, node):
        pass

    def visit_desc_returns(self, node):
        self.add_text(' -> ')

    def depart_desc_returns(self, node):
        pass

    def visit_desc_parameterlist(self, node):
        self.add_text('(')
        self.first_param = 1

    def depart_desc_parameterlist(self, node):
        self.add_text(')')

    def visit_desc_parameter(self, node):
        if not self.first_param:
            self.add_text(', ')
        else:
            self.first_param = 0
        self.add_text(node.astext())
        raise nodes.SkipNode

    def visit_desc_optional(self, node):
        self.add_text('[')

    def depart_desc_optional(self, node):
        self.add_text(']')

    def visit_desc_annotation(self, node):
        content = node.astext()
        if len(content) > MAXWIDTH:
            h = int(MAXWIDTH/3)
            content = content[:h] + " ... " + content[-h:]
            self.add_text(content)
            raise nodes.SkipNode

    def depart_desc_annotation(self, node):
        pass

    def visit_refcount(self, node):
        pass

    def depart_refcount(self, node):
        pass

    def visit_desc_content(self, node):
        self.new_state(self.indent)

    def depart_desc_content(self, node):
        self.end_state()

    def visit_figure(self, node):
        self.new_state(self.indent)

    def depart_figure(self, node):
        self.end_state()

    def visit_caption(self, node):
        pass

    def depart_caption(self, node):
        pass

    def visit_productionlist(self, node):
        self.new_state(self.indent)
        names = []
        for production in node:
            names.append(production['tokenname'])
        maxlen = max(len(name) for name in names)
        for production in node:
            if production['tokenname']:
                self.add_text(production['tokenname'].ljust(maxlen) + ' ::=')
                lastname = production['tokenname']
            else:
                self.add_text('%s    ' % (' '*len(lastname)))
            self.add_text(production.astext() + self.nl)
        self.end_state()
        raise nodes.SkipNode

    def visit_seealso(self, node):
        self.new_state(self.indent)

    def depart_seealso(self, node):
        self.end_state(first='')

    def visit_footnote(self, node):
        self._footnote = node.children[0].astext().strip()
        self.new_state(len(self._footnote) + self.indent)

    def depart_footnote(self, node):
        self.end_state(first='[%s] ' % self._footnote)

    def visit_citation(self, node):
        if len(node) and isinstance(node[0], nodes.label):
            self._citlabel = node[0].astext()
        else:
            self._citlabel = ''
        self.new_state(len(self._citlabel) + self.indent)

    def depart_citation(self, node):
        self.end_state(first='[%s] ' % self._citlabel)

    def visit_label(self, node):
        raise nodes.SkipNode

    def visit_option_list(self, node):
        pass

    def depart_option_list(self, node):
        pass

    def visit_option_list_item(self, node):
        self.new_state(0)

    def depart_option_list_item(self, node):
        self.end_state()

    def visit_option_group(self, node):
        self._firstoption = True

    def depart_option_group(self, node):
        self.add_text('     ')

    def visit_option(self, node):
        if self._firstoption:
            self._firstoption = False
        else:
            self.add_text(', ')

    def depart_option(self, node):
        pass

    def visit_option_string(self, node):
        pass

    def depart_option_string(self, node):
        pass

    def visit_option_argument(self, node):
        self.add_text(node['delimiter'])

    def depart_option_argument(self, node):
        pass

    def visit_description(self, node):
        pass

    def depart_description(self, node):
        pass

    def visit_tabular_col_spec(self, node):
        raise nodes.SkipNode

    def visit_colspec(self, node):
        self.table[0].append(node['colwidth'])
        raise nodes.SkipNode

    def visit_tgroup(self, node):
        pass

    def depart_tgroup(self, node):
        pass

    def visit_thead(self, node):
        pass

    def depart_thead(self, node):
        pass

    def visit_tbody(self, node):
        self.table.append('sep')

    def depart_tbody(self, node):
        pass

    def visit_row(self, node):
        self.table.append([])

    def depart_row(self, node):
        pass

    def visit_entry(self, node):
        if ['morerows', 'morecols'] in node.attlist():
            raise NotImplementedError('Column or row spanning cells are '
                                      'not implemented.')
        self.new_state(0)

    def depart_entry(self, node):
        text = self.nl.join(self.nl.join(x[1]) for x in self.states.pop())
        self.stateindent.pop()
        self.table[-1].append(text)

    def visit_table(self, node):
        if self.table:
            raise NotImplementedError('Nested tables are not supported.')
        self.new_state(0)
        self.table = [[]]

    def depart_table(self, node):
        lines = self.table[1:]
        fmted_rows = []
        colwidths = self.table[0]
        realwidths = colwidths[:]
        separator = 0
        # don't allow paragraphs in table cells for now
        for line in lines:
            if line == 'sep':
                separator = len(fmted_rows)
            else:
                cells = []
                for i, cell in enumerate(line):
                    par = self.wrap(cell, width=colwidths[i])
                    if par:
                        maxwidth = max(map(len, par))
                    else:
                        maxwidth = 0
                    realwidths[i] = max(realwidths[i], maxwidth)
                    cells.append(par)
                fmted_rows.append(cells)

        def writerow(row, double=False):
            lines = zip(*row)
            sep = '|' if not double else '||'
            for line in lines:
                out = [sep]
                for i, cell in enumerate(line):
                    if cell:
                        out.append(' ' + cell.ljust(realwidths[i]+1))
                    else:
                        out.append(' ' * (realwidths[i] + 2))
                    out.append(sep)
                self.add_text(''.join(out) + self.nl)
        is_heading = True
        for i, row in enumerate(fmted_rows):
            if separator and i == separator:
                is_heading = False
            writerow(row, is_heading)

        self.table = None
        self.end_state()

    def visit_acks(self, node):
        self.new_state(0)
        self.add_text(', '.join(n.astext() for n in node.children[0].children)
                      + '.')
        self.end_state()
        raise nodes.SkipNode

    def visit_image(self, node):
        if 'alt' in node.attributes:
            self.add_text('[image: %s]' % node['alt'])
        self.add_text('[image]')
        raise nodes.SkipNode

    def visit_transition(self, node):
        self.new_state(0)
        self.add_text('----')
        self.end_state()
        raise nodes.SkipNode

    def visit_bullet_list(self, node):
        self.list_counter.append(LIST_TYPES.BULLET)

    def depart_bullet_list(self, node):
        self.list_counter.pop()
        self.new_state(0)
        self.add_text('')
        self.end_state()

    def visit_enumerated_list(self, node):
        self.list_counter.append(LIST_TYPES.ENUMERATED)

    def depart_enumerated_list(self, node):
        self.list_counter.pop()
        self.new_state(0)
        self.add_text('')
        self.end_state()

    def visit_definition_list(self, node):
        self.list_counter.append(LIST_TYPES.DEFINITION)

    def depart_definition_list(self, node):
        self.list_counter.pop()
        self.new_state(0)
        self.add_text('')
        self.end_state()

    def visit_list_item(self, node):
        if self.list_counter[-1] == LIST_TYPES.BULLET:
            self.new_state(self.indent)
        elif self.list_counter[-1] == LIST_TYPES.DEFINITION:
            pass
        else:
            # enumerated list
            self.list_counter[-1] += 1
            self.new_state(len(str(self.list_counter[-1])) + self.indent)

    def depart_list_item(self, node):
        if self.list_counter[-1] == LIST_TYPES.BULLET:
            # bullet
            self.end_state(first='* ', end=None)
        elif self.list_counter[-1] == -2:
            # definition list
            pass
        else:
            # enumerated list
            self.end_state(first='# ', end=None)

    def visit_definition_list_item(self, node):
        self._li_has_classifier = len(node) >= 2 and \
                                  isinstance(node[1], nodes.classifier)

    def depart_definition_list_item(self, node):
        pass

    def visit_term(self, node):
        self.new_state(0)

    def depart_term(self, node):
        if not self._li_has_classifier:
            self.end_state(end=None)

    def visit_termsep(self, node):
        self.add_text(', ')
        raise nodes.SkipNode

    def visit_classifier(self, node):
        self.add_text(' : ')

    def depart_classifier(self, node):
        self.end_state(end=None)

    def visit_definition(self, node):
        self.new_state(self.indent)

    def depart_definition(self, node):
        self.end_state()

    def visit_field_list(self, node):
        pass

    def depart_field_list(self, node):
        pass

    def visit_field(self, node):
        self.new_state(0)

    def depart_field(self, node):
        self.end_state(end=None)

    def visit_field_name(self, node):
        self.add_text(':')

    def depart_field_name(self, node):
        self.add_text(':')
        content = node.astext()
        self.add_text((16-len(content))*' ')

    def visit_field_body(self, node):
        self.new_state(self.indent)

    def depart_field_body(self, node):
        self.end_state()

    def visit_centered(self, node):
        pass

    def depart_centered(self, node):
        pass

    def visit_hlist(self, node):
        pass

    def depart_hlist(self, node):
        pass

    def visit_hlistcol(self, node):
        pass

    def depart_hlistcol(self, node):
        pass

    def visit_admonition(self, node):
        self.new_state(0)

    def depart_admonition(self, node):
        self.end_state()

    def _visit_info(self, node):
        self.new_state(0)
        self.add_text('{info}')

    def _depart_info(self, node):
        self.add_text('{info}')
        self.end_state()

    def _visit_note(self, node):
        self.new_state(0)
        self.add_text('{note}')

    def _depart_note(self, node):
        self.add_text('{note}')
        self.end_state()

    def _visit_tip(self, node):
        self.new_state(0)
        self.add_text('{tip}')

    def _depart_tip(self, node):
        self.add_text('{tip}')
        self.end_state()

    def _visit_warning(self, node):
        self.new_state(0)
        self.add_text('{warning}')

    def _depart_warning(self, node):
        self.add_text('{warning}')
        self.end_state()

    visit_attention = _visit_note
    depart_attention = _depart_note
    visit_caution = _visit_warning
    depart_caution = _depart_warning
    visit_danger = _visit_warning
    depart_danger = _depart_warning
    visit_error = _visit_warning
    depart_error = _depart_warning
    visit_hint = _visit_tip
    depart_hint = _depart_tip
    visit_important = _visit_warning
    depart_important = _depart_warning
    visit_note = _visit_info
    depart_note = _depart_info
    visit_tip = _visit_tip
    depart_tip = _depart_tip
    visit_warning = _visit_warning
    depart_warning = _depart_warning

    def visit_versionmodified(self, node):
        self.new_state(0)
        if node.children:
            self.add_text(versionlabels[node['type']] % node['version'] + ': ')
        else:
            self.add_text(versionlabels[node['type']] % node['version'] + '.')

    def depart_versionmodified(self, node):
        self.end_state()

    def visit_literal_block(self, node):
        lang = node.get('language', '')
        if lang in LANG_MAP.keys():
            lang = LANG_MAP[lang]
        self.add_text('{code:title=|theme=Default|linenumbers=false|language=%s|collapse=false}' % lang)
        self.new_state(0)

    def depart_literal_block(self, node):
        self.add_text('{code}')
        self.end_state()

    def visit_doctest_block(self, node):
        self.new_state(0)

    def depart_doctest_block(self, node):
        self.end_state()

    def visit_line_block(self, node):
        pass

    def depart_line_block(self, node):
        self.add_text(self.nl)

    def visit_line(self, node):
        self.escape_newlines += 1

    def depart_line(self, node):
        self.escape_newlines -= 1

    def visit_block_quote(self, node):
        self.quote_level += 1
        if not self.builder.config.confluence_experimental_indentation:
            self.new_state(self.indent)

    def depart_block_quote(self, node):
        self.quote_level -= 1
        if not self.builder.config.confluence_experimental_indentation:
            self.end_state()

    def visit_compact_paragraph(self, node):
        pass

    def depart_compact_paragraph(self, node):
        pass

    def visit_paragraph(self, node):
        if not isinstance(node.parent, nodes.Admonition) or \
               isinstance(node.parent, addnodes.seealso):
            self.new_state(0)

    def depart_paragraph(self, node):
        # Don't put line breaks between list items
        if isinstance(node.parent, nodes.list_item):
            self.end_state(end=None)
        elif not isinstance(node.parent, (nodes.Admonition,
                                          addnodes.seealso)):
            self.end_state()

    def visit_target(self, node):
        if 'refid' in node:
            if self.can_anchor:
                self.add_text('{anchor:' + node['refid'] + '}')
            else:
                ConfluenceLogger.warn("anchor macro restricted; cannot create "
                        "link anchor (%s): %s" % (self.docname, node['refid']))

    def depart_target(self, node):
        pass

    def visit_index(self, node):
        raise nodes.SkipNode

    def visit_substitution_definition(self, node):
        raise nodes.SkipNode

    def visit_pending_xref(self, node):
        pass

    def depart_pending_xref(self, node):
        pass

    def visit_reference(self, node):
        # External link.
        if not 'internal' in node:
            if 'name' in node:
                self.add_text('[%s|%s]' % (node['name'], node['refuri']))
            else:
                self.add_text('[%s]' % (node['refuri']))
            raise nodes.SkipNode

        # Internal link.
        if 'refuri' in node:
            if '#' in node['refuri']:
                anchor = '#' + node['refuri'].split('#')[1]
            else:
                anchor = ''

            docname = self.docparent + path.splitext(node['refuri'])[0]
            doctitle = ConfluenceDocMap.title(docname)

            if doctitle:
                label = node.astext()
                if label == doctitle and not anchor:
                    self.add_text('[%s]' % label)
                else:
                    self.add_text('[%s|%s%s]' % (label, doctitle, anchor))
            else:
                self.builder.warn("unable to build link to document due to "
                    "missing title (in %s): %s" % (self.docname, docname))
            raise nodes.SkipNode

        # Anchor.
        if 'refid' in node:
            anchor = ''.join(node['refid'].split())
            self.add_text('[%s|#%s]' % (node.astext(), anchor))
            raise nodes.SkipNode

    def depart_reference(self, node):
        pass

    def visit_download_reference(self, node):
        self.log_unknown("download_reference", node)
        pass

    def depart_download_reference(self, node):
        pass

    def visit_emphasis(self, node):
        self.add_text('_')

    def depart_emphasis(self, node):
        self.add_text('_')

    def visit_literal_emphasis(self, node):
        self.add_text('_')

    def depart_literal_emphasis(self, node):
        self.add_text('_')

    def visit_strong(self, node):
        self.add_text('*')

    def depart_strong(self, node):
        self.add_text('*')

    def visit_abbreviation(self, node):
        self.add_text('')

    def depart_abbreviation(self, node):
        if node.hasattr('explanation'):
            self.add_text(' (%s)' % node['explanation'])

    def visit_title_reference(self, node):
        self.add_text('*')

    def depart_title_reference(self, node):
        self.add_text('*')

    def visit_literal(self, node):
        self.add_text('{{')

    def depart_literal(self, node):
        self.add_text('}}')

    def visit_subscript(self, node):
        self.add_text('_')

    def depart_subscript(self, node):
        pass

    def visit_superscript(self, node):
        self.add_text('^')

    def depart_superscript(self, node):
        pass

    def visit_footnote_reference(self, node):
        self.add_text('[%s]' % node.astext())
        raise nodes.SkipNode

    def visit_citation_reference(self, node):
        self.add_text('[%s]' % node.astext())
        raise nodes.SkipNode

    def visit_Text(self, node):
        conf = self.builder.config

        s = ''
        if conf.confluence_experimental_indentation:
            for i in range(self.quote_level):
                s += EXPERIMENTAL_QUOTE_KEYWORD
        s += node.astext()

        if self.escape_newlines or not conf.confluence_adv_strict_line_breaks:
            s = s.replace(self.nl, ' ')

        self.add_text(s)

    def depart_Text(self, node):
        pass

    def visit_generated(self, node):
        pass

    def depart_generated(self, node):
        pass

    def visit_inline(self, node):
        pass

    def depart_inline(self, node):
        pass

    def visit_problematic(self, node):
        self.add_text('>>')

    def depart_problematic(self, node):
        self.add_text('<<')

    def visit_system_message(self, node):
        self.new_state(0)
        self.add_text('<SYSTEM MESSAGE: %s>' % node.astext())
        self.end_state()
        raise nodes.SkipNode

    def visit_comment(self, node):
        raise nodes.SkipNode

    def visit_meta(self, node):
        # only valid for HTML
        raise nodes.SkipNode

    def visit_raw(self, node):
        if 'text' in node.get('format', '').split():
            self.body = self.body + node.astext()
        raise nodes.SkipNode

    def unknown_visit(self, node):
        raise NotImplementedError('Unknown node: ' + node.__class__.__name__)
