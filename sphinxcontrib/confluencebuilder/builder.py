# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from docutils import nodes
from docutils.io import StringOutput
from os import path
from sphinx import addnodes
from sphinx.builders import Builder
from sphinx.errors import ExtensionError
from sphinx.locale import __
from sphinx.util import status_iterator
from sphinx.util.math import wrap_displaymath
from sphinx.util.osutil import ensuredir
from sphinxcontrib.confluencebuilder.assets import ConfluenceAssetManager
from sphinxcontrib.confluencebuilder.assets import ConfluenceSupportedImages
from sphinxcontrib.confluencebuilder.config import process_ask_configs
from sphinxcontrib.confluencebuilder.config.checks import validate_configuration
from sphinxcontrib.confluencebuilder.config.defaults import apply_defaults
from sphinxcontrib.confluencebuilder.intersphinx import build_intersphinx
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger
from sphinxcontrib.confluencebuilder.nodes import ConfluenceNavigationNode
from sphinxcontrib.confluencebuilder.nodes import confluence_metadata
from sphinxcontrib.confluencebuilder.publisher import ConfluencePublisher
from sphinxcontrib.confluencebuilder.state import ConfluenceState
from sphinxcontrib.confluencebuilder.util import ConfluenceUtil
from sphinxcontrib.confluencebuilder.util import extract_strings_from_file
from sphinxcontrib.confluencebuilder.util import first
from sphinxcontrib.confluencebuilder.writer import ConfluenceWriter
import io

try:
    basestring
except NameError:
    basestring = str

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

class ConfluenceBuilder(Builder):
    allow_parallel = True
    name = 'confluence'
    format = 'confluence_storage'
    supported_image_types = ConfluenceSupportedImages()
    supported_remote_images = True

    def __init__(self, app):
        super(ConfluenceBuilder, self).__init__(app)

        self.cache_doctrees = {}
        self.cloud = False
        self.file_suffix = '.conf'
        self.info = ConfluenceLogger.info
        self.link_suffix = None
        self.master_doc_page_id = None
        self.metadata = {}
        self.nav_next = {}
        self.nav_prev = {}
        self.omitted_docnames = []
        self.publish_allowlist = []
        self.publish_denylist = []
        self.publish_docnames = []
        self.publisher = ConfluencePublisher()
        self.secnumbers = {}
        self.verbose = ConfluenceLogger.verbose
        self.warn = ConfluenceLogger.warn
        self._original_get_doctree = None

        # state tracking is set at initialization (not cleanup) so its content's
        # can be checked/validated on after the builder has executed (testing)
        ConfluenceState.reset()

    def init(self):
        validate_configuration(self)
        apply_defaults(self.config)
        config = self.config

        self.add_secnumbers = self.config.confluence_add_secnumbers
        self.secnumber_suffix = self.config.confluence_secnumber_suffix

        if self.config.confluence_additional_mime_types:
            for type_ in self.config.confluence_additional_mime_types:
                self.supported_image_types.register(type_)

        if 'graphviz_output_format' in self.config:
            self.graphviz_output_format = self.config['graphviz_output_format']
        else:
            self.graphviz_output_format = 'png'

        if self.config.confluence_publish:
            process_ask_configs(self.config)

        self.assets = ConfluenceAssetManager(config, self.env, self.outdir)
        self.writer = ConfluenceWriter(self)
        self.config.sphinx_verbosity = self.app.verbosity
        self.publisher.init(self.config)

        old_url = self.config.confluence_server_url
        new_url = ConfluenceUtil.normalizeBaseUrl(old_url)
        if old_url != new_url:
            ConfluenceLogger.warn('normalizing confluence url from '
                '{} to {} '.format(old_url, new_url))
            self.config.confluence_server_url = new_url

        # detect if Confluence Cloud if using the Atlassian domain
        if new_url:
            self.cloud = new_url.endswith('.atlassian.net/wiki/')

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

        self.prev_next_loc = self.config.confluence_prev_next_buttons_location

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

        if self.config.confluence_publish:
            self.publish = True
            self.publisher.connect()
        else:
            self.publish = False

        def prepare_subset(option):
            value = getattr(config, option)
            if not value:
                return None

            # if provided via command line, treat as a list
            if option in config['overrides'] and isinstance(value, basestring):
                value = value.split(',')

            if isinstance(value, basestring):
                files = extract_strings_from_file(value)
            else:
                files = value

            return set(files) if files else None

        self.publish_allowlist = prepare_subset('confluence_publish_allowlist')
        self.publish_denylist = prepare_subset('confluence_publish_denylist')

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

        # track relations between accepted documents
        #
        # Prepares a relation mapping between each non-orphan documents which
        # can be used by navigational elements.
        prevdoc = ordered_docnames[0] if ordered_docnames else None
        for docname in ordered_docnames[1:]:
            self.nav_prev[docname] = self.get_relative_uri(docname, prevdoc)
            self.nav_next[prevdoc] = self.get_relative_uri(prevdoc, docname)
            prevdoc = docname

        # add orphans (if any) to the publish list
        ordered_docnames.extend(x for x in docnames if x not in traversed)

        for docname in ordered_docnames:
            doctree = self.env.get_doctree(docname)

            # acquire title from override (if any), or parse first title entity
            if (self.config.confluence_title_overrides and
                    docname in self.config.confluence_title_overrides):
                doctitle = self.config.confluence_title_overrides[docname]
            else:
                doctitle = self._parse_doctree_title(docname, doctree)

            # only register title/track for publishing if there is a title
            # value that can be applied to this document
            if doctitle:
                secnumbers = self.env.toc_secnumbers.get(docname, {})
                if self.add_secnumbers and secnumbers.get(''):
                    doctitle = ('.'.join(map(str, secnumbers[''])) +
                        self.secnumber_suffix + doctitle)

                doctitle = ConfluenceState.registerTitle(docname, doctitle,
                    self.config)

                # only publish documents that sphinx asked to prepare
                if docname in docnames:
                    self.publish_docnames.append(docname)

            # track the toctree depth for a document, which a translator can
            # use as a hint when dealing with max-depth capabilities
            toctree = first(doctree.traverse(addnodes.toctree))
            if toctree and toctree.get('maxdepth') > 0:
                ConfluenceState.registerToctreeDepth(
                    docname, toctree.get('maxdepth'))

            # register title targets for references
            self._register_doctree_title_targets(docname, doctree)

            # post-prepare a ready doctree
            self._prepare_doctree_writing(docname, doctree)

        # Scan for assets that may exist in the documents to be published. This
        # will find most if not all assets in the documentation set. The
        # exception is assets which may be finalized during a document's post
        # transformation stage (e.g. embedded images are converted into real
        # images in Sphinx, which is then provided to a translator). Embedded
        # images are detected during an 'doctree-resolved' hook (see __init__).
        self.assets.process(ordered_docnames)

    def _prepare_doctree_writing(self, docname, doctree):
        # extract metadata information
        self._extract_metadata(docname, doctree)

        # replace inheritance diagram with images
        # (always invoke before _replace_graphviz_nodes)
        self._replace_inheritance_diagram(doctree)

        # replace graphviz nodes with images
        self._replace_graphviz_nodes(doctree)

        # replace math blocks with images
        self._replace_math_blocks(doctree)

        # for every doctree, pick the best image candidate
        self.post_process_images(doctree)

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
                        ordered, child, traversed, depth + 1)
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

        if self.prev_next_loc in ('top', 'both'):
            navnode = self._build_navigation_node(docname)
            if navnode:
                navnode.top = True
                doctree.insert(0, navnode)

        if self.prev_next_loc in ('bottom', 'both'):
            navnode = self._build_navigation_node(docname)
            if navnode:
                navnode.bottom = True
                doctree.append(navnode)

        self.secnumbers = self.env.toc_secnumbers.get(docname, {})
        self.fignumbers = self.env.toc_fignumbers.get(docname, {})

        # remove title from page contents (if any)
        if self.config.confluence_remove_title:
            title_element = self._find_title_element(doctree)
            if title_element:
                # If the removed title is referenced to from within the same
                # document (i.e. a local table of contents entry), flag any
                # references pointing to it as a "top" (anchor) reference. This
                # can be used later in a translator to hint at what type of link
                # to build.
                ids = []

                if 'ids' in title_element:
                    ids.extend(title_element['ids'])

                parent = title_element.parent
                if isinstance(parent, nodes.section) and 'ids' in parent:
                    ids.extend(parent['ids'])

                if ids:
                    for node in doctree.traverse(nodes.reference):
                        if 'refid' in node and node['refid']:
                            if node['refid'] in ids:
                                node['top-reference'] = True
                                break

                title_element.parent.remove(title_element)

        # This method is taken from TextBuilder.write_doc()
        # with minor changes to support :confval:`rst_file_transform`.
        destination = StringOutput(encoding='utf-8')

        self.writer.write(doctree, destination)
        outfilename = path.join(self.outdir, self.file_transform(docname))
        if self.writer.output is not None:
            ensuredir(path.dirname(outfilename))
            try:
                with io.open(outfilename, 'w', encoding='utf-8') as file:
                    if self.writer.output:
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

        data = {
            'content': output,
            'labels': [],
        }

        if self.config.confluence_global_labels:
            data['labels'].extend(self.config.confluence_global_labels)

        metadata = self.metadata[docname]
        if 'labels' in metadata:
            data['labels'].extend([v for v in metadata['labels']])

        uploaded_id = self.publisher.storePage(title, data, parent_id)
        ConfluenceState.registerUploadId(docname, uploaded_id)

        if self.config.master_doc == docname:
            self.master_doc_page_id = uploaded_id

        if conf.confluence_purge and self.legacy_pages is None:
            if conf.confluence_purge_from_master and self.master_doc_page_id:
                baseid = self.master_doc_page_id
            else:
                baseid = self.parent_id

            # if no base identifier and dry running, ignore legeacy page
            # searching as there is no initial master document to reference
            # against
            if (conf.confluence_purge_from_master and
                    conf.confluence_publish_dryrun and not baseid):
                self.legacy_pages = []
            elif self.config.confluence_adv_aggressive_search is True:
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
                self.info('updating space\'s homepage... ', nonl=True)
                self.publisher.updateSpaceHome(self.master_doc_page_id)
                self.info('done\n')

            if self.cloud:
                point_url = '{0}spaces/{1}/pages/{2}'
            else:
                point_url = '{0}pages/viewpage.action?pageId={2}'

            self.info('Publish point: ' + point_url.format(
                self.config.confluence_server_url,
                self.config.confluence_space_name,
                self.master_doc_page_id))

    def publish_purge(self):
        if self.config.confluence_purge:
            if self.publish_allowlist or self.publish_denylist:
                self.warn('confluence_purge disabled due to '
                    'confluence_publish_allowlist/confluence_publish_denylist')
                return

            if self.legacy_pages:
                n = len(self.legacy_pages)
                self.info('removing legacy pages... (total: {}) '.format(n),
                    nonl=True)
                for legacy_page_id in self.legacy_pages:
                    self.publisher.removePage(legacy_page_id)
                    # remove any pending assets to remove from the page (as they
                    # are already been removed)
                    self.legacy_assets.pop(legacy_page_id, None)
                self.info('done\n')

            n = 0
            for legacy_asset_info in self.legacy_assets.values():
                n += len(legacy_asset_info.keys())
            if n > 0:
                self.info('removing legacy assets... (total: {}) '.format(n),
                    nonl=True)
                for legacy_asset_info in self.legacy_assets.values():
                    for id in legacy_asset_info.keys():
                        self.publisher.removeAttachment(id)
                self.info('done\n')

    def finish(self):
        # restore environment's get_doctree if it was temporarily replaced
        if self._original_get_doctree:
            self.env.get_doctree = self._original_get_doctree

        if self.publish:
            self.legacy_assets = {}
            self.legacy_pages = None
            self.parent_id = self.publisher.getBasePageId()

            for docname in status_iterator(
                    self.publish_docnames, 'publishing documents... ',
                    length=len(self.publish_docnames),
                    verbosity=self.app.verbosity):
                if self._check_publish_skip(docname):
                    self.verbose(docname + ' skipped due to configuration')
                    continue
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
                if self._check_publish_skip(docname):
                    self.verbose(key + ' skipped due to configuration')
                    continue

                try:
                    with open(absfile, 'rb') as file:
                        output = file.read()
                        self.publish_asset(key, docname, output, type, hash)
                except (IOError, OSError) as err:
                    ConfluenceLogger.warn("error reading asset %s: "
                        "%s" % (key, err))

            self.publish_purge()
            self.publish_finalize()

            self.info('building intersphinx... ', nonl=True)
            build_intersphinx(self)
            self.info('done\n')

    def cleanup(self):
        if self.publish:
            self.publisher.disconnect()

    def _build_navigation_node(self, docname):
        """
        build a navigation node for a document

        Requests to build a navigation node for a provided document name. If
        this document has no navigational hints to apply, this method will
        return a `None` value.

        Args:
            docname: the document name

        Returns:
            returns a navigation node; ``None`` if no nav-node for document
        """
        if docname not in self.nav_prev and docname not in self.nav_next:
            return None

        navnode = ConfluenceNavigationNode()

        if docname in self.nav_prev:
            prev_label = '← ' + __('Previous')
            reference = nodes.reference(prev_label, prev_label, internal=True,
                refuri=self.nav_prev[docname])
            reference._navnode = True
            reference._navnode_next = False
            reference._navnode_previous = True
            navnode.append(reference)

        if docname in self.nav_next:
            next_label = __('Next') + ' →'
            reference = nodes.reference(next_label, next_label, internal=True,
                refuri=self.nav_next[docname])
            reference._navnode = True
            reference._navnode_next = True
            reference._navnode_previous = False
            navnode.append(reference)

        return navnode

    def _check_publish_skip(self, docname):
        """
        check publishing should be skipped for the provided docname

        A runner's configuration may have an explicit list of docnames to either
        allow or deny publishing. Check if the provided docname has been flagged
        to be skipped.

        Args:
            docname: the docname to check
        """
        if self.publish_denylist and docname in self.publish_denylist:
            return True

        if self.publish_allowlist and docname not in self.publish_allowlist:
            return True

        return False

    def _extract_metadata(self, docname, doctree):
        """
        extract metadata from a document

        Documents may define metadata information which can be used during a
        publication event. When processing a doctree, strip out the metadata
        information and save it for when a publish event occurs.

        Args:
            docname: the document
            doctree: the doctree to extract metadata from
        """
        metadata = self.metadata.setdefault(docname, {})

        for node in doctree.traverse(confluence_metadata):
            labels = metadata.setdefault('labels', [])
            labels.extend(node['params']['labels'])
            node.parent.remove(node)

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
        std_domain = self.env.get_domain('std')
        try:
            citation_domain = self.env.get_domain('citation')
        except ExtensionError:
            citation_domain = None

        if 'anonlabels' in std_domain.data:
            anonlabels = std_domain.data['anonlabels']
            for key, (fn, _l) in list(anonlabels.items()):
                if fn == olddocname:
                    data = anonlabels[key]
                    anonlabels[key] = newdocname, data[1]

        citations = None
        if 'citations' in std_domain.data: # Sphinx <2.1
            citations = std_domain.data['citations']
        elif citation_domain: # Sphinx >=2.1
            citations = citation_domain.citations
        if citations:
            for key, (fn, _l, lineno) in list(citations.items()):
                if fn == olddocname:
                    data = citations[key]
                    citations[key] = newdocname, data[1], data[2]

        if 'citation_refs' in std_domain.data: # Sphinx <2.0
            citation_refs = std_domain.data['citation_refs']
            for key, docnames in list(citation_refs.items()):
                if fn == olddocname:
                    data = citation_refs[key]
                    citation_refs[key] = newdocname

        if 'labels' in std_domain.data:
            labels = std_domain.data['labels']
            for key, (fn, _l, _l) in list(labels.items()):
                if fn == olddocname:
                    data = labels[key]
                    labels[key] = newdocname, data[1], data[2]

        if 'objects' in std_domain.data:
            objects = std_domain.data['objects']
            for key, (fn, _l) in list(objects.items()):
                if fn == olddocname:
                    data = objects[key]
                    objects[key] = newdocname, data[1]

        if 'progoptions' in std_domain.data:
            progoptions = std_domain.data['progoptions']
            for key, (fn, _l) in list(progoptions.items()):
                if fn == olddocname:
                    data = progoptions[key]
                    progoptions[key] = newdocname, data[1]

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
        secnumbers = self.env.toc_secnumbers.get(docname, {})

        for node in doctree.traverse(nodes.title):
            if isinstance(node.parent, nodes.section):
                section_node = node.parent
                if 'ids' in section_node:
                    target = ''.join(node.astext().split())

                    # when confluence has a header that contains a link, the
                    # automatically assigned identifier removes any underscores
                    if node.next_node(addnodes.pending_xref):
                        target = target.replace('_', '')

                    if self.add_secnumbers:
                        anchorname = '#' + target
                        if anchorname not in secnumbers:
                            anchorname = ''

                        secnumber = secnumbers.get(anchorname)
                        if secnumber:
                            target = ('.'.join(map(str, secnumber)) +
                                self.secnumber_suffix + target)

                    section_id = doc_used_names.get(target, 0)
                    doc_used_names[target] = section_id + 1
                    if section_id > 0:
                        target = '{}.{}'.format(target, section_id)

                    for id in section_node['ids']:
                        id = '{}#{}'.format(docname, id)
                        ConfluenceState.registerTarget(id, target)

    def _replace_graphviz_nodes(self, doctree):
        """
        replace graphviz nodes with images

        graphviz nodes are pre-processed and replaced with respective images in
        the processed documentation set. Typically, the node support from
        `sphinx.ext.graphviz` would be added to the builder; however, this
        extension renders graphs during the translation phase (which is not
        ideal for how assets are managed in this extension).

        Instead, this implementation just traverses for graphviz nodes,
        generates renderings and replaces the nodes with image nodes (which in
        turn will be handled by the existing image-based implementation).

        Args:
            doctree: the doctree to replace blocks on
        """
        if graphviz is None:
            return

        # graphviz's render_dot call expects a translator to be passed in; mock
        # a translator tied to our self-builder
        class MockTranslator:
            def __init__(self, builder):
                self.builder = builder
        mock_translator = MockTranslator(self)

        for node in doctree.traverse(graphviz):
            try:
                _, out_filename = render_dot(mock_translator, node['code'],
                    node['options'], self.graphviz_output_format, 'graphviz')
                if not out_filename:
                    node.parent.remove(node)
                    continue

                new_node = nodes.image(candidates={'?'}, uri=out_filename)
                if 'align' in node:
                    new_node['align'] = node['align']
                node.replace_self(new_node)
            except GraphvizError as exc:
                ConfluenceLogger.warn('dot code {}: {}'.format(
                    node['code'], exc))
                node.parent.remove(node)

    def _replace_inheritance_diagram(self, doctree):
        """
        replace inheritance diagrams with images

        Inheritance diagrams are pre-processed and replaced with respective
        images in the processed documentation set. Typically, the node support
        from `sphinx.ext.inheritance_diagram` would be added to the builder;
        however, this extension renders graphs during the translation phase
        (which is not ideal for how assets are managed in this extension).

        Instead, this implementation just traverses for inheritance diagrams,
        generates renderings and replaces the nodes with image nodes (which in
        turn will be handled by the existing image-based implementation).

        Note that the interactive image map is not handled in this
        implementation since Confluence does not support image maps (without
        external extensions).

        Args:
            doctree: the doctree to replace blocks on
        """
        if inheritance_diagram is None:
            return

        # graphviz's render_dot call expects a translator to be passed in; mock
        # a translator tied to our self-builder
        class MockTranslator:
            def __init__(self, builder):
                self.builder = builder
        mock_translator = MockTranslator(self)

        for node in doctree.traverse(inheritance_diagram.inheritance_diagram):
            graph = node['graph']

            graph_hash = inheritance_diagram.get_graph_hash(node)
            name = 'inheritance%s' % graph_hash

            dotcode = graph.generate_dot(name, {}, env=self.env)

            try:
                _, out_filename = render_dot(mock_translator, dotcode, {},
                    self.graphviz_output_format, 'inheritance')
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

    def _replace_math_blocks(self, doctree):
        """
        replace math blocks with images

        Math blocks are pre-processed and replaced with respective images in the
        list of documents to process. This is to help prepare additional images
        into the asset management for this extension. Math support will work on
        systems which have latex/dvipng installed.

        Args:
            doctree: the doctree to replace blocks on
        """
        if imgmath is None:
            return

        # imgmath's render_math call expects a translator to be passed
        # in; mock a translator tied to our self-builder
        class MockTranslator:
            def __init__(self, builder):
                self.builder = builder
        mock_translator = MockTranslator(self)

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

                mf, _ = imgmath.render_math(mock_translator, latex)
                if not mf:
                    continue

                new_node = nodes.image(
                    candidates={'?'},
                    uri=path.join(self.outdir, mf))
                if not isinstance(node, nodes.math):
                    new_node['align'] = 'center'
                if node.get('number'):
                    new_node['math_number'] = node['number']
                node.replace_self(new_node)
            except imgmath.MathExtError as exc:
                ConfluenceLogger.warn('inline latex {}: {}'.format(
                    node.astext(), exc))

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
