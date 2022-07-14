# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2022 Sphinx Confluence Builder Contributors (AUTHORS)
:copyright: Copyright 2007-2021 by the Sphinx team (sphinx-doc/sphinx#AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from collections import defaultdict
from docutils import nodes
from docutils.io import StringOutput
from os import path
from sphinx import addnodes
from sphinx.builders import Builder
from sphinx.errors import ExtensionError
from sphinx.locale import _ as SL
from sphinx.util import status_iterator
from sphinx.util.osutil import ensuredir
from sphinxcontrib.confluencebuilder.assets import ConfluenceAssetManager
from sphinxcontrib.confluencebuilder.assets import ConfluenceSupportedImages
from sphinxcontrib.confluencebuilder.config import process_ask_configs
from sphinxcontrib.confluencebuilder.config.checks import validate_configuration
from sphinxcontrib.confluencebuilder.config.defaults import apply_defaults
from sphinxcontrib.confluencebuilder.intersphinx import build_intersphinx
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger
from sphinxcontrib.confluencebuilder.nodes import confluence_footer
from sphinxcontrib.confluencebuilder.nodes import confluence_header
from sphinxcontrib.confluencebuilder.nodes import confluence_metadata
from sphinxcontrib.confluencebuilder.nodes import confluence_page_generation_notice
from sphinxcontrib.confluencebuilder.nodes import confluence_source_link
from sphinxcontrib.confluencebuilder.publisher import ConfluencePublisher
from sphinxcontrib.confluencebuilder.state import ConfluenceState
from sphinxcontrib.confluencebuilder.storage.index import generate_storage_format_domainindex
from sphinxcontrib.confluencebuilder.storage.index import generate_storage_format_genindex
from sphinxcontrib.confluencebuilder.storage.search import generate_storage_format_search
from sphinxcontrib.confluencebuilder.storage.translator import ConfluenceStorageFormatTranslator
from sphinxcontrib.confluencebuilder.transmute import doctree_transmute
from sphinxcontrib.confluencebuilder.util import ConfluenceUtil
from sphinxcontrib.confluencebuilder.util import extract_strings_from_file
from sphinxcontrib.confluencebuilder.util import first
from sphinxcontrib.confluencebuilder.writer import ConfluenceWriter
import io

try:
    basestring  # pylint: disable=E0601
except NameError:
    basestring = str


class ConfluenceBuilder(Builder):
    allow_parallel = True
    default_translator_class = ConfluenceStorageFormatTranslator
    name = 'confluence'
    format = 'confluence_storage'
    supported_image_types = ConfluenceSupportedImages()
    supported_remote_images = True

    def __init__(self, app):
        super(ConfluenceBuilder, self).__init__(app)

        self.cache_doctrees = {}
        self.cloud = False
        self.domain_indices = {}
        self.file_suffix = '.conf'
        self.info = ConfluenceLogger.info
        self.link_suffix = None
        self.metadata = defaultdict(dict)
        self.nav_next = {}
        self.nav_prev = {}
        self.omitted_docnames = []
        self.publish_allowlist = []
        self.publish_denylist = []
        self.publish_docnames = []
        self.publisher = ConfluencePublisher()
        self.root_doc_page_id = None
        self.secnumbers = {}
        self.state = ConfluenceState
        self.use_index = None
        self.use_search = None
        self.verbose = ConfluenceLogger.verbose
        self.warn = ConfluenceLogger.warn
        self._cached_footer_data = None
        self._cached_header_data = None
        self._original_get_doctree = None
        self._verbose = self.app.verbosity

        # state tracking is set at initialization (not cleanup) so its content's
        # can be checked/validated on after the builder has executed (testing)
        self.state.reset()

    def init(self):
        validate_configuration(self)
        apply_defaults(self.config)
        config = self.config

        self.add_secnumbers = self.config.confluence_add_secnumbers
        self.secnumber_suffix = self.config.confluence_secnumber_suffix

        if self.name != 'singleconfluence':
            self.use_index = config.confluence_use_index
            self.use_search = config.confluence_include_search

        if self.config.confluence_additional_mime_types:
            for type_ in self.config.confluence_additional_mime_types:
                self.supported_image_types.register(type_)

        if 'graphviz_output_format' in self.config:
            self.graphviz_output_format = self.config['graphviz_output_format']
        else:
            self.graphviz_output_format = 'png'

        if self.config.confluence_publish:
            process_ask_configs(self.config)

        old_url = self.config.confluence_server_url
        new_url = ConfluenceUtil.normalize_base_url(old_url)
        if old_url != new_url:
            self.warn('normalizing confluence url from '
                '{} to {} '.format(old_url, new_url))
            self.config.confluence_server_url = new_url

        # detect if Confluence Cloud if using the Atlassian domain
        if new_url:
            self.cloud = new_url.endswith('.atlassian.net/wiki/')

        self.assets = ConfluenceAssetManager(config, self.env, self.outdir)
        self.writer = ConfluenceWriter(self)
        self.config.sphinx_verbosity = self._verbose
        self.publisher.init(self.config, self.cloud)

        self.create_template_bridge()
        self.templates.init(self)

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
        traversed = [self.config.root_doc]

        # default enable special document names if they are references in the
        # official docnames list
        if self.use_index is None and 'genindex' in docnames:
            self.use_index = True
        if self.use_search is None and 'search' in docnames:
            self.use_search = True

        # generate domain index information
        self.domain_indices = {}
        indices_config = self.config.confluence_domain_indices
        if indices_config and self.name != 'singleconfluence':
            for domain_name in sorted(self.env.domains):
                domain = self.env.domains[domain_name]
                for indexcls in domain.indices:
                    indexname = '%s-%s' % (domain.name, indexcls.name)

                    if isinstance(indices_config, list):
                        if indexname not in indices_config:
                            continue

                    content, _ = indexcls(domain).generate()
                    if content:
                        self.domain_indices[indexname] = (indexcls, content)

        # prepare caching doctree hook
        #
        # We'll temporarily override the environment's 'get_doctree' method to
        # allow this extension to manipulate the doctree for a document inside
        # the pre-writing stage to also take effect in the writing stage.
        self._original_get_doctree = self.env.get_doctree
        self.env.get_doctree = self._get_doctree

        # process the document structure of the root document, allowing:
        #  - populating a publish order to ensure parent pages are created first
        #     (when using hierarchy mode)
        #  - squash pages which exceed maximum depth (if configured with a max
        #     depth value)
        self.process_tree_structure(
            ordered_docnames, self.config.root_doc, traversed)

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

                self.state.register_title(
                    docname, doctitle, self.config, doc_source_path=doctree.attributes['source'],
                    src_dir=self.env.srcdir)

                # only publish documents that sphinx asked to prepare
                if docname in docnames:
                    self.publish_docnames.append(docname)

            # track the toctree depth for a document, which a translator can
            # use as a hint when dealing with max-depth capabilities
            toctree = first(doctree.traverse(addnodes.toctree))
            if toctree and toctree.get('maxdepth') > 0:
                self.state.register_toctree_depth(
                    docname, toctree.get('maxdepth'))

            # register title targets for references
            self._register_doctree_title_targets(docname, doctree)

            # post-prepare a ready doctree
            self._prepare_doctree_writing(docname, doctree)

        # register titles for special documents (if needed); if a title is not
        # already set from a placeholder document, configure a default title
        if self.use_index and not self.state.title('genindex'):
            self.state.register_title('genindex', SL('Index'), self.config)

        if self.use_search and not self.state.title('search'):
            self.state.register_title('search', SL('Search'), self.config)

        if self.domain_indices:
            for indexname, indexdata in self.domain_indices.items():
                if self.state.title(indexname):
                    continue

                indexcls, _ = indexdata
                title = indexcls.localname
                self.state.register_title(indexname, title, self.config)

        # track relations between accepted documents
        #
        # Prepares a relation mapping between each non-orphan documents which
        # can be used by navigational elements. If any documents are special
        # pages, ignore them for consideration in the navigational bar.
        nav_docnames = list(ordered_docnames)

        if self.use_index and 'genindex' in nav_docnames:
            nav_docnames.remove('genindex')

        if self.use_search and 'search' in nav_docnames:
            nav_docnames.remove('search')

        if self.domain_indices:
            for indexname, indexdata in self.domain_indices.items():
                if indexname in nav_docnames:
                    nav_docnames.remove(indexname)

        navdocs_transform = self.config.confluence_navdocs_transform
        if navdocs_transform:
            nav_docnames = navdocs_transform(self, nav_docnames)

        prevdoc = nav_docnames[0] if nav_docnames else None
        for docname in nav_docnames[1:]:
            self.nav_prev[docname] = self.get_relative_uri(docname, prevdoc)
            self.nav_next[prevdoc] = self.get_relative_uri(prevdoc, docname)
            prevdoc = docname

        # register labels for special documents (if needed)
        labels = self.env.domaindata['std']['labels']
        anonlabels = self.env.domaindata['std']['anonlabels']
        if self.use_index:
            anonlabels['genindex'] = 'genindex', ''
            labels['genindex'] = 'genindex', '', ''

        if self.use_search:
            anonlabels['search'] = 'search', ''
            labels['search'] = 'search', '', ''

        if self.domain_indices:
            for indexname, _ in self.domain_indices.items():
                anonlabels[indexname] = indexname, ''
                labels[indexname] = indexname, '', ''

        # Scan for assets that may exist in the documents to be published. This
        # will find most if not all assets in the documentation set. The
        # exception is assets which may be finalized during a document's post
        # transformation stage (e.g. embedded images are converted into real
        # images in Sphinx, which is then provided to a translator). Embedded
        # images and other late-injected assets are processed in a translator
        # when needed.
        if self.name != 'singleconfluence':
            self.assets.process(ordered_docnames)

    def _prepare_doctree_writing(self, docname, doctree):
        # extract metadata information
        self._extract_metadata(docname, doctree)

        # convert any desired nodes in a doctree to node types supported by the
        # translator implementation
        doctree_transmute(self, doctree)

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
                    self.state.register_parent_docname(child, docname)
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

        self._header_footer_init(docname, doctree)

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
                            top_ref = node['refid'] in ids

                            # allow a derived class to hint if this is a #top
                            # reference node
                            if not top_ref:
                                top_ref = self._top_ref_check(node)

                            if top_ref:
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
                self.warn('error writing file %s: %s' % (outfilename, err))

    def publish_doc(self, docname, output):
        conf = self.config
        title = self.state.title(docname)
        is_root_doc = self.config.root_doc == docname

        parent_id = None
        if self.config.root_doc and self.config.confluence_page_hierarchy:
            if self.config.root_doc != docname:
                parent = self.state.parent_docname(docname)
                parent_id = self.state.upload_id(parent)
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

        if conf.confluence_publish_root and is_root_doc:
            uploaded_id = self.publisher.store_page_by_id(title,
                conf.confluence_publish_root, data)
        else:
            uploaded_id = self.publisher.store_page(title, data, parent_id)
        self.state.register_upload_id(docname, uploaded_id)

        if self.config.root_doc == docname:
            self.root_doc_page_id = uploaded_id

            # populate ancestors to be used to pre-check ancestors assignments
            # on new pages (`uploaded_id` may not be set if dry run)
            if uploaded_id:
                root_ancestors = self.publisher.get_ancestors(uploaded_id)
                self.publisher.restrict_ancestors(root_ancestors)

        # if purging is enabled and we have yet to populate a list of legacy
        # pages to cache, populate pages in our target scope now
        if conf.confluence_purge and self.legacy_pages is None:
            if conf.confluence_publish_root:
                baseid = conf.confluence_publish_root
            elif conf.confluence_purge_from_root and self.root_doc_page_id:
                baseid = self.root_doc_page_id
            else:
                baseid = self.parent_id

            # if no base identifier and dry running, ignore legacy page
            # searching as there is no initial root document to reference
            # against
            if (conf.confluence_purge_from_root and
                    conf.confluence_publish_dryrun and not baseid):
                self.legacy_pages = []
            elif self.config.confluence_adv_aggressive_search is True:
                self.legacy_pages = self.publisher.get_descendants_compat(baseid)
            else:
                self.legacy_pages = self.publisher.get_descendants(baseid)

            # only populate a list of possible legacy assets when a user is
            # configured to check or push assets to the target space
            asset_override = conf.confluence_asset_override
            if asset_override is None or asset_override:
                for legacy_page in self.legacy_pages:
                    attachments = self.publisher.get_attachments(legacy_page)
                    self.legacy_assets[legacy_page] = attachments

        if conf.confluence_purge:
            if uploaded_id in self.legacy_pages:
                self.legacy_pages.remove(uploaded_id)

    def publish_asset(self, key, docname, output, type_, hash_):
        conf = self.config
        publisher = self.publisher

        title = self.state.title(docname)
        page_id = self.state.upload_id(docname)

        if not page_id and not conf.confluence_publish_dryrun:
            # A page identifier may not be tracked in cases where only a subset
            # of documents are published and the target page an asset will be
            # published to was not part of the request. In this case, ask the
            # Confluence instance what the target page's identifier is.
            page_id, _ = publisher.get_page(title)
            if page_id:
                self.state.register_upload_id(docname, page_id)
            else:
                self.warn('cannot publish asset since publishing '
                    'point cannot be found ({}): {}'.format(key, docname))
                return

        attachment_id = None

        if conf.confluence_asset_override is None:
            # "automatic" management -- check if already published; if not, push
            attachment_id = publisher.store_attachment(
                page_id, key, output, type_, hash_)
        elif conf.confluence_asset_override:
            # forced publishing of the asset
            attachment_id = publisher.store_attachment(
                page_id, key, output, type_, hash_, force=True)

        if attachment_id and conf.confluence_purge:
            if page_id in self.legacy_assets:
                legacy_asset_info = self.legacy_assets[page_id]
                if attachment_id in legacy_asset_info:
                    legacy_asset_info.pop(attachment_id, None)

    def publish_finalize(self):
        if self.root_doc_page_id:
            if self.config.confluence_root_homepage is True:
                self.info('updating space\'s homepage... ',
                    nonl=(not self._verbose))
                self.publisher.update_space_home(self.root_doc_page_id)
                self.info('done')

            if self.cloud:
                point_url = '{0}spaces/{1}/pages/{2}'
            else:
                point_url = '{0}pages/viewpage.action?pageId={2}'

            self.info('Publish point: ' + point_url.format(
                self.config.confluence_server_url,
                self.config.confluence_space_key,
                self.root_doc_page_id))

    def publish_purge(self):
        if self.config.confluence_purge:
            if self.publish_allowlist or self.publish_denylist:
                self.warn('confluence_purge disabled due to '
                    'confluence_publish_allowlist/confluence_publish_denylist')
                return

            if self.legacy_pages:
                for legacy_page_id in status_iterator(
                        self.legacy_pages, 'removing legacy pages... ',
                        length=len(self.legacy_pages),
                        verbosity=self._verbose):
                    self.publisher.remove_page(legacy_page_id)
                    # remove any pending assets to remove from the page (as they
                    # are already been removed)
                    self.legacy_assets.pop(legacy_page_id, None)

            legacy_assets = {}
            for legacy_asset_info in self.legacy_assets.values():
                for attachment_id, attachment_name in legacy_asset_info.items():
                    legacy_assets[attachment_id] = attachment_name

            if legacy_assets:
                def to_asset_name(attachment_id):
                    return legacy_assets[attachment_id]

                for attachment_id in status_iterator(
                        legacy_assets.keys(),
                        'removing legacy assets... ',
                        length=len(legacy_assets.keys()),
                        verbosity=self._verbose,
                        stringify_func=to_asset_name):

                    self.publisher.remove_attachment(attachment_id)

    def finish(self):
        # restore environment's get_doctree if it was temporarily replaced
        if self._original_get_doctree:
            self.env.get_doctree = self._original_get_doctree

        # build index
        if self.use_index:
            self.info('generating index...', nonl=(not self._verbose))

            self._generate_special_document('genindex',
                generate_storage_format_genindex)

            if not self._verbose:
                self.info(' done')

        # build domain indexes
        if self.domain_indices:
            for indexname, indexdata in self.domain_indices.items():
                self.info('generating index ({})...'.format(indexname),
                    nonl=(not self._verbose))

                self._generate_special_document(indexname,
                    generate_storage_format_domainindex)

                if not self._verbose:
                    self.info(' done')

        # build search
        if self.use_search:
            self.info('generating search...', nonl=(not self._verbose))

            self._generate_special_document('search',
                generate_storage_format_search)

            if not self._verbose:
                self.info(' done')

        # publish generated output (if desired)
        if self.publish:
            self.legacy_assets = {}
            self.legacy_pages = None
            self.parent_id = self.publisher.get_base_page_id()

            for docname in status_iterator(
                    self.publish_docnames, 'publishing documents... ',
                    length=len(self.publish_docnames),
                    verbosity=self._verbose):
                if self._check_publish_skip(docname):
                    self.verbose(docname + ' skipped due to configuration')
                    continue
                docfile = path.join(self.outdir, self.file_transform(docname))

                try:
                    with io.open(docfile, 'r', encoding='utf-8') as file:
                        output = file.read()
                        self.publish_doc(docname, output)

                except (IOError, OSError) as err:
                    self.warn('error reading file %s: %s' % (docfile, err))

            def to_asset_name(asset):
                return asset[0]

            assets = self.assets.build()
            for asset in status_iterator(assets, 'publishing assets... ',
                    length=len(assets), verbosity=self._verbose,
                    stringify_func=to_asset_name):
                key, absfile, type_, hash_, docname = asset
                if self._check_publish_skip(docname):
                    self.verbose(key + ' skipped due to configuration')
                    continue

                try:
                    with open(absfile, 'rb') as file:
                        output = file.read()
                        self.publish_asset(key, docname, output, type_, hash_)
                except (IOError, OSError) as err:
                    self.warn('error reading asset %s: %s' % (key, err))

            self.publish_purge()
            self.publish_finalize()

            self.info('building intersphinx... ', nonl=(not self._verbose))
            build_intersphinx(self)
            self.info('done')

    def cleanup(self):
        if self.publish:
            self.publisher.disconnect()

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
            labels.extend(node.params['labels'])
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
        if 'citations' in std_domain.data:  # Sphinx <2.1
            citations = std_domain.data['citations']
        elif citation_domain:  # Sphinx >=2.1
            citations = citation_domain.citations
        if citations:
            for key, (fn, _l, _) in list(citations.items()):
                if fn == olddocname:
                    data = citations[key]
                    citations[key] = newdocname, data[1], data[2]

        if 'citation_refs' in std_domain.data:  # Sphinx <2.0
            citation_refs = std_domain.data['citation_refs']
            for key, _ in list(citation_refs.items()):
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

    def _generate_special_document(self, docname, generator):
        """
        generate a special document

        Provides support to generate the contents of a document for Sphinx
        "special" documents -- specifically, genindex, search and domain index
        documents.

        Args:
            docname: the docname to generate
            generator: instance which will generate content for a file
        """

        # register document if its not already registered for publishing
        # (i.e. placeholder documents)
        if docname not in self.publish_docnames:
            self.publish_docnames.append(docname)

        # render and cache header data (if any)
        if self._cached_header_data is None:
            self._cached_header_data = ''
            header_template_data = ''

            if self.config.confluence_header_file is not None:
                fname = path.join(self.env.srcdir,
                    self.config.confluence_header_file)
                try:
                    with io.open(fname, encoding='utf-8') as file:
                        header_template_data = file.read() + '\n'
                except (IOError, OSError) as err:
                    self.warn('error reading file {}: {}'.format(fname, err))

                # if no data is supplied, the file is plain text
                if self.config.confluence_header_data is None:
                    self._cached_header_data = header_template_data
                else:
                    self._cached_header_data = self.templates.render_string(
                        header_template_data,
                        self.config.confluence_header_data)

        # render and cache footer data (if any)
        if self._cached_footer_data is None:
            self._cached_footer_data = ''
            footer_template_data = ''

            if self.config.confluence_footer_file is not None:
                fname = path.join(self.env.srcdir,
                    self.config.confluence_footer_file)
                try:
                    with io.open(fname, encoding='utf-8') as file:
                        footer_template_data = file.read() + '\n'
                except (IOError, OSError) as err:
                    self.warn('error reading file {}: {}'.format(fname, err))

                # if no data is supplied, the file is plain text
                if self.config.confluence_footer_data is None:
                    self._cached_footer_data = footer_template_data
                else:
                    self._cached_header_data = self.templates.render_string(
                        footer_template_data,
                        self.config.confluence_footer_data)

        # generate/replace the document in the output directory
        fname = path.join(self.outdir, docname + self.file_suffix)
        try:
            with io.open(fname, 'w', encoding='utf-8') as f:
                f.write(self._cached_header_data)
                generator(self, docname, f)
                f.write(self._cached_footer_data)
        except (IOError, OSError) as err:
            self.warn('error writing file %s: %s', docname, err)

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

    def _header_footer_init(self, docname, doctree):
        """
        initialize header/footer nodes (if needed) for a document

        Generates header/footers nodes and injects them into a provided doctree.

        Args:
            docname: the document name
            doctree: the doctree
        """

        add_header_node = False
        add_footer_node = False

        header_node = confluence_header()
        footer_node = confluence_footer()

        prev_next_loc = self.config.confluence_prev_next_buttons_location

        # add source link
        if self.config.confluence_sourcelink:
            default_host = ''
            default_view = 'blob'

            sourcelink = dict(self.config.confluence_sourcelink)
            if 'url' not in sourcelink:
                url_base = '{protocol}://{host}/{owner}/{repo}/'

                source_type = sourcelink.get('type')
                if source_type == 'bitbucket':
                    default_host = 'bitbucket.org'
                    default_view = 'view'
                    url = 'src/{version}/{container}{page}{suffix}?mode={view}'
                elif source_type == 'github':
                    default_host = 'github.com'
                    url = '{view}/{version}/{container}{page}{suffix}'
                elif source_type == 'gitlab':
                    default_host = 'gitlab.com'
                    url = '{view}/{version}/{container}{page}{suffix}'
                else:
                    # unsupported source type should not pass here after this
                    # extension's configuration check
                    assert False

                sourcelink['url'] = url_base + url

            sourcelink.setdefault('container', '')
            sourcelink.setdefault('protocol', 'https')
            sourcelink.setdefault('host', default_host)
            sourcelink.setdefault('view', default_view)

            es_node = confluence_source_link()
            es_node.params.update(sourcelink)
            header_node.append(es_node)
            add_header_node = True

        # add page generation notice
        if self.config.confluence_page_generation_notice:
            pgn_node = confluence_page_generation_notice()
            header_node.append(pgn_node)
            add_header_node = True

        # add header next/previous
        if prev_next_loc in ('top', 'both'):
            if self._header_footer_inject_navnode(docname, header_node):
                add_header_node = True

        # add footer next/previous
        if prev_next_loc in ('bottom', 'both'):
            if self._header_footer_inject_navnode(docname, footer_node):
                add_footer_node = True

        # inject header/footer nodes into doctree if there is content to add
        if add_header_node:
            doctree.insert(0, header_node)

        if add_footer_node:
            doctree.append(footer_node)

    def _header_footer_inject_navnode(self, docname, node):
        """
        inject navigational nodes for a document's header/footer node

        Requests to build a navigation nodes for a provided document name to be
        added into a provided header/footer node. If this document has no
        navigational hints to apply, this method has no effect.

        Args:
            docname: the document name
            node: the node to inject navigational nodes into

        Returns:
            whether or not any nodes have been injected
        """

        if docname not in self.nav_prev and docname not in self.nav_next:
            return False

        if docname in self.nav_prev:
            prev_label = '← ' + SL('Previous')
            reference = nodes.reference(prev_label, prev_label, internal=True,
                refuri=self.nav_prev[docname])
            reference._navnode = True
            reference._navnode_next = False
            reference._navnode_previous = True
            node.append(reference)

        if docname in self.nav_next:
            next_label = SL('Next') + ' →'
            reference = nodes.reference(next_label, next_label, internal=True,
                refuri=self.nav_next[docname])
            reference._navnode = True
            reference._navnode_next = True
            reference._navnode_previous = False
            node.append(reference)

        return True

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

                    if self.add_secnumbers:
                        anchorname = '#' + section_node['ids'][0]
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

                    for id_ in section_node['ids']:
                        id_ = '{}#{}'.format(docname, id_)
                        self.state.register_target(id_, target)

    def _top_ref_check(self, node):
        """
        report if the provided node is consider a #top reference

        Allows an implementer extending this call to provide a hint if the
        provided reference node is to be considered a "#top" reference.

        Args:
            node: the node to check

        Returns:
            whether or not the node should be a #top reference
        """
        return False

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
                    self.warn('document will be published using an '
                        'generated title value: {}'.format(docname))
            elif self.publish:
                self.warn('document will not be published since it '
                    'has no title: {}'.format(docname))

        return doctitle
