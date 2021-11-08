# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from docutils import nodes
from os import path
from sphinx import addnodes
from sphinx.util.math import wrap_displaymath
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger
from sphinxcontrib.confluencebuilder.nodes import confluence_expand
from sphinxcontrib.confluencebuilder.svg import confluence_supported_svg
from sphinxcontrib.confluencebuilder.svg import svg_initialize
from sphinxcontrib.confluencebuilder.util import first

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

# ##############################################################################
# disable import/except warnings for third-party modules
# pylint: disable=E

# load sphinx_toolbox extension if available to handle node pre-processing
try:
    from sphinx_toolbox.assets import AssetNode as sphinx_toolbox_AssetNode
    sphinx_toolbox_assets = True
except:  # noqa: E722
    sphinx_toolbox_assets = False

try:
    from sphinx_toolbox.collapse import CollapseNode as sphinx_toolbox_CollapseNode
    sphinx_toolbox_collapse = True
except:  # noqa: E722
    sphinx_toolbox_collapse = False

try:
    from sphinx_toolbox.github.issues import IssueNode as sphinx_toolbox_IssueNode
    from sphinx_toolbox.github.issues import IssueNodeWithName as sphinx_toolbox_IssueNodeWithName
    sphinx_toolbox_github_issues = True
except:  # noqa: E722
    sphinx_toolbox_github_issues = False

try:
    from sphinx_toolbox.github.repos_and_users import GitHubObjectLinkNode as sphinx_toolbox_GitHubObjectLinkNode
    sphinx_toolbox_github_repos_and_users = True
except:  # noqa: E722
    sphinx_toolbox_github_repos_and_users = False

# load sphinx-gallery extension if available
try:
    from sphinx_gallery.directives import imgsgnode as sphinx_gallery_imgsgnode
    sphinx_gallery = True
except:  # noqa: E722
    sphinx_gallery = False

# load sphinxcontrib-mermaid extension if available
try:
    from sphinxcontrib.mermaid import MermaidError
    from sphinxcontrib.mermaid import mermaid
    from sphinxcontrib.mermaid import render_mm as mermaid_render
    sphinxcontrib_mermaid = True
except:  # noqa: E722
    sphinxcontrib_mermaid = False

# re-enable pylint warnings from above
# pylint: enable=E
# ##############################################################################


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


def replace_sphinx_toolbox_nodes(builder, doctree):
    """
    replace sphinx_toolbox nodes with compatible node types

    Various sphinx_toolbox nodes are pre-processed and replaced with compatible
    node types for a given doctree.

    Args:
        builder: the builder
        doctree: the doctree to replace nodes on
    """

    # allow users to disabled third-party implemented extension changes
    restricted = builder.config.confluence_adv_restricted
    if 'ext-sphinx_toolbox' in restricted:
        return

    if sphinx_toolbox_assets:
        for node in doctree.traverse(sphinx_toolbox_AssetNode):
            # mock a docname based off the configured sphinx_toolbox's asset
            # directory; which the processing of a download_reference will
            # strip and use the asset directory has the container folder to find
            # the file in
            mock_docname = path.join(builder.config.assets_dir, 'mock')
            new_node = addnodes.download_reference(
                node.astext(),
                node.astext(),
                refdoc=mock_docname,
                refexplicit=True,
                reftarget=node['refuri'],
            )
            node.replace_self(new_node)

    if sphinx_toolbox_collapse:
        for node in doctree.traverse(sphinx_toolbox_CollapseNode):
            new_node = confluence_expand(node.rawsource, title=node.label,
                *node.children, **node.attributes)
            node.replace_self(new_node)

    if sphinx_toolbox_github_issues:
        # note: using while loop since replacing issue nodes has observed to
        #  cause an exception while docutils is processing a doctree
        while True:
            node = first(itertools.chain(
                doctree.traverse(sphinx_toolbox_IssueNode),
                doctree.traverse(sphinx_toolbox_IssueNodeWithName)))
            if not node:
                break

            if isinstance(node, sphinx_toolbox_IssueNodeWithName):
                title = '{}#{}'.format(node.repo_name, node.issue_number)
            else:
                title = '#{}'.format(node.issue_number)

            new_node = nodes.reference(title, title, refuri=node.issue_url)
            node.replace_self(new_node)

    if sphinx_toolbox_github_repos_and_users:
        for node in doctree.traverse(sphinx_toolbox_GitHubObjectLinkNode):
            new_node = nodes.reference(node.name, node.name, refuri=node.url)
            node.replace_self(new_node)


def replace_sphinx_gallery_nodes(builder, doctree):
    """
    replace sphinx-gallery nodes with images

    sphinx-gallery nodes are pre-processed and replaced with respective images
    in the processed documentation set.

    Args:
        builder: the builder
        doctree: the doctree to replace blocks on
    """

    # allow users to disabled third-party implemented extension changes
    restricted = builder.config.confluence_adv_restricted
    if 'ext-sphinx_gallery' in restricted:
        return

    if not sphinx_gallery:
        return

    for node in doctree.traverse(sphinx_gallery_imgsgnode):
        new_node = nodes.image(candidates={'?'}, **node.attributes)
        if 'align' in node:
            new_node['align'] = node['align']
        node.replace_self(new_node)


def replace_sphinxcontrib_mermaid_nodes(builder, doctree):
    """
    replace mermaid nodes with images

    mermaid nodes are pre-processed and replaced with respective images in the
    processed documentation set.

    Args:
        builder: the builder
        doctree: the doctree to replace blocks on
    """

    # allow users to disabled third-party implemented extension changes
    restricted = builder.config.confluence_adv_restricted
    if 'ext-sphinxcontrib.mermaid' in restricted:
        return

    if not sphinxcontrib_mermaid:
        return

    # mermaid's mermaid_render call expects a translator to be passed in; mock a
    # translator tied to our builder
    class MockTranslator:
        def __init__(self, builder):
            self.builder = builder
    mock_translator = MockTranslator(builder)

    for node in doctree.traverse(mermaid):
        try:
            format = builder.config.mermaid_output_format
            if format == 'raw':
                format = 'png'

            fname, _ = mermaid_render(mock_translator,
                node['code'], node['options'], format, 'mermaid')
            if not fname:
                node.parent.remove(node)
                continue

            new_node = nodes.image(candidates={'?'}, uri=fname)
            if 'align' in node:
                new_node['align'] = node['align']
            node.replace_self(new_node)
        except MermaidError as exc:
            ConfluenceLogger.warn('mermaid code %r: ' % node['code'] + str(exc))
            node.parent.remove(node)
