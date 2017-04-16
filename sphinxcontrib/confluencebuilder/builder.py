# -*- coding: utf-8 -*-
"""
    sphinxcontrib.confluencebuilder.builder
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2016-2017 by the contributors (see AUTHORS file).
    :license: BSD, see LICENSE.txt for details.
"""

from __future__ import (print_function, unicode_literals, absolute_import)
from .common import ConfluenceDocMap
from .exceptions import ConfluenceConfigurationError
from .publisher import ConfluencePublisher
from .writer import ConfluenceWriter
from docutils.io import StringOutput
from docutils import nodes
from sphinx.builders import Builder
from sphinx.util.osutil import ensuredir, SEP
from os import path
from xmlrpc.client import Fault
import codecs

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
    legacy_pages = []
    publisher = ConfluencePublisher()

    def init(self):
        self.publisher.init(self.config)

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

        if self.config.confluence_space_name is not None:
            self.space_name = self.config.confluence_space_name
        else:
            self.parent_id = None

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

    def prepare_writing(self, docnames):
        self.writer = ConfluenceWriter(self)
        for doc in docnames:
            doctree = self.env.get_doctree(doc)
            idx = doctree.first_child_matching_class(nodes.section)
            if idx is None or idx == -1:
                continue

            first_section = doctree[idx]
            idx = first_section.first_child_matching_class(nodes.title)
            if idx is None or idx == -1:
                continue

            doctitle = first_section[idx].astext()
            if doctitle:
                ConfluenceDocMap.register(doc, doctitle,
                    self.config.confluence_publish_prefix)

        ConfluenceDocMap.conflictCheck()

    def write_doc(self, docname, doctree):
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
            title = ConfluenceDocMap.title(docname)
            if not title:
                self.warn("skipping document with no title: %s" % docname)
                return

            uploaded_page_id = self.publisher.storePage(title,
                    self.writer.output, self.parent_id)
            if self.config.confluence_purge:
                if uploaded_page_id in self.legacy_pages:
                    self.legacy_pages.remove(uploaded_page_id)

    def finish(self):
        if self.publish:
            if self.config.confluence_purge is True and self.legacy_pages:
                self.info('removing legacy pages... ', nonl=0)
                for legacy_page_id in self.legacy_pages:
                   self.publisher.removePage(legacy_page_id)
                self.info('done\n')

            self.publisher.disconnect()
