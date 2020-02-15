# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2020 by the contributors (see AUTHORS file).
    :copyright: Copyright 2007-2019 by the Sphinx team (sphinx-doc/sphinx#AUTHORS).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from .builder import ConfluenceBuilder
from .logger import ConfluenceLogger
from docutils import nodes
from docutils.io import StringOutput
from getpass import getpass
from sphinx.locale import __
from sphinx.util.console import darkgreen # pylint: disable=no-name-in-module
from sphinx.util.nodes import inline_all_toctrees

class SingleConfluenceBuilder(ConfluenceBuilder):
    name = 'singleconfluence'

    def __init__(self, app):
        super(SingleConfluenceBuilder, self).__init__(app)

    def fix_refuris(self, tree):
        #
        # fix refuris with double anchor
        #
        fname = self.config.master_doc + self.file_suffix

        for refnode in tree.traverse(nodes.reference):
            if 'refuri' not in refnode:
                continue

            refuri = refnode['refuri']
            hashindex = refuri.find('#')
            if hashindex < 0:
                continue

            hashindex = refuri.find('#', hashindex + 1)
            if hashindex >= 0:
                refnode['refuri'] = fname + refuri[hashindex:]

    def assemble_doctree(self):
        master = self.config.master_doc
        tree = self.env.get_doctree(master)
        tree = inline_all_toctrees(
            self, set(), master, tree, darkgreen, [master])
        tree['docname'] = master

        self.env.resolve_references(tree, master, self)
        self.fix_refuris(tree)

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

    def write(self, build_docnames, updated_docnames, method='update'):
        docnames = self.env.all_docs

        ConfluenceLogger.info(
            __('preparing documents for single confluence document'), nonl=0)
        self.prepare_writing(docnames)
        ConfluenceLogger.info(__('done'))

        ConfluenceLogger.info(
            __('assembling single confluence document'), nonl=0)
        doctree = self.assemble_doctree()
        self.env.toc_secnumbers = self.assemble_toc_secnumbers()
        self.env.toc_fignumbers = self.assemble_toc_fignumbers()
        ConfluenceLogger.info(__('done'))

        ConfluenceLogger.info(__('writing single confluence document'), nonl=0)
        self.write_doc_serialized(self.config.master_doc, doctree)
        self.write_doc(self.config.master_doc, doctree)
        ConfluenceLogger.info(__('done'))
