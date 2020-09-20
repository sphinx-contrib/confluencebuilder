# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020 Sphinx Confluence Builder Contributors (AUTHORS)
:copyright: Copyright 2007-2019 by the Sphinx team (sphinx-doc/sphinx#AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from .builder import ConfluenceBuilder
from .compat import progress_message
from .logger import ConfluenceLogger
from .state import ConfluenceState
from docutils import nodes
from sphinx.locale import __
from sphinx.util.console import darkgreen # pylint: disable=no-name-in-module
from sphinx.util.nodes import inline_all_toctrees

class SingleConfluenceBuilder(ConfluenceBuilder):
    name = 'singleconfluence'

    def __init__(self, app):
        super(SingleConfluenceBuilder, self).__init__(app)

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
        #
        # Assemble toc_secnumbers to resolve section numbers on SingleHTML.
        # Merge all secnumbers to single secnumber.
        #
        # Note: current Sphinx has refid confliction in singlehtml mode.
        #       To avoid the problem, it replaces key of secnumbers to
        #       tuple of docname and refid.
        #
        #       There are related codes in inline_all_toctres() and
        #       HTMLTranslter#add_secnumber().
        #
        new_secnumbers = {}  # type: Dict[str, Tuple[int, ...]]

        for docname, secnums in self.env.toc_secnumbers.items():
            for id, secnum in secnums.items():
                alias = '{}/{}'.format(docname, id)
                new_secnumbers[alias] = secnum

        return {self.config.master_doc: new_secnumbers}

    def assemble_toc_fignumbers(self):
        #
        # Assemble toc_fignumbers to resolve figure numbers on SingleHTML.
        # Merge all fignumbers to single fignumber.
        #
        # Note: current Sphinx has refid confliction in singlehtml mode.
        #       To avoid the problem, it replaces key of secnumbers to
        #       tuple of docname and refid.
        #
        #       There are related codes in inline_all_toctres() and
        #       HTMLTranslter#add_fignumber().
        #
        new_fignumbers = {}  # type: Dict[str, Dict[str, Tuple[int, ...]]]

        #
        # {'foo': {'figure': {'id2': (2,), 'id1': (1,)}},
        #  'bar': {'figure': {'id1': (3,)}}}
        #
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
            doctree = self.assemble_doctree()
            self._prepare_doctree_writing(self.config.master_doc, doctree)

            self.env.toc_secnumbers = self.assemble_toc_secnumbers()
            self.env.toc_fignumbers = self.assemble_toc_fignumbers()

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
        ConfluenceState.registerTitle(docname, doctitle,
            self.config.confluence_publish_prefix,
            self.config.confluence_publish_postfix)

        # register the root document for publishing
        self.publish_docnames.append(docname)

        return doctitle
