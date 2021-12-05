# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from docutils import nodes
from os import path
from sphinx.util.math import wrap_displaymath
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger
from sphinxcontrib.confluencebuilder.svg import confluence_supported_svg
from sphinxcontrib.confluencebuilder.svg import svg_initialize
from sphinxcontrib.confluencebuilder.transmute.ext_sphinx_diagrams import replace_sphinx_diagrams_nodes
from sphinxcontrib.confluencebuilder.transmute.ext_sphinx_gallery import replace_sphinx_gallery_nodes
from sphinxcontrib.confluencebuilder.transmute.ext_sphinx_toolbox import replace_sphinx_toolbox_nodes
from sphinxcontrib.confluencebuilder.transmute.ext_sphinxcontrib_mermaid import replace_sphinxcontrib_mermaid_nodes

# load graphviz extension if available to handle node pre-processing
try:
    from sphinx.ext.graphviz import GraphvizError
    from sphinx.ext.graphviz import graphviz
    from sphinx.ext.graphviz import render_dot
except ImportError:
    graphviz = None

# load imgmath extension if available to handle math node pre-processing
try:
    from sphinx.ext import imgmath
    import itertools
except ImportError:
    imgmath = None

# load inheritance_diagram extension if available to handle node pre-processing
if graphviz:
    try:
        from sphinx.ext import inheritance_diagram
    except ImportError:
        inheritance_diagram = None


def doctree_transmute(builder, doctree):
    """
    replace nodes in a doctree with support node types

    This call can be used by a builder to replace various node types (typically,
    from extensions) into alternative node types which can be processed by this
    extension's translator(s).

    Args:
        builder: the builder
        doctree: the doctree to replace blocks on
    """

    # --------------------------
    # sphinx internal extensions
    # --------------------------

    # replace inheritance diagram with images
    # (always invoke before _replace_graphviz_nodes)
    replace_inheritance_diagram(builder, doctree)

    # replace graphviz nodes with images
    replace_graphviz_nodes(builder, doctree)

    # replace math blocks with images
    replace_math_blocks(builder, doctree)

    # --------------------------
    # sphinx external extensions
    # --------------------------

    replace_sphinx_diagrams_nodes(builder, doctree)

    replace_sphinx_gallery_nodes(builder, doctree)

    replace_sphinx_toolbox_nodes(builder, doctree)

    replace_sphinxcontrib_mermaid_nodes(builder, doctree)

    # -------------------
    # post-transmute work
    # -------------------

    # re-work svg entries to support confluence
    prepare_svgs(builder, doctree)


def prepare_svgs(builder, doctree):
    """
    process any svgs found in a doctree to work on confluence

    The following will process a doctree for any SVG images to ensure they are
    compatible with published on a Confluence instance. See
    `confluence_supported_svg` for more details.

    Args:
        builder: the builder
        doctree: the doctree to check for svgs
    """

    svg_initialize()

    for node in doctree.traverse(nodes.image):
        confluence_supported_svg(builder, node)


def replace_graphviz_nodes(builder, doctree):
    """
    replace graphviz nodes with images

    graphviz nodes are pre-processed and replaced with respective images in the
    processed documentation set. Typically, the node support from
    `sphinx.ext.graphviz` would be added to the builder; however, this extension
    renders graphs during the translation phase (which is not ideal for how
    assets are managed in this extension).

    Instead, this implementation just traverses for graphviz nodes, generates
    renderings and replaces the nodes with image nodes (which in turn will be
    handled by the existing image-based implementation).

    Args:
        builder: the builder
        doctree: the doctree to replace blocks on
    """

    if graphviz is None:
        return

    # graphviz's render_dot call expects a translator to be passed in; mock a
    # translator tied to our builder
    class MockTranslator:
        def __init__(self, builder):
            self.builder = builder
    mock_translator = MockTranslator(builder)

    for node in doctree.traverse(graphviz):
        try:
            _, out_filename = render_dot(mock_translator, node['code'],
                node['options'], builder.graphviz_output_format, 'graphviz')
            if not out_filename:
                node.parent.remove(node)
                continue

            new_node = nodes.image(candidates={'?'}, uri=out_filename)
            if 'align' in node:
                new_node['align'] = node['align']
            node.replace_self(new_node)
        except GraphvizError as exc:
            ConfluenceLogger.warn('dot code {}: {}'.format(node['code'], exc))
            node.parent.remove(node)


def replace_inheritance_diagram(builder, doctree):
    """
    replace inheritance diagrams with images

    Inheritance diagrams are pre-processed and replaced with respective images
    in the processed documentation set. Typically, the node support from
    `sphinx.ext.inheritance_diagram` would be added to the builder; however,
    this extension renders graphs during the translation phase (which is not
    ideal for how assets are managed in this extension).

    Instead, this implementation just traverses for inheritance diagrams,
    generates renderings and replaces the nodes with image nodes (which in turn
    will be handled by the existing image-based implementation).

    Note that the interactive image map is not handled in this implementation
    since Confluence does not support image maps (without external extensions).

    Args:
        builder: the builder
        doctree: the doctree to replace blocks on
    """

    if inheritance_diagram is None:
        return

    # graphviz's render_dot call expects a translator to be passed in; mock
    # a translator tied to our builder
    class MockTranslator:
        def __init__(self, builder):
            self.builder = builder
    mock_translator = MockTranslator(builder)

    for node in doctree.traverse(inheritance_diagram.inheritance_diagram):
        graph = node['graph']

        graph_hash = inheritance_diagram.get_graph_hash(node)
        name = 'inheritance%s' % graph_hash

        dotcode = graph.generate_dot(name, {}, env=builder.env)

        try:
            _, out_filename = render_dot(mock_translator, dotcode, {},
                builder.graphviz_output_format, 'inheritance')
            if not out_filename:
                node.parent.remove(node)
                continue

            new_node = nodes.image(candidates={'?'}, uri=out_filename)
            if 'align' in node:
                new_node['align'] = node['align']
            node.replace_self(new_node)
        except GraphvizError as exc:
            ConfluenceLogger.warn('dot code {}: {}'.format(dotcode, exc))
            node.parent.remove(node)


def replace_math_blocks(builder, doctree):
    """
    replace math blocks with images

    Math blocks are pre-processed and replaced with respective images in the
    list of documents to process. This is to help prepare additional images into
    the asset management for this extension. Math support will work on systems
    which have latex/dvipng installed.

    Args:
        builder: the builder
        doctree: the doctree to replace blocks on
    """

    if imgmath is None:
        return

    # imgmath's render_math call expects a translator to be passed
    # in; mock a translator tied to our builder
    class MockTranslator:
        def __init__(self, builder):
            self.builder = builder
    mock_translator = MockTranslator(builder)

    for node in itertools.chain(doctree.traverse(nodes.math),
            doctree.traverse(nodes.math_block)):
        try:
            if not isinstance(node, nodes.math):
                if node['nowrap']:
                    latex = node.astext()
                else:
                    latex = wrap_displaymath(node.astext(), None, False)
            else:
                latex = '$' + node.astext() + '$'

            mf, depth = imgmath.render_math(mock_translator, latex)
            if not mf:
                continue

            new_node = nodes.image(
                candidates={'?'},
                uri=path.join(builder.outdir, mf),
                **node.attributes)
            new_node['from_math'] = True
            if not isinstance(node, nodes.math):
                new_node['align'] = 'center'
            if depth is not None:
                new_node['math_depth'] = depth
            node.replace_self(new_node)
        except imgmath.MathExtError as exc:
            ConfluenceLogger.warn('inline latex {}: {}'.format(
                node.astext(), exc))
