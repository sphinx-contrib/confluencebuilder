# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)
# Copyright 2007-2021 by the Sphinx team (sphinx-doc/sphinx#AUTHORS)

from collections import defaultdict
from docutils import nodes
from docutils.io import StringOutput
from pathlib import Path
from sphinx import addnodes
from sphinx.builders import Builder
from sphinx.locale import _ as SL
from sphinx.util.display import status_iterator
from sphinxcontrib.confluencebuilder.assets import ConfluenceAssetManager
from sphinxcontrib.confluencebuilder.compat import docutils_findall as findall
from sphinxcontrib.confluencebuilder.config import process_ask_configs
from sphinxcontrib.confluencebuilder.config.checks import validate_configuration
from sphinxcontrib.confluencebuilder.config.defaults import apply_defaults
from sphinxcontrib.confluencebuilder.config.env import apply_env_overrides
from sphinxcontrib.confluencebuilder.config.env import build_hash
from sphinxcontrib.confluencebuilder.env import ConfluenceCacheInfo
from sphinxcontrib.confluencebuilder.intersphinx import build_intersphinx
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger
from sphinxcontrib.confluencebuilder.manifest import ConfluenceManifest
from sphinxcontrib.confluencebuilder.nodes import confluence_footer
from sphinxcontrib.confluencebuilder.nodes import confluence_header
from sphinxcontrib.confluencebuilder.nodes import confluence_metadata
from sphinxcontrib.confluencebuilder.nodes import confluence_page_generation_notice
from sphinxcontrib.confluencebuilder.nodes import confluence_source_link
from sphinxcontrib.confluencebuilder.nodes import confluence_parameters_fetch as PARAMS
from sphinxcontrib.confluencebuilder.publisher import ConfluencePublisher
from sphinxcontrib.confluencebuilder.state import ConfluenceState
from sphinxcontrib.confluencebuilder.std.confluence import CONFLUENCE_MAX_WIDTH
from sphinxcontrib.confluencebuilder.std.confluence import SUPPORTED_IMAGE_TYPES
from sphinxcontrib.confluencebuilder.storage.index import generate_storage_format_domainindex
from sphinxcontrib.confluencebuilder.storage.index import generate_storage_format_genindex
from sphinxcontrib.confluencebuilder.storage.search import generate_storage_format_search
from sphinxcontrib.confluencebuilder.storage.translator import ConfluenceStorageFormatTranslator
from sphinxcontrib.confluencebuilder.transmute import doctree_transmute
from sphinxcontrib.confluencebuilder.util import ConfluenceUtil
from sphinxcontrib.confluencebuilder.util import detect_cloud
from sphinxcontrib.confluencebuilder.util import extract_strings_from_file
from sphinxcontrib.confluencebuilder.util import first
from sphinxcontrib.confluencebuilder.util import handle_cli_file_subset
from sphinxcontrib.confluencebuilder.writer import ConfluenceWriter
from urllib.parse import quote
import os
import tempfile
import time


class ConfluenceBuilder(Builder):
    allow_parallel = True
    default_translator_class = ConfluenceStorageFormatTranslator
    name = 'confluence'
    format = 'confluence_storage'
    supported_image_types = SUPPORTED_IMAGE_TYPES
    supported_linkcode = name
    supported_remote_images = True

    def __init__(self, app, env=None):
        super().__init__(app, env)

        self.cache_doctrees = {}
        self.cloud = False
        self.domain_indices = {}
        self.file_suffix = '.conf'
        self.info = ConfluenceLogger.info
        self.legacy_assets = {}
        self.legacy_pages = None
        self.link_suffix = None
        self.metadata = defaultdict(dict)
        self.nav_next = {}
        self.nav_prev = {}
        self.note = ConfluenceLogger.note
        self.omitted_docnames = []
        self.orphan_docnames = []
        self.out_dir = Path(self.outdir)
        self.parent_id = None
        self.publish_allowlist = None
        self.publish_denylist = None
        self.publish_docnames = []
        self.publisher = ConfluencePublisher()
        self.root_doc_page_id = None
        self.secnumbers = {}
        self.state = ConfluenceState
        self.use_index = None
        self.use_search = None
        self.verbose = ConfluenceLogger.verbose
        self.warn = ConfluenceLogger.warn
        self._cache_info = ConfluenceCacheInfo(self)
        self._cached_footer_data = None
        self._cached_header_data = None
        self._config_confluence_hash = None
        self._original_get_doctree = None
        self._verbose = self.app.verbosity

        self.manifest = ConfluenceManifest(self.config, self.state)

        # state tracking is set at initialization (not cleanup) so its content's
        # can be checked/validated on after the builder has executed (testing)
        self.state.reset()

    def init(self):
        apply_env_overrides(self)
        validate_configuration(self)
        apply_defaults(self)
        config = self.config

        # populate desired metadata into the manifest after the configuration
        # has been finalized
        self.manifest.register_metadata()

        self.add_secnumbers = self.config.confluence_add_secnumbers
        self.secnumber_suffix = self.config.confluence_secnumber_suffix
        self.post_cleanup = config.confluence_cleanup_purge or \
            config.confluence_cleanup_archive

        if self.name != 'singleconfluence':
            self.use_index = config.confluence_use_index
            self.use_search = config.confluence_include_search

        if self.config.confluence_additional_mime_types:
            for type_ in self.config.confluence_additional_mime_types:
                if type_ not in self.supported_image_types:
                    self.supported_image_types.append(type_)

        if 'graphviz_output_format' in self.config:  # noqa: SIM401
            self.graphviz_output_format = self.config['graphviz_output_format']
        else:
            self.graphviz_output_format = 'png'

        # For users building with Windows and using `dvisvgm` from MiKTeX, the
        # process may fail when dealing with temporary file locations that do
        # not share a common partition as the output directory.
        #
        #  ERROR: Windows API error 87: The parameter is incorrect.
        #
        # The imgmath extension allows a builder to override where temporary
        # files are build -- use this to hint to using a temporary directory
        # on the same partition the output directory to help prevent issues.
        self._imgmath_tempdir = Path(tempfile.mkdtemp(
            prefix='.imgmath-', dir=self.out_dir))

        if self.config.confluence_publish:
            process_ask_configs(self.config)

        old_url = self.config.confluence_server_url
        new_url = ConfluenceUtil.normalize_base_url(old_url)
        if old_url != new_url:
            self.warn(f'normalizing confluence url from {old_url} to {new_url}')
            self.config.confluence_server_url = new_url

        # track if operating with a Confluence Cloud target
        if self.config.confluence_adv_cloud is not None:
            self.cloud = self.config.confluence_adv_cloud
        else:
            self.cloud = detect_cloud(new_url)

        self.assets = ConfluenceAssetManager(config, self.env, self.out_dir)
        self.writer = ConfluenceWriter(self)
        self.config.sphinx_verbosity = self._verbose
        self.publisher.init(self.config, self.cloud)

        # With the configuration finalizes, generate a Confluence-specific
        # configuration hash that is applicable to this run
        self._config_confluence_hash = build_hash(config)
        self.verbose('configuration hash ' + self._config_confluence_hash)

        self._cache_info.load_cache()
        self._cache_info.configure(self._config_confluence_hash)

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

        self.file_transform = file_transform
        self.link_transform = link_transform

        if self.config.confluence_lang_overrides is not None:
            if isinstance(self.config.confluence_lang_overrides, dict):
                def lang_transform(lang):
                    return self.config.confluence_lang_overrides.get(lang)

                self.lang_transform = lang_transform
            else:
                self.lang_transform = self.config.confluence_lang_overrides
        else:
            self.lang_transform = None

        if self.config.confluence_publish:
            self.publish = True
            self.publisher.connect()
        else:
            self.publish = False

        def prepare_subset(option):
            value = getattr(config, option)
            if value is None:
                return None

            value = handle_cli_file_subset(self, option, value)
            if value is None:
                return None

            if isinstance(value, (str, os.PathLike)):
                files = extract_strings_from_file(value)
            else:
                files = value

            return set(files)

        self.publish_allowlist = prepare_subset('confluence_publish_allowlist')
        self.publish_denylist = prepare_subset('confluence_publish_denylist')

    def get_outdated_docs(self):
        """
        Return an iterable of input files that are outdated.
        """

        for docname in self.env.found_docs:
            if self._cache_info.is_outdated(docname):
                yield docname
                continue

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
                    indexname = f'{domain.name}-{indexcls.name}'

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

        # TMPFIX: as of Sphinx v6.1.x, doctrees can be cached when first
        # written, which can prevent manipulating them between the doctree
        # (pickle) write state and re-reading them later (specifically, this
        # extension's means of manipulation) -- for now, if we detect the
        # environment is performing any doctree caching, clear the entire
        # cache
        if getattr(self.env, '_write_doc_doctree_cache', None):
            self.env._write_doc_doctree_cache = {}  # noqa: SLF001

        # process the document structure of the root document, populating a
        # publish order to ensure parent pages are created first (when using
        # hierarchy mode)
        self.process_tree_structure(
            ordered_docnames, self.config.root_doc, traversed)

        # add orphans (if any) to the publish list
        if self.config.confluence_publish_orphan:
            self.orphan_docnames = [x for x in docnames if x not in traversed]
            ordered_docnames.extend(self.orphan_docnames)

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

                self.state.register_title(docname, doctitle, self.config)

                # only publish documents that sphinx asked to prepare
                if docname in docnames:
                    self.publish_docnames.append(docname)

            # track the toctree depth for a document, which a translator can
            # use as a hint when dealing with max-depth capabilities
            toctree = first(findall(doctree, addnodes.toctree))
            if toctree and toctree.get('maxdepth') > 0:
                self.state.register_toctree_depth(
                    docname, toctree.get('maxdepth'))

            # post-prepare a ready doctree
            self._prepare_doctree_writing(docname, doctree)

            # register targets for references
            self._register_doctree_targets(docname, doctree)

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
            for indexname in self.domain_indices:
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
            for indexname in self.domain_indices:
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

    def process_tree_structure(self, ordered, docname, traversed):
        ordered.append(docname)

        doctree = self.env.get_doctree(docname)
        for toctreenode in findall(doctree, addnodes.toctree):
            for child in toctreenode['includefiles']:
                if child not in traversed:
                    self.state.register_parent_docname(child, docname)
                    traversed.append(child)

                    self.process_tree_structure(ordered, child, traversed)

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
                    for node in findall(doctree, nodes.reference):
                        if node.get('refid'):
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
        out_file = self.out_dir / self.file_transform(docname)
        if self.writer.output is not None:
            out_file.parent.mkdir(parents=True, exist_ok=True)
            try:
                with out_file.open('w', encoding='utf-8') as file:
                    if self.writer.output:
                        file.write(self.writer.output)
            except OSError as err:
                self.warn(f'error writing file {out_file}: {err}')
            else:
                self.manifest.add_page(
                    docname, self.writer.output, out_file, self.out_dir)

        self._cache_info.track_page_hash(docname)

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

            # if a custom orphan root has been configured and this is an orphan
            # page, override the parent to publish under; either the provided
            # orphan root ID or no parent (zero value)
            orphan_root_id = conf.confluence_publish_orphan_container
            if orphan_root_id is not None:
                if docname in self.orphan_docnames:
                    parent_id = orphan_root_id

        data = self._prepare_page_data(docname, output)

        metadata = self.metadata.get(docname, {})
        docguid = metadata.get('guid')

        forced_page_id = self.app.emit_firstresult(
            'confluence-publish-override-pageid', docname, {
                'guid': docguid,
                'title': title,
            })

        if forced_page_id:
            uploaded_id = self.publisher.store_page_by_id(title,
                forced_page_id, data)
        elif conf.confluence_publish_root and is_root_doc:
            uploaded_id = self.publisher.store_page_by_id(title,
                conf.confluence_publish_root, data)
        else:
            po_transform = conf.confluence_parent_override_transform
            if po_transform:
                new_parent_id = po_transform(docname, parent_id)
                if new_parent_id:
                    parent_id = new_parent_id

            uploaded_id = self.publisher.store_page(title, data, parent_id)
        self.state.register_upload_id(docname, uploaded_id)

        self._cache_info.track_last_page_id(docname, uploaded_id)

        if self.config.root_doc == docname:
            self.root_doc_page_id = uploaded_id

            # populate ancestors to be used to pre-check ancestors assignments
            # on new pages (`uploaded_id` may not be set if dry run)
            if uploaded_id:
                root_ancestors = self.publisher.get_ancestors(uploaded_id)
                self.publisher.restrict_ancestors(root_ancestors)

        # if purging is enabled and we have yet to populate a list of legacy
        # pages to cache, populate pages in our target scope now
        if self.post_cleanup and self.legacy_pages is None:
            # flag for newlining any note events needed for cleanup
            extra_msg = False

            if conf.confluence_publish_root:
                baseid = conf.confluence_publish_root
            elif conf.confluence_cleanup_from_root:
                baseid = self.root_doc_page_id
            else:
                baseid = self.parent_id

            # if no base identifier and dry running, ignore legacy page
            # searching as there is no initial root document to reference
            # against
            if (conf.confluence_cleanup_from_root and
                    conf.confluence_publish_dryrun and not baseid):
                self.legacy_pages = []
            else:
                if not extra_msg and not self._verbose:
                    self.note('')

                self.note('querying for descendants... ',
                    nonl=(not self._verbose))
                self.legacy_pages = self.publisher.get_descendants(
                    baseid, conf.confluence_cleanup_search_mode)
                if not self._verbose:
                    self.info('done')

                extra_msg = True

            # remove any configured orphan root id from a cleanup check
            orphan_root_id = str(conf.confluence_publish_orphan_container)
            if conf.confluence_publish_orphan and orphan_root_id:
                if orphan_root_id in self.legacy_pages:
                    self.legacy_pages.remove(orphan_root_id)

            # only populate a list of possible legacy assets when a user is
            # configured to check or push assets to the target space
            asset_override = conf.confluence_asset_override
            if self.legacy_pages and (asset_override is None or asset_override):
                if not extra_msg and not self._verbose:
                    self.note('')

                for legacy_page in status_iterator(
                        sorted(self.legacy_pages),
                        'querying for attachments... ',
                        length=len(self.legacy_pages),
                        verbosity=self._verbose):
                    attachments = self.publisher.get_attachments(legacy_page)
                    self.legacy_assets[legacy_page] = attachments

                    # unknown cause but using a nested status_iterator appears
                    # to not flush log events to users standard output without
                    # sleeping -- not sure if its the logger, a threading/gil
                    # situation with this implementation or more -- although
                    # looks if we wait a moment, logging works as expected
                    time.sleep(0.1)

        if self.post_cleanup:
            if uploaded_id in self.legacy_pages:
                self.legacy_pages.remove(uploaded_id)

        if uploaded_id:
            self.app.emit('confluence-publish-page', docname, uploaded_id, {
                'guid': docguid,
                'title': title,
            })

    def _prepare_page_data(self, docname, output):
        data = {
            'content': output,
            'editor': self.config.confluence_editor,
            'full-width': None,
            'labels': [],
        }
        metadata = self.metadata[docname]

        # apply editor override (if any)
        if 'editor' in metadata and self.name != 'singleconfluence':
            data['editor'] = metadata['editor']

        # determine appearance
        #
        # Note: we do not have an "OFF" for v1 editor since an
        # appearance hint is ignored; width management in this
        # case is managed in the translator
        if 'fullWidth' in metadata and self.name != 'singleconfluence':
            confluence_full_width = (metadata['fullWidth'] == 'true')
        else:
            confluence_full_width = self.config.confluence_full_width

        if confluence_full_width:
            data['full-width'] = 'full-width'
        else:
            data['full-width'] = 'default'

        # add global labels and page-specific labels
        if self.config.confluence_global_labels:
            data['labels'].extend(self.config.confluence_global_labels)

        if 'labels' in metadata:
            data['labels'].extend(list(metadata['labels']))

        return data

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
                    f'point cannot be found ({key}): {docname}')
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

        if attachment_id and self.post_cleanup:
            if page_id in self.legacy_assets:
                legacy_asset_info = self.legacy_assets[page_id]
                if attachment_id in legacy_asset_info:
                    legacy_asset_info.pop(attachment_id, None)

        if attachment_id:
            self.app.emit('confluence-publish-attachment',
                docname, key, attachment_id, {
                'hash': hash_,
                'type': type_,
            })

    def publish_finalize(self):
        if self.root_doc_page_id:
            if self.config.confluence_root_homepage is True:
                self.info('updating space\'s homepage... ',
                    nonl=(not self._verbose))
                self.publisher.update_space_home(self.root_doc_page_id)
                if not self._verbose:
                    self.info('done')

            if self.cloud:
                point_url_fmt = '{0}spaces/{1}/pages/{2}'
            else:
                point_url_fmt = '{0}pages/viewpage.action?pageId={2}'

            point_url = point_url_fmt.format(
                self.config.confluence_server_url,
                self.config.confluence_space_key,
                self.root_doc_page_id)

            self.info('Publish point: ' + point_url)
            self.app.emit('confluence-publish-point', point_url)

    def publish_cleanup(self):
        # check if archive cleanup is enabled
        if self.config.confluence_cleanup_archive:
            if self.publish_allowlist or self.publish_denylist:
                self.warn('confluence_cleanup_archive disabled due to '
                    'confluence_publish_allowlist/confluence_publish_denylist')
                return

            if self.legacy_pages:
                if self.config.confluence_adv_bulk_archiving:
                    print('archiving legacy pages...')
                    self.publisher.archive_pages(self.legacy_pages)
                else:
                    for legacy_page_id in status_iterator(
                            self.legacy_pages, 'archiving legacy pages... ',
                            length=len(self.legacy_pages),
                            verbosity=self._verbose):
                        self.publisher.archive_page(legacy_page_id)

        # check if purging is enabled
        if self.config.confluence_cleanup_purge:
            if self.publish_allowlist or self.publish_denylist:
                self.warn('confluence_cleanup_purge disabled due to '
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
                legacy_assets.update(legacy_asset_info)

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
            for indexname in self.domain_indices:
                self.info(f'generating index ({indexname})...',
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
            self.parent_id = self.publisher.get_base_page_id()

            for docname in status_iterator(
                    self.publish_docnames, 'publishing documents... ',
                    length=len(self.publish_docnames),
                    verbosity=self._verbose):
                if self._check_publish_skip(docname):
                    self.verbose(docname + ' skipped due to configuration')
                    continue
                docfile = self.out_dir / self.file_transform(docname)

                try:
                    with docfile.open(encoding='utf-8') as file:
                        output = file.read()
                        self.publish_doc(docname, output)
                except OSError as err:
                    self.warn(f'error reading file {docfile}: {err}')

            self.info('building intersphinx... ', nonl=(not self._verbose))
            build_intersphinx(self)
            if not self._verbose:
                self.info('done')

            if self.config.confluence_publish_intersphinx:
                inventory_db = self.out_dir / 'objects.inv'
                if inventory_db.is_file():
                    self.verbose('registering intersphinx database attachment')
                    self.assets.add(str(inventory_db), self.config.root_doc)
                else:
                    self.verbose('no generated intersphinx database detected')

            def to_asset_name(asset):
                return asset[0]

            assets = self.assets.build()
            for asset in status_iterator(assets, 'publishing assets... ',
                    length=len(assets), verbosity=self._verbose,
                    stringify_func=to_asset_name):
                key, abs_file, type_, hash_, docname = asset
                if self._check_publish_skip(docname):
                    self.verbose(key + ' skipped due to configuration')
                    continue

                try:
                    with abs_file.open('rb') as file:
                        output = file.read()
                        self.publish_asset(key, docname, output, type_, hash_)
                except OSError as err:
                    self.warn(f'error reading asset {key}: {err}')

            # if we have documents that were not changed (and therefore, not
            # needing to be republished), assume any cached publish page ids
            # are still valid and remove them from the legacy pages list
            if self.legacy_pages:
                all_docnames = self.env.all_docs.keys()
                other_docnames = all_docnames - set(self.publish_docnames)
                for unchanged_docname in other_docnames:
                    lpid = self._cache_info.last_page_id(unchanged_docname)
                    if lpid is not None and lpid in self.legacy_pages:
                        self.legacy_pages.remove(lpid)

            self.publish_cleanup()
            self.publish_finalize()
        else:
            assets = self.assets.build()

        # track all referenced assets into the manifest
        for asset in assets:
            key, abs_file, mime, hash_, docname = asset
            self.manifest.add_attachment(
                docname, key, mime, hash_, Path(abs_file), self.out_dir)

        # output the manifest into the output directory
        self.info('building manifest...', nonl=(not self._verbose))
        self.manifest.export(self.out_dir)
        if not self._verbose:
            self.info(' done')

        # persist cache from this run
        self._cache_info.save_cache()

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

        if self.publish_allowlist is not None and \
                docname not in self.publish_allowlist:
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

        for node in findall(doctree, confluence_metadata):
            for k, v in PARAMS(node).items():
                if k == 'labels':
                    labels = metadata.setdefault('labels', [])
                    labels.extend(v)
                else:
                    metadata[k] = v

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
                header_file = Path(self.env.srcdir,
                    self.config.confluence_header_file)
                try:
                    with header_file.open(encoding='utf-8') as file:
                        header_template_data = file.read() + '\n'
                except OSError as err:
                    self.warn(f'error reading file {header_file}: {err}')

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
                footer_file = Path(self.env.srcdir,
                    self.config.confluence_footer_file)
                try:
                    with footer_file.open(encoding='utf-8') as file:
                        footer_template_data = file.read() + '\n'
                except OSError as err:
                    self.warn(f'error reading file {footer_file}: {err}')

                # if no data is supplied, the file is plain text
                if self.config.confluence_footer_data is None:
                    self._cached_footer_data = footer_template_data
                else:
                    self._cached_header_data = self.templates.render_string(
                        footer_template_data,
                        self.config.confluence_footer_data)

        # generate/replace the document in the output directory
        is_v2 = self.config.confluence_editor == 'v2'
        is_wrapped = self.config.confluence_full_width is False
        out_file = self.out_dir / (docname + self.file_suffix)
        try:
            with out_file.open('w', encoding='utf-8') as f:
                f.write(self._cached_header_data)

                # add fixed width if not configured for full width on v1
                # (see also: ConfluenceStorageFormatTranslator.pre_body_data)
                if is_wrapped and not is_v2:
                    if self.cloud:
                        wrap_pre = (
                            '<ac:layout>'
                            '<ac:layout-section ac:type="fixed-width">'
                            '<ac:layout-cell>'
                        )
                    else:
                        max_width = f'{CONFLUENCE_MAX_WIDTH}px'
                        wrap_pre = (
                            '<div style="max-width: '
                            f'{max_width}; margin: 0 auto;">'
                        )
                    f.write(wrap_pre)

                generator(self, docname, f)

                if is_wrapped and not is_v2:
                    if self.cloud:
                        wrap_post = (
                            '</ac:layout-cell>'
                            '</ac:layout-section>'
                            '</ac:layout>'
                        )
                    else:
                        wrap_post = '</div>'
                    f.write(wrap_post)

                f.write(self._cached_footer_data)
        except OSError as err:
            self.warn('error writing file %s: %s', docname, err)

    def _get_doctree(self, docname):
        """
        override 'get_doctree' method

        To support document editing, doctree's may be loaded and manipulated
        before the writing stage. Normally, the writing stage will load target
        doctree's from their source so there is no way to pre-load and pass a
        document's doctree into the writing stage. To overcome this, this
        extension hooks into the environment's 'get_doctree' method and
        caches loaded document's doctree's into a map.
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

        # add page generation notice (first; if v2)
        if self.config.confluence_editor == 'v2':
            if self.config.confluence_page_generation_notice:
                pgn_node = confluence_page_generation_notice()
                header_node.append(pgn_node)
                add_header_node = True

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
                elif source_type == 'codeberg':
                    default_host = 'codeberg.org'
                    url = 'src/{version}/{container}{page}{suffix}'
                elif source_type == 'github':
                    default_host = 'github.com'
                    url = '{view}/{version}/{container}{page}{suffix}'
                elif source_type == 'gitlab':
                    default_host = 'gitlab.com'
                    url = '{view}/{version}/{container}{page}{suffix}'
                else:
                    # unsupported source type should not pass here after this
                    # extension's configuration check
                    msg = 'unsupported source type'
                    raise AssertionError(msg)

                sourcelink['url'] = url_base + url

            sourcelink.setdefault('container', '')
            sourcelink.setdefault('protocol', 'https')
            sourcelink.setdefault('host', default_host)
            sourcelink.setdefault('view', default_view)

            es_node = confluence_source_link()
            PARAMS(es_node).update(sourcelink)
            header_node.append(es_node)
            add_header_node = True

        # add page generation notice (second; if not v2)
        if self.config.confluence_editor != 'v2':
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
            reference.cbe_navnode = True
            reference.cbe_navnode_next = False
            reference.cbe_navnode_previous = True
            node.append(reference)

        if docname in self.nav_next:
            next_label = SL('Next') + ' →'
            reference = nodes.reference(next_label, next_label, internal=True,
                refuri=self.nav_next[docname])
            reference.cbe_navnode = True
            reference.cbe_navnode_next = True
            reference.cbe_navnode_previous = False
            node.append(reference)

        return True

    def _register_doctree_targets(self, docname, doctree, title_track=None):
        """
        register targets for a doctree

        Compiles a list of targets which references can link against. This
        tracked expected targets for sections which are automatically generated
        in a rendered Confluence instance.

        Args:
            docname: the docname of the doctree
            doctree: the doctree to search for targets
            title_track (optional): database for tracking unique titles
        """

        singleconfluence = self.name == 'singleconfluence'
        root_doc = self.config.root_doc if singleconfluence else docname
        secnumbers = self.env.toc_secnumbers.get(root_doc, {})

        # Determine the editor by checking if the metadata for a document
        # specifies a specific editor override or fallback to the global
        # configuration if one is set. In singleconfluence, we always use
        # the global configuration.
        metadata = self.metadata.get(docname, {})
        editor = metadata.get('editor')
        if not editor or singleconfluence:
            editor = self.config.confluence_editor

        # Prepare a database to track titles if one is not already provided.
        # (i.e. not all callers care about unique targets between multiple
        # documents)
        title_track = title_track if title_track is not None else {}

        # Find the first section of this document page. It will be used to
        # create "base" line to a specific page embedded in the single
        # document generated. This only applies to single-document generation.
        root_section = None
        if singleconfluence:
            title_node = self._find_title_element(doctree)
            if title_node and isinstance(title_node.parent, nodes.section):
                root_section = title_node.parent

        # Process all section-owned titles for "title"/heading elements to
        # register.
        for node in findall(doctree, nodes.title):
            section_node = node.parent
            if not isinstance(section_node, nodes.section):
                continue

            # Extract the "title" for this section to be used when referencing
            # this heading. In Confluence, the anchor name matches that of the
            # title (side from things such as spaces removed). Although, for
            # repeated titles, there will be a ".<n>" postfix for any title
            # entry that has the same name starting with ".1". For example,
            # if a title "test" exists twice, the first header entry will have
            # an anchor of "test" and the second will have an entry of
            # "test.1".
            sep = '-' if editor == 'v2' else ''
            title_name = sep.join(node.astext().split())

            # Check to see if this title will have a section number added to
            # it (e.g. "test" becoming named "1. test"). It is assumed here
            # that any ID of a section node when passed into the environment's
            # section number tracking will result in the same section number
            # being returned.
            if self.add_secnumbers and 'ids' in section_node:
                first_id = first(section_node['ids'])

                anchorname = f'{docname}/#{first_id}'
                if anchorname not in secnumbers:
                    anchorname = f'{first_id}/'

                secnumber = secnumbers.get(anchorname)
                if secnumber:
                    title_name = ('.'.join(map(str, secnumber)) +
                        self.secnumber_suffix + title_name)

            # Determine the "final" target name of this title. Check if this
            # title has been used before. If so, append a new postfix to it.
            title_target = title_name
            last_title_postfix = title_track.get(title_target, 0)
            title_track[title_target] = last_title_postfix + 1
            if last_title_postfix > 0:
                title_target = f'{title_target}.{last_title_postfix}'

            # If this section is the (first) root section, register a target
            # for a "root" anchor point. This is important for references that
            # link to documents (e.g. `:doc:<>`). For example, if "page-a"
            # has a document link to "page-b" (e.g. `:doc:<page-b>`), we want
            # an anchor to jump to after the document is merged. We use the
            # first detected title in a page as the main target for the
            # document's "top" link.
            if singleconfluence and section_node == root_section:
                root_anchorname = f'/#{docname}'
                self._register_target(editor, root_anchorname, title_target)

            # For each identified assigned to the section, ensure we register
            # a target anchor for each one.
            if 'ids' in section_node:
                for id_ in section_node['ids']:
                    anchorname = f'{docname}/#{id_}'
                    self._register_target(editor, anchorname, title_target)

            # For each global name assigned to the section, ensure we register
            # a target anchor for each one.
            if 'names' in section_node:
                for name in section_node['names']:
                    anchorname = f'/#{name}'
                    self._register_target(editor, anchorname, title_target)

        # Process all targets except for entries associated with a section
        # (as those were processed above).
        for node in findall(doctree, nodes.target):
            node_refid = node.get('refid')
            if not node_refid:
                continue

            next_sibling = first(findall(node,
                include_self=False, descend=False, siblings=True))
            if isinstance(next_sibling, nodes.section):
                continue

            full_id = f'{docname}/#{node_refid}'
            self._register_target(editor, full_id, node_refid)

    def _register_target(self, editor, refid, target):
        # v2 editor does not link anchors with select characters;
        # provide a workaround that url encodes targets
        #
        # See: https://jira.atlassian.com/browse/CONFCLOUD-74698
        if not self.config.confluence_adv_disable_confcloud_74698:
            if editor == 'v2':
                new_target = quote(target)

                # So... related to CONFCLOUD-74698, something about anchors
                # with special characters will cause some pain for links.
                # This has been observed in the past, was removed after
                # thinking it was not an issue but is now being added again.
                # It appears that when a header is generated an identifier in
                # Confluence Cloud that has special characters, we can observe
                # Confluence prefixing these identifiers with two copies of
                # `[inlineExtension]`. Cannot explain why, so if this situation
                # occurs, just add the prefix data to help ensure links work.
                if not self.config.confluence_adv_disable_confcloud_ieaj:
                    if new_target != target:
                        new_target = 2 * '[inlineExtension]' + new_target

                target = new_target

        self.state.register_target(refid, target)

        # For singleconfluence, register global fallbacks for targets
        # to ensure merged targets from other documents can be linked to
        # from other doctrees.
        if self.name == 'singleconfluence':
            _, refid_part = refid.split('/', 1)
            fallback_refid = f'/{refid_part}'
            if fallback_refid != refid:
                self.state.register_target(fallback_refid, target)

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
                doctitle = f'autogen-{docname}'
                if self.publish:
                    self.warn('document will be published using an '
                        f'generated title value: {docname}')
            elif self.publish:
                self.warn('document will not be published since it '
                    f'has no title: {docname}')

        return doctitle
