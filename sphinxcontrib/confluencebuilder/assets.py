# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from contextlib import contextmanager
from docutils import nodes
from multiprocessing import Manager
from pathlib import Path
from sphinx import addnodes
from sphinx.util.osutil import canon_path
from sphinx.util.images import guess_mimetype
from sphinxcontrib.confluencebuilder.compat import docutils_findall as findall
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger as logger
from sphinxcontrib.confluencebuilder.std.confluence import INVALID_CHARS
from sphinxcontrib.confluencebuilder.util import ConfluenceUtil
from sphinxcontrib.confluencebuilder.util import find_env_abspath

# default content type to use if a type cannot be detected for an asset
DEFAULT_CONTENT_TYPE = 'application/octet-stream'


class ConfluenceAsset:
    """
    a confluence asset

    Holds metadata for an asset (image or file).

    Args:
        path: the absolute path to the asset
        type_: the content type of the asset
        hash_: the hash of the asset

    Attributes:
        doc2key: mapping of a docname to an attachment key
        hash: the hash of the asset
        path: the absolute path to the asset
        type: the content type of the asset
    """
    def __init__(self, path, type_, hash_):
        self.doc2key = {}
        self.hash = hash_
        self.path = path
        self.type = type_


class ConfluenceAssetManager:
    """
    a confluence assets tracker

    The asset manager is used to track detect assets to be referenced to and
    published (if configured) to a Confluence instance. The manager has the
    ability to track locations of assets, detect duplicate uses of assets (when
    references and/or duplicate physical files) and more. Typically, the builder
    will scan the list of documents to be processed for assets. When the
    translator is running, it will refer to the asset manager to know where an
    asset will be published (so the translator knows how to reference the
    asset). Finally, during the publishing phase, the list of tracked assets can
    be published to the respective publish points.

    Args:
        env: the build environment
        out_dir: configured output directory (where assets may be stored)
    """
    def __init__(self, env, out_dir):
        self.dockeys = {}
        self.env = env
        self.hash2asset = {}
        self.out_dir = out_dir
        self.path2asset = {}
        self._assets = []
        self._delayed_assets = []

    def add(self, path, docname):
        """
        add a custom attachment

        This method can be used to register a custom attachment to be added to
        a provided page. This call is for special cases when registering a
        file to upload outside a document's actual content (e.g. an
        intersphinx database).

        Args:
            path: the path of the file
            docname: the document's name to attach to

        Returns:
            the key and resolved path
        """
        logger.verbose(f'adding manual attachment: {path}')
        abs_path = find_env_abspath(self.env, self.out_dir, path)
        return self._register_entry(abs_path, docname)

    def fetch(self, node, docname=None, allow_new=True):
        """
        return attachment key and path for provided asset

        An asset-based node has a resource to be added to a page as an
        attachment. This fetch call return the "key"/name of the attachment,
        as well as the resolved path of the resource that will be uploaded.

        Args:
            node: the node to interpret
            docname (optional): the document name the fetch is force

        Returns:
            the key and path of the asset
        """

        # resolve asset path; stop if no path is available
        path = self._interpret_asset_path(node)
        if not path:
            return None, None

        # if not provided a docname, determine the docname this node exists on
        if not docname:
            docname = canon_path(self.env.path2doc(node.document['source']))

        if not docname:
            msg = 'failed to find document name (unexpected)'
            raise AssertionError(msg)

        # find the asset for this path; if we do not have one, this node was
        # created after pre-processing
        asset = self.path2asset.get(path, None)

        # stop if we have no asset for this node
        if not asset and not allow_new:
            return None, None

        # if no asset, build one
        if not asset:
            if isinstance(node, nodes.image):
                key, _ = self._process_image_node(node, docname)
            elif isinstance(node, addnodes.download_reference):
                key, _ = self._process_file_node(node, docname)
            else:
                msg = 'unimplemented node type'
                raise AssertionError(msg)

            asset = self.path2asset.get(path, None)

        # acquire the attachment key of this ready asset
        else:
            key = asset.doc2key.get(docname, None)

        # if we have no attachment key for this document, build one now
        if not key:
            key = self._build_attachment_key(asset, docname)

        # since this is a delayed asset entry, we are also going to track
        # this in a mp-list when later finalizing assets (in the case
        # where an invoke is running a parallel build)
        self._delayed_assets.append(
            (docname, key, path, asset.hash, asset.type))

        return key, path

    @contextmanager
    def multiprocessing_asset_tracking(self):
        """
        setup a context to help track delayed assets when using multiprocessing

        Provides a context to have the asset manager's delayed asset list to
        support a multiprocessing environment. The internal list is temporarily
        replaced with a multiprocessing Manager's list to allow processes to
        populated delayed assets. Once document process is completed, the
        cleanup of the context will convert the delayed asset entries into a
        local list.
        """

        manager = Manager()
        try:
            self._delayed_assets = manager.list()
            yield
            self._delayed_assets = list(self._delayed_assets)
        finally:
            manager.shutdown()

    def preprocess_doctree(self, doctree, docname):
        """
        process a document for assets

        This method will search each the provided document's doctree for
        supported assets which could be published. Asset information is tracked
        in this manager and other helper methods can be used to pull asset
        information when needed.

        Args:
            doctree: the document's tree
            docname: the document's name
        """

        logger.verbose(f'pre-processing doctree ({docname}) for assets...')

        image_nodes = findall(doctree, nodes.image)
        for node in image_nodes:
            self._process_image_node(node, docname)

        file_nodes = findall(doctree, addnodes.download_reference)
        for node in file_nodes:
            self._process_file_node(node, docname)

    def finalize_assets(self):
        """
        build a list of all assets tracked by the manager

        Returns a list of tuples for all asset entries tracked by this manager.
        A tuple entry will contain the following:

         - The key (or name) of the asset.
         - The absolute path of the asset on the system.
         - The content-type value of the asset.
         - The hash value of the asset.
         - The name of the document this asset should be published to.

        Returns:
            the list of assets
        """

        data = []

        # if we have any assets, populate a list to be used for publishing
        if self._assets or self._delayed_assets:
            logger.verbose('finalize assets...')

            # compile list of assets (pre-processed and main-thread registered)
            for asset in self._assets:
                for docname, key in asset.doc2key.items():
                    entry = (key, asset.path, asset.type, asset.hash, docname)
                    logger.verbose(f'> {key} ({docname}): {asset.path}')
                    data.append(entry)

                if not asset.doc2key:
                    logger.verbose(f'> missing doc-entries: {asset.path}')

            # for any "delayed" assets, check if they are registered on the
            # main builder's thread; if not, append them to the list
            for asset_entry in self._delayed_assets:
                docname, key, path, hash_, type_ = asset_entry
                key_db = self.dockeys.setdefault(docname, set())
                if key in key_db:
                    continue

                entry = (key, path, type_, hash_, docname)
                logger.verbose(f'~ {key} ({docname}): {path}')
                data.append(entry)
                key_db.add(key)

            logger.verbose(f'finalized assets (total: {len(data)})')
        else:
            logger.verbose('no assets to finalize')

        return data

    def _process_file_node(self, node, docname):
        """
        process an file node

        This method will process an file node for asset tracking. Asset
        information is tracked in this manager and other helper methods can be
        used to pull asset information when needed.

        Args:
            node: the file node
            docname: the document's name

        Returns:
            the key and path of the asset
        """

        target = node['reftarget']
        if target.find('://') == -1:
            logger.verbose(f'process file node ({docname}): {target}')
            path = self._interpret_asset_path(node)
            if path:
                return self._register_entry(path, docname)

        return None, None

    def _process_image_node(self, node, docname):
        """
        process an image node

        This method will process an image node for asset tracking. Asset
        information is tracked in this manager and other helper methods can be
        used to pull asset information when needed.

        Args:
            node: the image node
            docname: the document's name
        """

        uri = str(node['uri'])
        if not uri.startswith('data:') and uri.find('://') == -1:
            logger.verbose(f'process image node ({docname}): {uri}')
            path = self._interpret_asset_path(node)
            if path:
                return self._register_entry(path, docname)

        return None, None

    def _register_entry(self, path, docname):
        """
        handle an asset entry

        When an asset is detected in a document, the information about the asset
        is tracked in this manager. When an asset is detected, there are
        considerations to be made. If an asset path has already been registered
        (e.g. an asset used twice), only a single asset entry will be created.
        If an asset matches the hash of another asset, another entry is *not
        created (i.e. a documentation set has duplicate assets; *with the
        exception of when ``standalone`` is set to ``True``). In all cases where
        an asset is detected, the asset reference is updated to track which
        document the asset belongs to.

        Args:
            path: the absolute path to the asset
            docname: the document name this asset was found in

        Returns:
            the key and path of the asset
        """

        # find an asset for path
        asset = self.path2asset.get(path, None)

        # if no asset, check if the hash of the contents already has an
        # asset reference
        if not asset:
            hash_ = ConfluenceUtil.hash_asset(path)
            asset = self.hash2asset.get(hash_, None)

            if asset:
                logger.verbose(f'attachment alias ({hash_:.8s}): {asset.path}')
            # if still no asset, build a new asset entry for this path
            else:
                type_ = guess_mimetype(path, default=DEFAULT_CONTENT_TYPE)
                asset = ConfluenceAsset(path, type_, hash_)
                self.hash2asset[hash_] = asset
                self._assets.append(asset)
                logger.verbose(f'new attachment ({hash_:.8s}): {path}')

            self.path2asset[path] = asset

        # acquire the attachment key; if none, build one now
        key = asset.doc2key.get(docname, None)
        if not key:
            key = self._build_attachment_key(asset, docname)

        return key, path

    def _build_attachment_key(self, asset, docname):
        # determine the key to use for this asset
        #
        # Confluence does not allow attachments with select characters.
        # Filter out the asset name to a compatible key value.
        key = asset.path.name
        for rep in INVALID_CHARS:
            key = key.replace(rep, '_')

        # ensure the key is unique to the document it will be added to
        key_db = self.dockeys.setdefault(docname, set())
        tmp_path = Path(key)
        idx = 1
        while key in key_db:
            idx += 1
            key = f'{tmp_path.stem}_{idx}{tmp_path.suffix}'
        key_db.add(key)

        # track this key for this attachment on the specific document
        asset.doc2key.setdefault(docname, key)
        logger.verbose(f'setup attachment key ({docname}): {key}')

        return key

    def _interpret_asset_path(self, node):
        """
        find an absolute path for a target asset

        Returns the absolute path to an asset. For unsupported asset types,
        this method will return ``None`` values. This method should not be
        invoked on external assets (i.e. URLs).

        Args:
            node: the node to parse

        Returns:
            the absolute path
        """
        path = None

        if isinstance(node, nodes.image):
            # uri's will be relative to documentation root.
            path = Path(node['uri'])
        elif isinstance(node, addnodes.download_reference):
            # reftarget will be a reference to the asset with respect to the
            # document (refdoc) holding this reference. Use reftarget and refdoc
            # to find a proper path.
            docdir = Path(node['refdoc']).parent
            path = docdir / node['reftarget']
        else:
            msg = 'unimplemented node type'
            raise AssertionError(msg)  # noqa: TRY004

        abs_path = find_env_abspath(self.env, self.out_dir, path)
        if not abs_path:
            logger.verbose(f'failed to find path: {path}')

        return abs_path
