# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from docutils import nodes
from docutils.nodes import NodeVisitor as BaseTranslator
from pathlib import Path
from sphinx.util.images import get_image_size
from sphinx.util.images import guess_mimetype
from sphinx.util.osutil import SEP
from sphinx.util.osutil import canon_path
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger
from sphinxcontrib.confluencebuilder.std.sphinx import DEFAULT_ALIGNMENT
from sphinxcontrib.confluencebuilder.std.sphinx import DEFAULT_HIGHLIGHT_STYLE
from sphinxcontrib.confluencebuilder.svg import confluence_supported_svg
from sphinxcontrib.confluencebuilder.util import convert_length
from sphinxcontrib.confluencebuilder.util import extract_length
from sphinxcontrib.confluencebuilder.util import remove_nonspace_control_chars
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
        self.state = builder.state
        self.verbose = ConfluenceLogger.verbose
        self.warn = ConfluenceLogger.warn
        config = builder.config

        # acquire the active document name from the builder
        assert 'source' in document
        self.docname = canon_path(self.builder.env.path2doc(document['source']))

        # determine the active document's parent path to assist it title mapping
        # for relative document uris
        # (see '_visit_reference_intern_uri')
        if SEP in self.docname:
            docparent = self.docname[0 : self.docname.rfind(SEP) + 1]
        else:
            docparent = ''
        self.docparent = Path(docparent)

        self.assets = builder.assets
        self.body = []
        self.context = []
        self.nl = '\n'
        self._docnames = [self.docname]
        self._literal = False
        self._section_level = 1
        self._topic = False

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
        self.body_final = ''

        # prepend header (if any)
        if self.builder.config.confluence_header_file is not None:
            header_template_data = ''
            header_file = Path(self.builder.env.srcdir,
                self.builder.config.confluence_header_file)
            try:
                with header_file.open(encoding='utf-8') as file:
                    header_template_data = file.read()
            except OSError as err:
                self.warn(f'error reading file {header_file}: {err}')

            # if no data is supplied, the file is plain text
            if self.builder.config.confluence_header_data is None:
                header = header_template_data
            else:
                header = self.builder.templates.render_string(
                    header_template_data,
                    self.builder.config.confluence_header_data)

            self.body_final += header + self.nl

        self.body_final += self.pre_body_data()
        self.body_final += ''.join(self.body)
        self.body_final += self.post_body_data()

        # append footer (if any)
        if self.builder.config.confluence_footer_file is not None:
            footer_template_data = ''
            footer_file = Path(self.builder.env.srcdir,
                self.builder.config.confluence_footer_file)
            try:
                with footer_file.open(encoding='utf-8') as file:
                    footer_template_data = file.read()
            except OSError as err:
                self.warn(f'error reading file {footer_file}: {err}')

            # if no data is supplied, the file is plain text
            if self.builder.config.confluence_footer_data is None:
                footer = footer_template_data
            else:
                footer = self.builder.templates.render_string(
                    footer_template_data,
                    self.builder.config.confluence_footer_data)

            self.body_final += footer + self.nl

    def pre_body_data(self):
        return ''

    def post_body_data(self):
        return ''

    def visit_Text(self, node):
        text = node.astext()
        if not self._literal:
            text = text.replace(self.nl, ' ')
        text = self.encode(text)
        self.body.append(text)
        raise nodes.SkipNode

    def unknown_visit(self, node):
        node_name = node.__class__.__name__
        ignore_nodes = self.builder.config.confluence_adv_ignore_nodes
        if node_name in ignore_nodes:
            self.verbose(f'ignore node {node_name} (conf)')
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

        if node.source:
            lpf = f'#{node.line}' if node.line else ''
            self.warn(f'unknown node {node_name}: {node.source}{lpf}')
        else:
            self.warn(f'unknown node {node_name}: {self.docname}')

        raise nodes.SkipNode

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

    def visit_topic(self, node):
        self._topic = True
        self.visit_section(node)

    def depart_topic(self, node):
        self.depart_section(node)
        self._topic = False

    # -------------
    # images markup
    # -------------

    def visit_image(self, node):
        if 'uri' not in node or not node['uri']:
            self.verbose('skipping image with no uri')
            raise nodes.SkipNode

        uri = node['uri']
        uri = self.encode(uri)

        dochost = None
        img_key = None
        img_sz = None
        internal_img = uri.find('://') == -1 and not uri.startswith('data:')
        is_svg = uri.startswith('data:image/svg+xml') or \
            guess_mimetype(uri) == 'image/svg+xml'

        if internal_img:
            asset_docname = None
            if 'single' in self.builder.name:
                asset_docname = self.docname

            img_key, dochost, img_path = \
                self.assets.fetch(node, docname=asset_docname)

            # if this image has not already be processed (injected at a later
            # stage in the sphinx process); try processing it now
            if not img_key:
                # if this is an svg image, additional processing may also needed
                if is_svg:
                    confluence_supported_svg(self.builder, node)

                if not asset_docname:
                    asset_docname = self.docname

                img_key, dochost, img_path = \
                    self.assets.process_image_node(
                        node, asset_docname, standalone=True)

            if not img_key:
                self.warn('unable to find image: ' + uri)
                raise nodes.SkipNode

        # extract height, width and scale values on this image
        height, hu = extract_length(node.get('height'))
        scale = node.get('scale')
        width, wu = extract_length(node.get('width'))

        # if a scale value is provided and a height/width is not set, attempt to
        # determine the size of the image so that we can apply a scale value on
        # the detected size values
        if scale and not height and not width:
            if internal_img:
                img_sz = get_image_size(img_path)
                if img_sz is None:
                    self.warn('could not obtain image size; :scale: option is '
                        'ignored for ' + img_path)
                else:
                    width = img_sz[0]
                    wu = 'px'
            else:
                self.warn('cannot not obtain image size for external image; '
                    ':scale: option is ignored for ' + node['uri'])

        # apply scale factor to height/width fields
        if scale:
            if height:
                height = int(round(float(height) * scale / 100))
            if width:
                width = int(round(float(width) * scale / 100))

        # confluence only supports pixel sizes and percentage sizes in select
        # cases (e.g. applying a percentage width for an attached image can
        # result in an macro render error) -- adjust any other unit type (if
        # possible) to an acceptable pixel/percentage length
        if height:
            height = convert_length(height, hu)
            if height is None:
                self.warn('unsupported unit type for confluence: ' + hu)
        if width:
            width = convert_length(width, wu)
            if width is None:
                self.warn('unsupported unit type for confluence: ' + wu)

        # disable height/width entries for attached svgs as using these
        # attributes can result in a "broken image" rendering; instead, we will
        # track any desired height/width entry and inject them when publishing
        if internal_img and is_svg and (height or width):
            height = None
            hu = None
            width = None
            wu = None

        # [sphinx-gallery] create "thumbnail" images for sphinx-gallery
        #
        # If a sphinx-gallery-specific class type is detected for an image,
        # assume there is a desire for thumbnail-like images. Images are then
        # restricted with a specific height (a pattern observed when restricting
        # images to a smaller size with a Confluence editor). Although, if the
        # detected image size is smaller than our target, ignore any forced size
        # changes.
        if height is None and width is None and internal_img and not is_svg:
            if 'sphx-glr-multi-img' in node.get('class', []):
                if not img_sz:
                    img_sz = get_image_size(img_path)

                if not img_sz or img_sz[1] > 250:
                    height = '250'
                    hu = 'px'

        # forward image options
        opts = {}
        opts['dochost'] = dochost
        opts['height'] = height
        opts['hu'] = hu
        opts['key'] = img_key
        opts['width'] = width
        opts['wu'] = wu

        self._visit_image(node, opts)

    def _visit_image(self, node, opts):
        # ignore unless overwritten by derived translator
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

    def visit_meta(self, node):
        raise nodes.SkipNode

    def visit_line(self, node):
        # ignoring; no need to handle specific line entries
        pass

    def depart_line(self, node):
        pass

    def visit_number_reference(self, node):
        self.visit_reference(node)

    def depart_number_reference(self, node):
        self.depart_reference(node)

    def visit_raw(self, node):
        if 'confluence' in node.get('format', '').split():
            if not self._tracked_deprecated_raw_type:
                self._tracked_deprecated_raw_type = True
                self.warn('the raw "confluence" type is deprecated; '
                    'use "confluence_storage" instead')

            self.body.append(self.nl.join(node.astext().splitlines()))
        raise nodes.SkipNode

    def visit_reference(self, node):
        pass

    def depart_reference(self, node):
        pass

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

    def encode(self, text):
        # remove any non-space control characters that cannot be published to a
        # confluence instance
        return remove_nonspace_control_chars(text)

    # ##########################################################################
    # #                                                                        #
    # # helpers                                                                #
    # #                                                                        #
    # ##########################################################################

    def _fetch_alignment(self, node):
        """
        fetch the alignment to be used on a node

        A helper used to determine the recommended alignment value to apply
        for a given node. It will determine the alignment based off an explicit
        alignment hint provided on a node, or default the alignment based off
        its node type or the running configuration state.

        Args:
            node: the node

        Returns:
            the alignment to configure; may be `None`
        """

        alignment = None

        if 'align' in node:
            alignment = node['align']

        # if the parent is a figure, either take the assigned alignment from the
        # figure node; otherwise, apply the default alignment for the node
        elif isinstance(node.parent, nodes.figure):
            if 'align' in node.parent:
                alignment = node.parent['align']

            if not alignment or alignment == 'default':
                alignment = self._default_alignment

        if alignment:
            alignment = self.encode(alignment)

        return alignment
