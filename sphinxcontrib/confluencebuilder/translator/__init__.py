# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from docutils import nodes
from docutils.nodes import NodeVisitor as BaseTranslator
from os import path
from sphinx.util.osutil import SEP
from sphinx.util.osutil import canon_path
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger
from sphinxcontrib.confluencebuilder.std.sphinx import DEFAULT_ALIGNMENT
from sphinxcontrib.confluencebuilder.std.sphinx import DEFAULT_HIGHLIGHT_STYLE
import io
import sys

class ConfluenceBaseTranslator(BaseTranslator):
    _tracked_deprecated_raw_type = False

    """
    confluence base extension translator

    Base translator for the Confluence extension for Sphinx. This contains
    common implementation shared by other translators in this extension which
    can help process individual documents based on parsed node entries provided
    by docutils (used by Sphinx).

    Args:
        document: the document being translated
        builder: the sphinx builder instance
    """
    def __init__(self, document, builder):
        BaseTranslator.__init__(self, document)
        self.builder = builder
        self.warn = document.reporter.warning
        config = builder.config

        # acquire the active document name from the builder
        assert 'source' in document
        self.docname = canon_path(self.builder.env.path2doc(document['source']))

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
        self._docnames = [self.docname]
        self._literal = False
        self._section_level = 1

        if config.confluence_default_alignment:
            self._default_alignment = config.confluence_default_alignment
        else:
            self._default_alignment = DEFAULT_ALIGNMENT

        if config.highlight_language:
            self._highlight = config.highlight_language
        else:
            self._highlight = DEFAULT_HIGHLIGHT_STYLE
        self._linenothreshold = sys.maxsize

    # ##########################################################################
    # #                                                                        #
    # # base translator overrides                                              #
    # #                                                                        #
    # ##########################################################################

    def visit_document(self, node):
        pass

    def depart_document(self, node):
        self.document = ''

        # prepend header (if any)
        if self.builder.config.confluence_header_file is not None:
            headerFile = path.join(self.builder.env.srcdir,
                self.builder.config.confluence_header_file)
            try:
                with io.open(headerFile, encoding='utf-8') as file:
                    self.document += file.read() + self.nl
            except (IOError, OSError) as err:
                self.warn('error reading file {}: {}'.format(headerFile, err))

        self.document += ''.join(self.body)

        # append footer (if any)
        if self.builder.config.confluence_footer_file is not None:
            footerFile = path.join(self.builder.env.srcdir,
                self.builder.config.confluence_footer_file)
            try:
                with io.open(footerFile, encoding='utf-8') as file:
                    self.document += file.read() + self.nl
            except (IOError, OSError) as err:
                self.warn('error reading file {}: {}'.format(footerFile, err))

    def visit_Text(self, node):
        text = node.astext()
        if not self._literal:
            text = text.replace(self.nl, ' ')
        text = self._escape_text(text)
        self.body.append(text)
        raise nodes.SkipNode

    def unknown_visit(self, node):
        node_name = node.__class__.__name__
        ignore_nodes = self.builder.config.confluence_adv_ignore_nodes
        if node_name in ignore_nodes:
            ConfluenceLogger.verbose('ignore node {} (conf)'.format(node_name))
            raise nodes.SkipNode

        # allow users to override unknown nodes
        #
        # A node handler allows an advanced user to provide implementation to
        # process a node not supported by this extension. This is to assist in
        # providing a quick alternative to supporting another third party
        # extension in this translator (without having to take the time in
        # building a third extension).
        handler = self.builder.config.confluence_adv_node_handler
        if handler and isinstance(handler, dict) and node_name in handler:
            handler[node_name](self, node)
            raise nodes.SkipNode

        raise NotImplementedError('unknown node: ' + node_name)

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

    visit_topic = visit_section
    depart_topic = depart_section

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

    # --------------
    # sphinx -- math
    # --------------

    def visit_displaymath(self, node):
        # unsupported
        raise nodes.SkipNode

    def visit_eqref(self, node):
        # unsupported
        raise nodes.SkipNode

    def visit_math(self, node):
        # handled in "builder" at this time
        raise nodes.SkipNode

    def visit_math_block(self, node):
        # handled in "builder" at this time
        raise nodes.SkipNode

    # -----------------
    # sphinx -- toctree
    # -----------------

    def visit_toctree(self, node):
        # skip hidden toctree entries
        raise nodes.SkipNode

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

    def visit_acks(self, node):
        raise nodes.SkipNode

    def visit_comment(self, node):
        raise nodes.SkipNode

    def visit_line(self, node):
        # ignoring; no need to handle specific line entries
        pass

    def depart_line(self, node):
        pass

    def visit_raw(self, node):
        if 'confluence' in node.get('format', '').split():
            if not self._tracked_deprecated_raw_type:
                self._tracked_deprecated_raw_type = True
                self.warn('the raw "confluence" type is deprecated; '
                    'use "confluence_storage" instead')

            self.body.append(self.nl.join(node.astext().splitlines()))
        raise nodes.SkipNode

    def visit_sidebar(self, node):
        # unsupported
        raise nodes.SkipNode

    def visit_substitution_definition(self, node):
        raise nodes.SkipNode

    def visit_start_of_file(self, node):
        # track active inlined documents (singleconfluence builder) for anchors
        self._docnames.append(node['docname'])

    def depart_start_of_file(self, node):
        self._docnames.pop()

    # ##########################################################################
    # #                                                                        #
    # # virtual methods                                                        #
    # #                                                                        #
    # ##########################################################################

    def _escape_text(self, node):
        raise NotImplementedError('translator does not implement text escaping')
