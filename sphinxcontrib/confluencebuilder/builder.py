# -*- coding: utf-8 -*-
"""
    sphinxcontrib.confluencebuilder.builder
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2016-2017 by the contributors (see AUTHORS file).
    :license: BSD, see LICENSE.txt for details.
"""

from __future__ import (print_function, unicode_literals, absolute_import)
from .common import ConfluenceDocMap, ConfluenceLogger
from .exceptions import ConfluenceConfigurationError
from .publisher import ConfluencePublisher
from .writer import ConfluenceWriter
from docutils.io import StringOutput
from docutils import nodes
from sphinx import addnodes
from sphinx.builders import Builder
from sphinx.util.osutil import ensuredir, SEP
from sphinx.util.nodes import inline_all_toctrees
from sphinx.util.console import darkgreen
from os import path
from xmlrpc.client import Fault
import codecs
import numbers

# Clone of relative_uri() sphinx.util.osutil, with bug-fixes
# since the original code had a few errors.
# This was fixed in Sphinx 1.2b.
def relative_uri(base, to):
    """Return a relative URL from ``base`` to ``to``."""
    if to.startswith(SEP):
        return to
    b2 = base.split(SEP)
    t2 = to.split(SEP)
    # remove common segments (except the last segment)
    for x, y in zip(b2[:-1], t2[:-1]):
        if x != y:
            break
        b2.pop(0)
        t2.pop(0)
    if b2 == t2:
        # Special case: relative_uri('f/index.html','f/index.html')
        # returns '', not 'index.html'
        return ''
    if len(b2) == 1 and t2 == ['']:
        # Special case: relative_uri('f/index.html','f/') should
        # return './', not ''
        return '.' + SEP
    return ('..' + SEP) * (len(b2)-1) + SEP.join(t2)

class ConfluenceBuilder(Builder):
    current_docname = None
    name = 'confluence'
    format = 'confluence'
    file_suffix = '.conf'
    link_suffix = None  # defaults to file_suffix
    publisher = ConfluencePublisher()

    def init(self):
        self.writer = ConfluenceWriter(self)
        self.publisher.init(self.config)

        server_url = self.config.confluence_server_url
        if server_url and server_url.endswith('/'):
            self.config.confluence_server_url = server_url[:-1]

        if self.config.confluence_file_suffix is not None:
            self.file_suffix = self.config.confluence_file_suffix
        if self.config.confluence_link_suffix is not None:
            self.link_suffix = self.config.confluence_link_suffix
        elif self.link_suffix is None:
            self.link_suffix = self.file_suffix

        # Function to convert the docname to a reST file name.
        def file_transform(docname):
            return docname + self.file_suffix

        # Function to convert the docname to a relative URI.
        def link_transform(docname):
            return docname + self.link_suffix

        if self.config.confluence_file_transform is not None:
            self.file_transform = self.config.confluence_file_transform
        else:
            self.file_transform = file_transform
        if self.config.confluence_link_transform is not None:
            self.link_transform = self.config.confluence_link_transform
        else:
            self.link_transform = link_transform

        if self.config.confluence_publish:
            if not self.config.confluence_server_url:
                raise ConfluenceConfigurationError("""Confluence server URL """
                    """has not been set. Unable to publish.""")
            if not self.config.confluence_space_name:
                raise ConfluenceConfigurationError("""Confluence space key """
                    """has not been set. Unable to publish.""")
            if not self.config.confluence_server_user:
                if self.config.confluence_server_pass:
                    raise ConfluenceConfigurationError("""Confluence """
                        """username has not been set even though a password """
                        """has been set. Unable to publish.""")

            self.publish = True
            self.publisher.connect()
            self.parent_id = self.publisher.getBasePageId()
            self.legacy_pages = self.publisher.getDescendents(self.parent_id)
        else:
            self.publish = False
            self.parent_id = None
            self.legacy_pages = []

        if self.config.confluence_space_name is not None:
            self.space_name = self.config.confluence_space_name
        else:
            self.space_name = None

    def get_outdated_docs(self):
        """
        Return an iterable of input files that are outdated.
        """
        # This method is taken from TextBuilder.get_outdated_docs()
        # with minor changes to support :confval:`rst_file_transform`.
        for docname in self.env.found_docs:
            if docname not in self.env.all_docs:
                yield docname
                continue
            sourcename = path.join(self.env.srcdir, docname +
                                   self.file_suffix)
            targetname = path.join(self.outdir, self.file_transform(docname))
            print (sourcename, targetname)

            try:
                targetmtime = path.getmtime(targetname)
            except Exception:
                targetmtime = 0
            try:
                srcmtime = path.getmtime(sourcename)
                if srcmtime > targetmtime:
                    yield docname
            except EnvironmentError:
                # source doesn't exist anymore
                pass

    def get_target_uri(self, docname, typ=None):
        return self.link_transform(docname)

    def get_relative_uri(self, from_, to, typ=None):
        """
        Return a relative URI between two source filenames.
        """
        # This is slightly different from Builder.get_relative_uri,
        # as it contains a small bug (which was fixed in Sphinx 1.2).
        return relative_uri(self.get_target_uri(from_),
                            self.get_target_uri(to, typ))

    def process_tree_structure(self, docname, depth=0):
        register_parent = self.config.confluence_experimental_page_hierarchy
        register_depth = isinstance(self.config.confluence_experimental_max_depth, numbers.Number)

        if register_depth:
            ConfluenceDocMap.registerDepth(docname, depth)

        doctree = self.env.get_doctree(docname)
        for toctreenode in doctree.traverse(addnodes.toctree):
            for includefile in toctreenode['includefiles']:
                if register_parent:
                    ConfluenceDocMap.registerParent(includefile, docname)
                self.process_tree_structure(includefile, depth+1)

    def prepare_writing(self, docnames):
        if self.config.master_doc:
            self.process_tree_structure(self.config.master_doc)

        for doc in docnames:
            doctree = self.env.get_doctree(doc)

            # Find title for document.
            idx = doctree.first_child_matching_class(nodes.section)
            if idx is None or idx == -1:
                continue

            first_section = doctree[idx]
            idx = first_section.first_child_matching_class(nodes.title)
            if idx is None or idx == -1:
                continue

            doctitle = first_section[idx].astext()
            if not doctitle:
                continue

            first_section.remove(first_section[idx])

            doctitle = ConfluenceDocMap.registerTitle(doc, doctitle,
                self.config.confluence_publish_prefix)

            target_refs = []
            for node in doctree.traverse(nodes.target):
                if 'refid' in node:
                    target_refs.append(node['refid'])

            doc_used_names = {}
            for node in doctree.traverse(nodes.title):
                if isinstance(node.parent, nodes.section):
                    section_node = node.parent
                    if 'ids' in section_node:
                        target = ''.join(node.astext().split())
                        section_id = doc_used_names.get(target, 0)
                        doc_used_names[target] = section_id + 1
                        if section_id > 0:
                            target = '%s.%d' % (target, section_id)

                        for id in section_node['ids']:
                            if not id in target_refs:
                                id = '%s#%s' % (doc, id)
                            ConfluenceDocMap.registerTarget(id, target)

        ConfluenceDocMap.conflictCheck()

    def write_doc(self, docname, doctree):
        depth = ConfluenceDocMap.depth(docname)
        if isinstance(depth, numbers.Number) and depth is self.config.confluence_experimental_max_depth:
            ConfluenceLogger.verbose("inlining children of {}".format(docname))
            tree = self.env.get_doctree(docname)
            doctree = inline_all_toctrees(self, set(), docname, tree, darkgreen, [docname])
        elif isinstance(depth, numbers.Number) and depth > self.config.confluence_experimental_max_depth:
            ConfluenceLogger.verbose("\not writing doc: '{}' depth: {} > max_depth"
                                     .format(docname, depth))
            return

        self.current_docname = docname

        # This method is taken from TextBuilder.write_doc()
        # with minor changes to support :confval:`rst_file_transform`.
        destination = StringOutput(encoding='utf-8')

        self.writer.write(doctree, destination)
        outfilename = path.join(self.outdir, self.file_transform(docname))
        ensuredir(path.dirname(outfilename))
        try:
            f = codecs.open(outfilename, 'w', 'utf-8')
            try:
                f.write(self.writer.output)
            finally:
                f.close()
        except (IOError, OSError) as err:
            self.warn("error writing file %s: %s" % (outfilename, err))

        if self.publish:
            self.publish_doc(docname, self.writer.output)

    def publish_doc(self, docname, output):
        title = ConfluenceDocMap.title(docname)
        if not title:
            self.warn("skipping document with no title: %s" % docname)
            return

        parent = ConfluenceDocMap.parent(docname)
        parent_id = ConfluenceDocMap.id(parent)
        if not parent_id:
            parent_id = self.parent_id

        uploaded_id = self.publisher.storePage(title, output, parent_id)
        ConfluenceDocMap.registerID(docname, uploaded_id)

        if self.config.confluence_purge:
            if uploaded_id in self.legacy_pages:
                self.legacy_pages.remove(uploaded_id)

    def finish(self):
        if self.publish:
            if self.config.confluence_purge is True and self.legacy_pages:
                self.info('removing legacy pages... ', nonl=0)
                for legacy_page_id in self.legacy_pages:
                   self.publisher.removePage(legacy_page_id)
                self.info('done\n')

            self.publisher.disconnect()
