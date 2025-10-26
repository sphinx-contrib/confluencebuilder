# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)
# Copyright 2024 by the Sphinx team (sphinx-doc/sphinx#AUTHORS)

from docutils import nodes
from sphinx.domains.std import StandardDomain
from sphinx.ext.autodoc import cut_lines
from sphinx.roles import XRefRole
from sphinx.transforms.post_transforms import SphinxPostTransform
from sphinx.util.docfields import GroupedField
import sphinxcontrib.confluencebuilder
import sys

project = 'Sphinx Confluence Builder'
copyright = '2025 Sphinx Confluence Builder Contributors'
author = 'Sphinx Confluence Builder Contributors'
version = sphinxcontrib.confluencebuilder.__version__
release = sphinxcontrib.confluencebuilder.__version__

supported_confluence_ver = '8.5+'
supported_python_ver = '3.9+'
supported_requests_ver = '2.25.0+'
supported_sphinx_ver = '7.3+'

root_doc = 'contents'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
]

if any('spelling' in arg for arg in sys.argv):
    extensions.append('sphinxcontrib.spelling')
    spelling_exclude_patterns = ['changelog.rst']
    spelling_word_list_filename = '.spelling'

# reStructuredText string included at the end of every source
rst_epilog = f'''
.. |supported_confluence_ver| replace:: {supported_confluence_ver}
.. |supported_python_ver| replace:: {supported_python_ver}
.. |supported_requests_ver| replace:: {supported_requests_ver}
.. |supported_sphinx_ver| replace:: {supported_sphinx_ver}
'''

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = [
    '_build',
    '.DS_Store',
    'Thumbs.db',
]

suppress_warnings = [
    # Ignore excluded documents on toctrees (expected for LaTeX custom docs).
    'toc.excluded',
]

add_module_names = False

# -- Options for HTML output ----------------------------------------------

html_theme = 'sphinx13b'
html_theme_path = ['_themes']
templates_path = ['_templates']

html_static_path = ['_static']

html_additional_pages = {
    'index': 'index.html',
}

html_sidebars = {
    'index': [
        'indexsidebar.html',
        'searchbox.html',
        'ethical-ads.html',
    ],
}

html_context = {
    'supported_confluence_ver': supported_confluence_ver,
    'supported_python_ver': supported_python_ver,
    'supported_sphinx_ver': supported_sphinx_ver,
}

# -- Options for Latex output --------------------------------------------

latex_elements = {
    # explicit verbatim spacing (looks better?)
    'sphinxsetup': r'''
        verbatimsep=0.75em,
    ''',
    # remove empty pages
    'extraclassoptions': 'openany,oneside',
    # custom title
    'maketitle': r'''
\begin{titlepage}
    \vspace*{\stretch{1.2}}
    \sphinxlogo
    \vspace*{\stretch{1.0}}
    \begin{center}
        \large Provided by Sphinx Confluence Builder Contributors
        \par
        \DTMsetdatestyle{iso}
        \DTMtoday
        \par
        ''' + release + r'''
    \end{center}
    \vspace*{\stretch{1.0}}
\end{titlepage}
    ''',
    # iso datetime support
    # disable hyphenation
    # disable justified text
    # remove italics from links
    # new page for each section
    # minimize spacing between admonitions
    'preamble': r'''
        \usepackage{datetime2}
        \usepackage[none]{hyphenat}
        \usepackage[document]{ragged2e}
        \def\sphinxcrossref#1{#1}
        \newcommand{\sectionbreak}{\newpage}
        \NewDocumentEnvironment{ScbShrinkAdmonition}{O{}}
            {\vspace{-.6\baselineskip}}{\vspace{-.6\baselineskip}}
        \BeforeBeginEnvironment{sphinxadmonition}{\begin{ScbShrinkAdmonition}}
        \AfterEndEnvironment{sphinxadmonition}{\end{ScbShrinkAdmonition}}
    ''',
}

latex_logo = '_static/logo.png'

# -- Application hook -----------------------------------------------------


class DocumentationPostTransform(SphinxPostTransform):
    default_priority = 400

    def run(self, **kwargs):
        for node in self.document.traverse(nodes.reference):
            # tag references with `literal` child with a `literal-link` class
            # (to suppress hover styling)
            if isinstance(next(iter(node.children), None), nodes.literal):
                classes = node.get('classes', [])
                classes.append('literal-link')


class LiteralReferenceRole(XRefRole):
    def __init__(self):
        super().__init__(
            # mimic options for standard domain's xref
            lowercase=True, innernodeclass=nodes.inline, warn_dangling=True)

    def result_nodes(self, document, env, node, is_ref):
        # force custom domain so we can manipulate resolved nodes
        node['refdomain'] = 'cb-doc-modifiers'

        # force our custom reference role to be a `ref` type to resolve
        # it as any other standard reference
        node['reftype'] = 'ref'

        # force explicit -- for some reason non-explicit references are
        # not resolved (limitations of this hack)
        node['refexplicit'] = True

        return [node], []


class ConfluenceBuilderModifiersDomain(StandardDomain):
    name = 'cb-doc-modifiers'
    label = 'confluencebuilder (modifiers)'

    def resolve_xref(self,
            env, fromdocname, builder, typ, target, node, contnode):
        resolved = super().resolve_xref(
            env, fromdocname, builder, typ, target, node, contnode)

        if resolved:
            # build a literal node and wrap the inner node before returning
            # the resolved reference
            inner_node = resolved.next_node()
            container_node = nodes.literal('', '', inner_node)
            resolved.replace(inner_node, container_node)

        return resolved


def setup(app):
    app.require_sphinx('6.0')

    app.connect('builder-inited', builder_inited)

    app.add_js_file('jquery-3.6.3.min.js')
    app.add_js_file('version-alert.js')

    # remove first line description docstrings in documentation
    app.connect('autodoc-process-docstring', cut_lines(1))

    # add a custom "literal reference" which allow us to create page-to-page
    # references that are styled in literal tags
    app.add_domain(ConfluenceBuilderModifiersDomain)
    app.add_role('lref', LiteralReferenceRole())

    # custom directives/roles for documentation
    fdesc = GroupedField(
        'parameter', label='Parameters', names=['param'], can_collapse=True)

    app.add_object_type('builderval', 'builderval', objname='builders',
        indextemplate='pair: %s; Builder')
    app.add_object_type('confval', 'confval', objname='configuration value',
        indextemplate='pair: %s; Configuration value')
    app.add_object_type('event', 'event', objname='events',
        indextemplate='pair: %s; Event', doc_field_types=[fdesc])

    # register post-transformation hook for additional tweaks
    app.add_post_transform(DocumentationPostTransform)


def builder_inited(app):
    # "introduction.rst" document is for latex (PDF) only
    if app.builder.name != 'latex':
        app.config.exclude_patterns.extend([
            'introduction.rst',
        ])
