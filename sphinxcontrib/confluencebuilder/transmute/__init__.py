# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from docutils import nodes
from sphinx.util.math import wrap_displaymath
from sphinxcontrib.confluencebuilder.compat import docutils_findall as findall
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger
from sphinxcontrib.confluencebuilder.nodes import confluence_latex_block
from sphinxcontrib.confluencebuilder.nodes import confluence_latex_inline
from sphinxcontrib.confluencebuilder.nodes import confluence_mathjax_block
from sphinxcontrib.confluencebuilder.nodes import confluence_mathjax_inline
from sphinxcontrib.confluencebuilder.svg import confluence_supported_svg
from sphinxcontrib.confluencebuilder.svg import svg_initialize
from sphinxcontrib.confluencebuilder.transmute.ext_jupyter_sphinx import replace_jupyter_sphinx_nodes
from sphinxcontrib.confluencebuilder.transmute.ext_nbsphinx import replace_nbsphinx_nodes
from sphinxcontrib.confluencebuilder.transmute.ext_sphinx_diagrams import replace_sphinx_diagrams_nodes
from sphinxcontrib.confluencebuilder.transmute.ext_sphinx_gallery import replace_sphinx_gallery_nodes
from sphinxcontrib.confluencebuilder.transmute.ext_sphinx_toolbox import replace_sphinx_toolbox_nodes
from sphinxcontrib.confluencebuilder.transmute.ext_sphinxcontrib_mermaid import replace_sphinxcontrib_mermaid_nodes
import itertools

# load graphviz extension if available to handle node pre-processing
try:
    from sphinx.ext.graphviz import GraphvizError
    from sphinx.ext.graphviz import graphviz
    from sphinx.ext.graphviz import render_dot
    has_graphviz = True
except ImportError:
    has_graphviz = False

# load imgmath extension if available to handle math node pre-processing
try:
    from sphinx.ext import imgmath
    has_imgmath = True
except ImportError:
    has_imgmath = False

# load inheritance_diagram extension if available to handle node pre-processing
try:
    from sphinx.ext import inheritance_diagram
    has_inheritance_diagram = True
except ImportError:
    has_inheritance_diagram = False


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

    # replace math blocks with Confluence LaTeX blocks or raw MathJax content
    replace_math_blocks(builder, doctree)

    # --------------------------
    # sphinx external extensions
    # --------------------------

    replace_jupyter_sphinx_nodes(builder, doctree)

    replace_nbsphinx_nodes(builder, doctree)

    replace_sphinx_diagrams_nodes(builder, doctree)

    replace_sphinx_gallery_nodes(builder, doctree)

    replace_sphinx_toolbox_nodes(builder, doctree)

    replace_sphinxcontrib_mermaid_nodes(builder, doctree)

    # -------------------
    # post-transmute work
    # -------------------

    # replace Confluence LaTeX blocks with images (if configured/supported)
    prepare_math_images(builder, doctree)

    # re-work svg entries to support confluence
    prepare_svgs(builder, doctree)


def prepare_math_images(builder, doctree):
    """
    replace Confluence LaTeX blocks with images

    If configured and supported, Confluence LaTeX blocks can be replaced with
    images. This can help render LaTeX content on a Confluence instance that
    does not support a LaTeX macro. Math support will work on systems which
    have latex/dvipng installed.

    Args:
        builder: the builder
        doctree: the doctree to replace blocks on
    """

    # allow users to disabled implemented extension changes
    restricted = builder.config.confluence_adv_restricted
    if 'ext-imgmath' in restricted:
        return

    # disable automatic conversion of latex blocks to images if a latex
    # macro is configured
    if builder.config.confluence_latex_macro:
        return

    if not has_imgmath:
        return

    # convert Confluence LaTeX blocks into image blocks
    #
    # imgmath's render_math call expects a translator to be passed
    # in; mock a translator tied to our builder
    class MockTranslator:
        def __init__(self, builder):
            self.builder = builder
    mock_translator = MockTranslator(builder)

    math_image_ids = []

    for node in itertools.chain(findall(doctree, confluence_latex_inline),
            findall(doctree, confluence_latex_block)):
        try:
            mf, depth = imgmath.render_math(mock_translator, node.astext())
            if not mf:
                continue

            new_node = nodes.image(
                candidates={'?'},
                uri=str(builder.out_dir / mf),
                **node.attributes)

            if depth is not None:
                new_node['math_depth'] = depth

            node.replace_self(new_node)

            if builder.config.confluence_editor == 'v2':
                if 'ids' in new_node:
                    math_image_ids.extend(new_node['ids'])

        except imgmath.MathExtError as ex:
            ConfluenceLogger.warn(f'inline latex {node.astext()}: {ex}')

    # v2 editor will manually inject anchors in an image-managed
    # section to avoid a newline spacing between the anchor and
    # the image; keep track of ids for these images, and then
    # remove any targets with matching ids to prevent anchors from
    # being created
    for node in findall(doctree, nodes.target):
        if 'refid' in node and node['refid'] in math_image_ids:
            node.parent.remove(node)


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

    for node in findall(doctree, nodes.image):
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

    # allow users to disabled implemented extension changes
    restricted = builder.config.confluence_adv_restricted
    if 'ext-graphviz' in restricted:
        return

    if not has_graphviz:
        return

    # graphviz's render_dot call expects a translator to be passed in; mock a
    # translator tied to our builder
    class MockTranslator:
        def __init__(self, builder):
            self.builder = builder
    mock_translator = MockTranslator(builder)

    for node in findall(doctree, graphviz):
        node_code = node['code']
        try:
            _, out_filename = render_dot(mock_translator, node_code,
                node['options'], builder.graphviz_output_format, 'graphviz')
            if not out_filename:
                node.parent.remove(node)
                continue

            new_node = nodes.image(candidates={'?'}, uri=out_filename)
            if 'align' in node:
                new_node['align'] = node['align']
            node.replace_self(new_node)
        except GraphvizError as ex:
            ConfluenceLogger.warn(f'dot code {node_code}: {ex}')
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

    # allow users to disabled implemented extension changes
    restricted = builder.config.confluence_adv_restricted
    if 'ext-inheritance_diagram' in restricted:
        return

    if not has_graphviz or not has_inheritance_diagram:
        return

    # graphviz's render_dot call expects a translator to be passed in; mock
    # a translator tied to our builder
    class MockTranslator:
        def __init__(self, builder):
            self.builder = builder
    mock_translator = MockTranslator(builder)

    for node in findall(doctree, inheritance_diagram.inheritance_diagram):
        graph = node['graph']

        graph_hash = inheritance_diagram.get_graph_hash(node)
        name = f'inheritance{graph_hash}'

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
            ConfluenceLogger.warn(f'dot code {dotcode}: {exc}')
            node.parent.remove(node)


def replace_math_blocks(builder, doctree):
    """
    replace math blocks with Confluence LaTeX blocks

    Math blocks are pre-processed and replaced with Confluence LaTeX blocks.
    This is to help prepare nodes that can later be used for user-configured
    LaTeX macros, or help converting LaTeX blocks into images (if supported on
    the system).

    Args:
        builder: the builder
        doctree: the doctree to replace blocks on
    """

    # allow users to disabled implemented extension changes
    restricted = builder.config.confluence_adv_restricted
    if 'ext-math_blocks' in restricted:
        return

    # check if raw mathjax output is desired
    #
    # Note that this will only work in Confluence environments that included
    # support for rendering MathJax. This extension will only provide raw
    # page content that a page can use. Confluence Cloud may only support
    # adding MathJax scripts via a Marketplace addon. Cloud Data Center can
    # support loading a MathJax script, but can require HTML support or
    # registered some other means by a system administrator. This plugin
    # will not attempt to handle any of this; it will be up to the end user
    # to utilize this for their instance.
    mathjax_mode = builder.config.confluence_mathjax

    # convert math blocks into Confluence LaTeX blocks
    for node in itertools.chain(findall(doctree, nodes.math),
            findall(doctree, nodes.math_block)):

        inlined_math = isinstance(node, nodes.math)

        if not inlined_math:
            if node['nowrap']:
                latex = node.astext()
            else:
                latex = wrap_displaymath(node.astext(), None, numbering=False)

            if mathjax_mode:
                new_node_type = confluence_mathjax_block
            else:
                new_node_type = confluence_latex_block
        else:
            latex = node.astext()

            if mathjax_mode:
                new_node_type = confluence_mathjax_inline
            else:
                new_node_type = confluence_latex_inline

        if mathjax_mode:
            latex = '\\(' + node.astext() + '\\)'
        elif inlined_math:
            latex = '$' + node.astext() + '$'

        new_node = new_node_type(latex, latex, **node.attributes)
        new_node['from_math'] = True

        if not inlined_math:
            new_node['align'] = 'center'

        node.replace_self(new_node)
