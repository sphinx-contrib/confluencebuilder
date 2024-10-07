# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)
# Copyright 2007-2019 by the Sphinx team (sphinx-doc/sphinx#AUTHORS)

from docutils import nodes
from sphinx.util.console import darkgreen  # pylint: disable=no-name-in-module
from sphinx.util.display import progress_message
from sphinxcontrib.confluencebuilder.builder import ConfluenceBuilder
from sphinxcontrib.confluencebuilder.compat import docutils_findall as findall
from sphinxcontrib.confluencebuilder.compat import inline_all_toctrees
from sphinxcontrib.confluencebuilder.locale import C
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger as logger


class SingleConfluenceBuilder(ConfluenceBuilder):
    name = 'singleconfluence'
    supported_linkcode = name

    def assemble_doctree(self):
        root_doc = self.config.root_doc
        tree = self.env.get_doctree(root_doc)
        tree = inline_all_toctrees(
            self, set(), root_doc, tree, darkgreen, [root_doc],
            replace=not self.config.singleconfluence_toctree)
        tree['docname'] = root_doc

        self.env.get_and_resolve_doctree(root_doc, self, doctree=tree)
        self._fix_refuris(tree)

        return tree

    def assemble_toc_secnumbers(self):
        new_secnumbers = {}

        for docname, secnums in self.env.toc_secnumbers.items():
            for id_, secnum in secnums.items():
                alias = f'{docname}/{id_}'
                new_secnumbers[alias] = secnum

        return {self.config.root_doc: new_secnumbers}

    def assemble_toc_fignumbers(self):
        new_fignumbers = {}

        for docname, fignumlist in self.env.toc_fignumbers.items():
            for figtype, fignums in fignumlist.items():
                alias = f'{docname}/{figtype}'
                new_fignumbers.setdefault(alias, {})

                for id_, fignum in fignums.items():
                    new_fignumbers[alias][id_] = fignum

        return {self.config.root_doc: new_fignumbers}

    def get_outdated_docs(self):
        return 'all documents'

    def get_relative_uri(self, from_, to, typ=None):
        return self.get_target_uri(to, typ)

    def get_target_uri(self, docname, typ=None):
        if docname in self.env.all_docs:
            return f'{self.config.root_doc}{self.link_suffix}#{docname}'

        return self.link_transform(docname)

    def write(self, build_docnames, updated_docnames, method='update'):
        docnames = self.env.all_docs
        if self.config.root_doc not in docnames:
            logger.error('singleconfluence requires root_doc')
            return

        root_doctitle = self._process_root_document()
        if not root_doctitle:
            logger.error('singleconfluence requires title on root_doc')
            return

        with progress_message(C('assembling single confluence document')):
            if self.app.verbosity:
                print()

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
            self.env.toc_secnumbers.setdefault(self.config.root_doc, {}).update(
                assembled_toc_secnumbers[self.config.root_doc])
            self.env.toc_fignumbers.setdefault(self.config.root_doc, {}).update(
                assembled_toc_fignumbers[self.config.root_doc])

            # register title targets for references before assembling doc
            # re-works them into a single document
            title_db = {}
            for docname in docnames:
                doctree = self.env.get_doctree(docname)
                self._register_doctree_targets(docname, doctree, title_db)

            doctree = self.assemble_doctree()
            self._prepare_doctree_writing(self.config.root_doc, doctree)
            self.assets.process_document(doctree, self.config.root_doc)

        with progress_message(C('writing single confluence document')):
            if self.app.verbosity:
                print()

            self.write_doc_serialized(self.config.root_doc, doctree)
            self.write_doc(self.config.root_doc, doctree)

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
        root_docuri = self.config.root_doc + self.file_suffix

        for refnode in findall(doctree, nodes.reference):
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
            elif refuri.startswith(root_docuri + '#'):
                refnode['refid'] = refuri[idx + 1:]
                del refnode['refuri']

    def _process_root_document(self):
        docname = self.config.root_doc

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
        self.state.register_title(docname, doctitle, self.config)

        # register the root document for publishing
        self.publish_docnames.append(docname)

        return doctitle

    def _top_ref_check(self, node):
        """
        report if the provided node is consider a #top reference

        Check if the provided reference node is a reference to the root
        document. If so, flag that it should be a "#top" reference instead of an
        internal anchor target.

        Args:
            node: the node to check

        Returns:
            whether or not the node should be a #top reference
        """
        return node['refid'] == self.config.root_doc
