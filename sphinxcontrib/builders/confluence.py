# -*- coding: utf-8 -*-
"""
    sphinxcontrib.builders.confluence
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. moduleauthor:: Anthony Shaw <anthonyshaw@apache.org>

    :copyright: Copyright 2016 by Anthony Shaw.
    :license: BSD, see LICENSE.txt for details.
"""

from __future__ import (print_function, unicode_literals, absolute_import)

import codecs
from os import path

from docutils.io import StringOutput

from sphinx.builders import Builder
from sphinx.util.osutil import ensuredir, SEP
from ..writers.confluence import ConfluenceWriter

from xmlrpclib import Fault

try:
    from confluence import Confluence
    HAS_CONFLUENCE = True
except ImportError:
    HAS_CONFLUENCE = False


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
    name = 'confluence'
    format = 'confluence'
    file_suffix = '.conf'
    link_suffix = None  # defaults to file_suffix

    def init(self):
        """Load necessary templates and perform initialization."""
        if self.config.confluence_file_suffix is not None:
            self.file_suffix = self.config.confluence_file_suffix
        if self.config.confluence_link_suffix is not None:
            self.link_suffix = self.config.confluence_link_suffix
        elif self.link_suffix is None:
            self.link_suffix = self.file_suffix
        if self.config.confluence_publish:
            if not HAS_CONFLUENCE:
                raise ImportError("Must install Confluence module first to publish.")
            self.publish = True
            self._connect()
        else:
            self.publish = False
        if self.config.confluence_space_name is not None:
            self.space_name = self.config.confluence_space_name
        if self.config.confluence_parent_page is not None and self.publish:
            self.parent_id = self.confluence.getPageId(self.config.confluence_parent_page,
                                                       self.space_name)
        else:
            self.parent_id = None

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

    def write_doc(self, docname, doctree):
        # This method is taken from TextBuilder.write_doc()
        # with minor changes to support :confval:`rst_file_transform`.
        destination = StringOutput(encoding='utf-8')
        # print "write(%s,%s)" % (type(doctree), type(destination))

        self.writer.write(doctree, destination)
        outfilename = path.join(self.outdir, self.file_transform(docname))
        # print "write(%s,%s) -> %s" % (type(doctree), type(destination), outfilename)
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
            if len(doctree.children) <= 0:
                self.warn("Skipping page %s with no title" % outfilename)
                return
            title = [el for el in doctree.traverse() if el.tagname == 'title'][0].astext()
            try:
                page = self.confluence.getPage(str(title), self.space_name)
            except Fault:
                page = {
                    'title': title,
                    'space': self.space_name
                }
            finally:
                self.info('Uploading page to confluence - Title "%s"' % title)
                if '\n' in str(title):
                    self.warn('Page title too long, truncating')
                    page['title'] = str(title).split('\n')[0]
                page['content'] = self.confluence._server.confluence2.convertWikiToStorageFormat(
                    self.confluence._token2,
                    self.writer.output)
                if self.parent_id:
                    page['parentId'] = self.parent_id
                self.confluence._server.confluence2.storePage(
                    self.confluence._token2,
                    page)

    def finish(self):
        pass

    def _connect(self):
        try:
            self.confluence = Confluence(profile='sphinx')
        except ImportError:
            raise ImportError("Must install confluence PyPi package to publish")
        except Exception as ex:
            raise Exception("Could not connect, check remote API is configured. %s" % ex)
