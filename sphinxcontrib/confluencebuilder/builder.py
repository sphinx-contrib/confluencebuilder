# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2016-2018 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from __future__ import (print_function, unicode_literals, absolute_import)
from .assets import ConfluenceAssetManager
from .config import ConfluenceConfig
from .exceptions import ConfluenceConfigurationError
from .logger import ConfluenceLogger
from .publisher import ConfluencePublisher
from .state import ConfluenceState
from .util import ConfluenceUtil
from .writer import ConfluenceWriter
from docutils import nodes
from docutils.io import StringOutput
from getpass import getpass
from os import path
from sphinx import addnodes
from sphinx.builders import Builder
from sphinx.util import status_iterator
from sphinx.util.osutil import ensuredir, SEP
import io
import sys

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

    def __init__(self, app):
        super(ConfluenceBuilder, self).__init__(app)

        self.cache_doctrees = {}
        self.current_docname = None
        self.file_suffix = '.conf'
        self.link_suffix = None
        self.master_doc_page_id = None
        self.omitted_docnames = []
        self.publish_docnames = []
        self.publisher = ConfluencePublisher()

        # state tracking is set at initialization (not cleanup) so its content's
        # can be checked/validated on after the builder has executed (testing)
        ConfluenceState.reset()

    def init(self, suppress_conf_check=False):
        if not ConfluenceConfig.validate(self.config, not suppress_conf_check):
            raise ConfluenceConfigurationError('configuration error')

        if self.config.confluence_ask_password:
            print('(request to accept password from interactive session)')
            print(' Instance: ' + self.config.confluence_server_url)
            print('     User: ' + self.config.confluence_server_user)
            sys.stdout.write(' Password: ')
            sys.stdout.flush()
            self.config.confluence_server_pass = getpass('')
            if not self.config.confluence_server_pass:
                raise ConfluenceConfigurationError('no password provided')

        self.assets = ConfluenceAssetManager(self.config.master_doc, self.env)
        self.writer = ConfluenceWriter(self)
        self.config.sphinx_verbosity = self.app.verbosity
        self.publisher.init(self.config)

        old_url = self.config.confluence_server_url
        new_url = ConfluenceUtil.normalizeBaseUrl(old_url)
        if old_url != new_url:
            ConfluenceLogger.warn('normalizing confluence url from '
                '{} to {} '.format(old_url, new_url))
            self.config.confluence_server_url = new_url

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

        if self.config.confluence_lang_transform is not None:
            self.lang_transform = self.config.confluence_lang_transform
        else:
            self.lang_transform = None

        if self.config.confluence_publish and (self.config.confluence_publish.lower()
                                               not in ('0', 'false', 'n', 'no', 'off')):
            self.publish = True
            self.publisher.connect()
        else:
            self.publish = False

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

    def prepare_writing(self, docnames):
        ordered_docnames = []
        traversed = [self.config.master_doc]

        # prepare caching doctree hook
        #
        # We'll temporarily override the environment's 'get_doctree' method to
        # allow this extension to manipulate the doctree for a document inside
        # the pre-writing stage to also take effect in the writing stage.
        self._original_get_doctree = self.env.get_doctree
        self.env.get_doctree = self._get_doctree

        # process the document structure of the master document, allowing:
        #  - populating a publish order to ensure parent pages are created first
        #     (when using hierarchy mode)
        #  - squash pages which exceed maximum depth (if configured with a max
        #     depth value)
        self.process_tree_structure(
            ordered_docnames, self.config.master_doc, traversed)

        # add orphans (if any) to the publish list
        ordered_docnames.extend(x for x in docnames if x not in traversed)

        for docname in ordered_docnames:
            doctree = self.env.get_doctree(docname)

            doctitle = self._parse_doctree_title(docname, doctree)
            if not doctitle:
                continue

            doctitle = ConfluenceState.registerTitle(docname, doctitle,
                self.config.confluence_publish_prefix)
            self.publish_docnames.append(docname)

            toctrees = doctree.traverse(addnodes.toctree)
            if toctrees and toctrees[0].get('maxdepth') > 0:
                ConfluenceState.registerToctreeDepth(
                    docname, toctrees[0].get('maxdepth'))

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
                            id = '{}#{}'.format(docname, id)
                            ConfluenceState.registerTarget(id, target)

        # Scan for assets that may exist in the documents to be published. This
        # will find most if not all assets in the documentation set. The
        # exception is assets which may be finalized during a document's post
        # transformation stage (e.x. embedded images are converted into real
        # images in Sphinx, which is then provided to a translator). Embedded
        # images are detected during an 'doctree-resolved' hook (see __init__).
        ConfluenceLogger.info('scanning for assets... ', nonl=0)
        self.assets.process(ordered_docnames)
        ConfluenceLogger.info('done\n')

        ConfluenceState.titleConflictCheck()

    def process_tree_structure(self, ordered, docname, traversed, depth=0):
        omit = False
        max_depth = self.config.confluence_max_doc_depth
        if max_depth is not None and depth > max_depth:
            omit = True
            self.omitted_docnames.append(docname)

        if not omit:
            ordered.append(docname)

        modified = False
        doctree = self.env.get_doctree(docname)
        for toctreenode in doctree.traverse(addnodes.toctree):
            if not omit and max_depth is not None:
                if (toctreenode['maxdepth'] == -1 or
                        depth + toctreenode['maxdepth'] > max_depth):
                    new_depth = max_depth - depth
                    assert new_depth >= 0
                    toctreenode['maxdepth'] = new_depth
            movednodes = []
            for child in toctreenode['includefiles']:
                if child not in traversed:
                    ConfluenceState.registerParentDocname(child, docname)
                    traversed.append(child)

                    children = self.process_tree_structure(
                        ordered, child, traversed, depth+1)
                    if children:
                        movednodes.append(children)
                        self._fix_std_labels(child, docname)

            if movednodes:
                modified = True
                toctreenode.replace_self(movednodes)
                toctreenode.parent['classes'].remove('toctree-wrapper')

        if omit:
            container = addnodes.start_of_file(docname=docname)
            container.children = doctree.children
            return container
        elif modified:
            self.env.resolve_references(doctree, docname, self)

    def write_doc(self, docname, doctree):
        if docname in self.omitted_docnames:
            return
        self.current_docname = docname

        # remove title from page contents (if any)
        if self.config.confluence_remove_title:
            title_element = self._find_title_element(doctree)
            if title_element:
                # If the removed title is referenced to from within the same
                # document (i.e. a local table of contents entry), remove the
                # entry (and parents if empty). This should, in the case of a
                # table of contents (contents directive), remove the leading
                # generated title link.
                if 'refid' in title_element:
                    for node in doctree.traverse(nodes.reference):
                        if ('ids' in node
                                and node['ids'][0] == title_element['refid']):
                            def remove_until_has_children(node):
                                parent = node.parent
                                parent.remove(node)
                                if not parent.children:
                                    remove_until_has_children(parent)
                            remove_until_has_children(node)

                title_element.parent.remove(title_element)

        # This method is taken from TextBuilder.write_doc()
        # with minor changes to support :confval:`rst_file_transform`.
        destination = StringOutput(encoding='utf-8')

        self.writer.write(doctree, destination)
        outfilename = path.join(self.outdir, self.file_transform(docname))
        if self.writer.output:
            ensuredir(path.dirname(outfilename))
            try:
                with io.open(outfilename, 'w', encoding='utf-8') as file:
                    file.write(self.writer.output)
            except (IOError, OSError) as err:
                ConfluenceLogger.warn("error writing file "
                    "%s: %s" % (outfilename, err))

    def publish_doc(self, docname, output):
        conf = self.config
        title = ConfluenceState.title(docname)

        parent_id = None
        if self.config.master_doc and self.config.confluence_page_hierarchy:
            if self.config.master_doc != docname:
                parent = ConfluenceState.parentDocname(docname)
                parent_id = ConfluenceState.uploadId(parent)
        if not parent_id:
            parent_id = self.parent_id

        uploaded_id = self.publisher.storePage(title, output, parent_id)
        ConfluenceState.registerUploadId(docname, uploaded_id)

        if self.config.master_doc == docname:
            self.master_doc_page_id = uploaded_id

        if conf.confluence_purge and self.legacy_pages is None:
            if conf.confluence_purge_from_master and self.master_doc_page_id:
                baseid = self.master_doc_page_id
            else:
                baseid = self.parent_id
            ConfluenceLogger.info('querying list of existing pages...')
            if self.config.confluence_adv_aggressive_search is True:
                self.legacy_pages = self.publisher.getDescendantsCompat(baseid)
            else:
                self.legacy_pages = self.publisher.getDescendants(baseid)

            # only populate a list of possible legacy assets when a user is
            # configured to check or push assets to the target space
            asset_override = conf.confluence_asset_override
            if asset_override is None or asset_override:
                for legacy_page in self.legacy_pages:
                    attachments = self.publisher.getAttachments(legacy_page)
                    self.legacy_assets[legacy_page] = attachments

        if conf.confluence_purge:
            if uploaded_id in self.legacy_pages:
                self.legacy_pages.remove(uploaded_id)

    def publish_asset(self, key, docname, output, type, hash):
        conf = self.config
        publisher = self.publisher

        title = ConfluenceState.title(docname)
        page_id = ConfluenceState.uploadId(docname)

        if not page_id:
            # A page identifier may not be tracked in cases where only a subset
            # of documents are published and the target page an asset will be
            # published to was not part of the request. In this case, ask the
            # Confluence instance what the target page's identifier is.
            page_id, _ = publisher.getPage(title)
            if page_id:
                ConfluenceState.registerUploadId(docname, page_id)
            else:
                ConfluenceLogger.warn('cannot publish asset since publishing '
                    'point cannot be found ({}): {}'.format(key, docname))
                return

        if conf.confluence_asset_override is None:
            # "automatic" management -- check if already published; if not, push
            attachment_id = publisher.storeAttachment(
                page_id, key, output, type, hash)
        elif conf.confluence_asset_override:
            # forced publishing of the asset
            attachment_id = publisher.storeAttachment(
                page_id, key, output, type, hash, force=True)

        if attachment_id and conf.confluence_purge:
            if page_id in self.legacy_assets:
                legacy_asset_info = self.legacy_assets[page_id]
                if attachment_id in legacy_asset_info:
                    legacy_asset_info.pop(attachment_id, None)

    def publish_finalize(self):
        if self.master_doc_page_id:
            if self.config.confluence_master_homepage is True:
                ConfluenceLogger.info('updating space\'s homepage... ', nonl=0)
                self.publisher.updateSpaceHome(self.master_doc_page_id)
                ConfluenceLogger.info('done\n')

    def publish_purge(self):
        if self.config.confluence_purge:
            if self.legacy_pages:
                n = len(self.legacy_pages)
                ConfluenceLogger.info(
                    'removing legacy pages... (total: {}) '.format(n), nonl=0)
                for legacy_page_id in self.legacy_pages:
                    self.publisher.removePage(legacy_page_id)
                    # remove any pending assets to remove from the page (as they
                    # are already been removed)
                    self.legacy_assets.pop(legacy_page_id, None)
                ConfluenceLogger.info('done\n')

            n = 0
            for page_id, legacy_asset_info in self.legacy_assets.items():
                n += len(legacy_asset_info.keys())
            if n > 0:
                ConfluenceLogger.info(
                    'removing legacy assets... (total: {}) '.format(n), nonl=0)
                for page_id, legacy_asset_info in self.legacy_assets.items():
                    for id, name in legacy_asset_info.items():
                        self.publisher.removeAttachment(page_id, id, name)
                ConfluenceLogger.info('done\n')

    def finish(self):
        self.env.get_doctree = self._original_get_doctree

        if self.publish:
            self.legacy_assets = {}
            self.legacy_pages = None
            self.parent_id = self.publisher.getBasePageId()

            for docname in status_iterator(
                    self.publish_docnames, 'publishing documents... ',
                    length=len(self.publish_docnames),
                    verbosity=self.app.verbosity):
                docfile = path.join(self.outdir, self.file_transform(docname))

                try:
                    with io.open(docfile, 'r', encoding='utf-8') as file:
                        output = file.read()
                        self.publish_doc(docname, output)

                except (IOError, OSError) as err:
                    ConfluenceLogger.warn("error reading file %s: "
                        "%s" % (docfile, err))

            def to_asset_name(asset):
                return asset[0]

            assets = self.assets.build()
            for asset in status_iterator(assets, 'publishing assets... ',
                    length=len(assets), verbosity=self.app.verbosity,
                    stringify_func=to_asset_name):
                key, absfile, type, hash, docname = asset

                try:
                    with open(absfile, 'rb') as file:
                        output = file.read()
                        self.publish_asset(key, docname, output, type, hash)
                except (IOError, OSError) as err:
                    ConfluenceLogger.warn("error reading asset %s: "
                        "%s" % (key, err))

            self.publish_purge()
            self.publish_finalize()

    def cleanup(self):
        if self.publish:
            self.publisher.disconnect()

    def _find_title_element(self, doctree):
        """
        find (if any) the title element of a document

        From a provided document's doctree, attempt to extract a possible title
        value from known information. This call will look for the first section
        node's title value as the title value for a document.

        Args:
            doctree: the document tree to find a title value element on

        Returns:
            the title element
        """
        node = doctree.next_node(nodes.section)
        if isinstance(node, nodes.section):
            return node.next_node(nodes.title)

        return None

    def _fix_std_labels(self, olddocname, newdocname):
        """
        fix standard domain labels for squashed documents

        When Sphinx resolves references for a doctree ('resolve_references'),
        the standard domain's internal labels are used to map references to
        target documents. To support document squashing (aka. max depth pages),
        this utility method helps override a document's tuple labels so that any
        squashed page's labels can be moved into a parent document's label set.
        """
        # see also: sphinx/domains/std.py
        domain = self.env.get_domain('std')
        for key, (fn, _l, lineno) in list(domain.data['citations'].items()):
            if fn == olddocname:
                data = domain.data['citations'][key]
                domain.data['citations'][key] = newdocname, data[1], data[2]
        for key, docnames in list(domain.data['citation_refs'].items()):
            if fn == olddocname:
                data = domain.data['citation_refs'][key]
                domain.data['citation_refs'][key] = newdocname
        for key, (fn, _l, _l) in list(domain.data['labels'].items()):
            if fn == olddocname:
                data = domain.data['labels'][key]
                domain.data['labels'][key] = newdocname, data[1], data[2]
        for key, (fn, _l) in list(domain.data['anonlabels'].items()):
            if fn == olddocname:
                data = domain.data['anonlabels'][key]
                domain.data['anonlabels'][key] = newdocname, data[1]

    def _get_doctree(self, docname):
        """
        override 'get_doctree' method

        To support document squashing (aka. max depth pages), doctree's may be
        loaded and manipulated before the writing stage. Normally, the writing
        stage will load target doctree's from their source so there is no way to
        pre-load and pass a document's doctree into the writing stage. To
        overcome this, this extension hooks into the environment's 'get_doctree'
        method and caches loaded document's doctree's into a map.
        """
        if docname not in self.cache_doctrees:
            self.cache_doctrees[docname] = self._original_get_doctree(docname)
        return self.cache_doctrees[docname]

    def _parse_doctree_title(self, docname, doctree):
        """
        parse a doctree for a raw title value

        Examine a document's doctree value to find a title value from a title
        section element. If no title is found, a title can be automatically
        generated (if configuration permits) or a `None` value is returned.
        """
        doctitle = None
        title_element = self._find_title_element(doctree)
        if title_element:
            doctitle = title_element.astext()

        if not doctitle:
            if not self.config.confluence_disable_autogen_title:
                doctitle = "autogen-{}".format(docname)
                if self.publish:
                    ConfluenceLogger.warn("document will be published using an "
                        "generated title value: {}".format(docname))
            elif self.publish:
                ConfluenceLogger.warn("document will not be published since it "
                    "has no title: {}".format(docname))

        return doctitle
