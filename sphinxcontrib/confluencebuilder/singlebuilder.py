# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020 Sphinx Confluence Builder Contributors (AUTHORS)
:copyright: Copyright 2007-2019 by the Sphinx team (sphinx-doc/sphinx#AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from docutils import nodes
from sphinx.locale import __
from sphinx.util.console import darkgreen # pylint: disable=no-name-in-module
from sphinx.util.nodes import inline_all_toctrees
from sphinxcontrib.confluencebuilder.builder import ConfluenceBuilder
from sphinxcontrib.confluencebuilder.compat import progress_message
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger
from sphinxcontrib.confluencebuilder.state import ConfluenceState

class SingleConfluenceBuilder(ConfluenceBuilder):
    name = 'singleconfluence'

    def __init__(self, app):
        super(SingleConfluenceBuilder, self).__init__(app)

        self.root_doc = self.config.master_doc

    def assemble_doctree(self):
        master = self.config.master_doc
        tree = self.env.get_doctree(master)
        tree = inline_all_toctrees(
            self, set(), master, tree, darkgreen, [master])
        tree['docname'] = master

        self.env.resolve_references(tree, master, self)
        self._fix_refuris(tree)

        return tree

    def assemble_toc_secnumbers(self):
        new_secnumbers = {}

        for docname, secnums in self.env.toc_secnumbers.items():
            for id, secnum in secnums.items():
                alias = '{}/{}'.format(docname, id)
                new_secnumbers[alias] = secnum

        return {self.config.master_doc: new_secnumbers}

    def assemble_toc_fignumbers(self):
        new_fignumbers = {}

        for docname, fignumlist in self.env.toc_fignumbers.items():
            for figtype, fignums in fignumlist.items():
                alias = '{}/{}'.format(docname, figtype)
                new_fignumbers.setdefault(alias, {})

                for id, fignum in fignums.items():
                    new_fignumbers[alias][id] = fignum

        return {self.config.master_doc: new_fignumbers}

    def get_outdated_docs(self):
        return 'all documents'

    def get_relative_uri(self, from_, to, typ=None):
        return self.get_target_uri(to, typ)

    def get_target_uri(self, docname, typ=None):
        if docname in self.env.all_docs:
            return '{}{}#{}'.format(
                self.config.master_doc, self.link_suffix, docname)
        else:
            return self.link_transform(docname)

    def write(self, build_docnames, updated_docnames, method='update'):
        docnames = self.env.all_docs
        if self.config.master_doc not in docnames:
            ConfluenceLogger.error('singleconfluence required master_doc')
            return

        root_doctitle = self._process_root_document()
        if not root_doctitle:
            ConfluenceLogger.error(
                'singleconfluence required title on master_doc')
            return

        with progress_message(__('assembling single confluence document')):
            # assemble toc section/figure numbers
            #
            # Both the environment's `toc_secnumbers` and `toc_fignumbers`
            # are populated; however, they do not contain a complete list of
            # each document's section/figure numbers. The assembling process
            # will create a dictionary keys of '<docname>/<id>' which the writer
            # implementations can used to build desired references when invoked
            # with a `singleconfluence` builder. Unlike Sphinx's `singlehtml`
            # builder, this builder will update the existing number dictionaries
            # to hold the original mappings (for other post-transforms,
            # extensions, etc.) and the newer mappings for reference building.
            assembled_toc_secnumbers = self.assemble_toc_secnumbers()
            assembled_toc_fignumbers = self.assemble_toc_fignumbers()
            self.env.toc_secnumbers.setdefault(self.root_doc, {}).update(
                assembled_toc_secnumbers[self.root_doc])
            self.env.toc_fignumbers.setdefault(self.root_doc, {}).update(
                assembled_toc_fignumbers[self.root_doc])

            # register title targets for references before assembling doc
            # re-works them into a single document
            for docname in docnames:
                doctree = self.env.get_doctree(docname)
                self._register_doctree_title_targets(docname, doctree)

            doctree = self.assemble_doctree()
            self._prepare_doctree_writing(self.config.master_doc, doctree)
            self.assets.processDocument(doctree, self.config.master_doc)

        with progress_message(__('writing single confluence document')):
            self.write_doc_serialized(self.config.master_doc, doctree)
            self.write_doc(self.config.master_doc, doctree)

    def _fix_refuris(self, doctree):
        """
        process refuris that self-reference to the new toctree

        When assembling a new single doctree, references between pages now
        become references to specific targets on the single page. This call will
        correct two scenarios. If a reference's `refuri` references the newly
        generated page, replace the `refuri` with a `refid`. This allows a
        translator to easily process the reference to a local target (which it
        is) instead of treating it as a target on a possibly independent page.
        Second, this change also removes the possibly of double-anchors
        generated when combining into a single toctree. When inlining toctree's,
        parses may stack target identifiers in a `refuri`. If this occurs, only
        the last stacked target idenitifier is needed.

        Args:
            doctree: the doctree to parse
        """
        master_docuri = self.config.master_doc + self.file_suffix

        for refnode in doctree.traverse(nodes.reference):
            if 'refuri' not in refnode:
                continue

            refuri = refnode['refuri']
            idx = refuri.find('#')
            if idx < 0:
                continue

            idx2 = refuri.find('#', idx + 1)
            if idx2 >= 0:
                refnode['refid'] = refuri[idx2 + 1:]
                del refnode['refuri']
            elif refuri.startswith(master_docuri + '#'):
                refnode['refid'] = refuri[idx + 1:]
                del refnode['refuri']

    def _process_root_document(self):
        docname = self.config.master_doc

        # Extract the title from the root document as it will be used to decide
        # which Confluence page the document will be published to.
        if (self.config.confluence_title_overrides and
                docname in self.config.confluence_title_overrides):
            doctitle = self.config.confluence_title_overrides[docname]
        else:
            doctree = self.env.get_doctree(docname)
            doctitle = self._parse_doctree_title(docname, doctree)
            if not doctitle:
                return None

        # register the title for the root document (for references, assets, ...)
        ConfluenceState.registerTitle(docname, doctitle, self.config)

        # register the root document for publishing
        self.publish_docnames.append(docname)

        return doctitle

    def _register_doctree_title_targets(self, docname, doctree):
        """
        register title targets for a doctree

        Compiles a list of title targets which references can link against. This
        tracked expected targets for sections which are automatically generated
        in a rendered Confluence instance.

        Args:
            docname: the docname of the doctree
            doctree: the doctree to search for targets
        """

        doc_used_names = {}
        secnumbers = self.env.toc_secnumbers.get(self.config.master_doc, {})

        for node in doctree.traverse(nodes.title):
            if isinstance(node.parent, nodes.section):
                section_node = node.parent
                if 'ids' in section_node:
                    title_name = ''.join(node.astext().split())

                    for id in section_node['ids']:
                        target = title_name

                        anchorname = '%s/#%s' % (docname, id)
                        if anchorname not in secnumbers:
                            anchorname = '%s/' % id

                        if self.add_secnumbers:
                            secnumber = secnumbers.get(anchorname)
                            if secnumber:
                                target = ('.'.join(map(str, secnumber)) +
                                    self.secnumber_suffix + target)

                        section_id = doc_used_names.get(target, 0)
                        doc_used_names[target] = section_id + 1
                        if section_id > 0:
                            target = '{}.{}'.format(target, section_id)

                        ConfluenceState.registerTarget(anchorname, target)
