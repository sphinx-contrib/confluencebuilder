# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from pathlib import Path
from sphinxcontrib.confluencebuilder.util import ConfluenceUtil
import json


# base filename for cache information
ENV_CACHE_BASENAME = '.cache_confluence_'

# filename for configuration hash
ENV_CACHE_CONFIG = ENV_CACHE_BASENAME + 'config'

# filename for documentation hashes
ENV_CACHE_DOCHASH = ENV_CACHE_BASENAME + 'dochash'

# filename for last publication identifiers
ENV_CACHE_PUBLISH = ENV_CACHE_BASENAME + 'publish'


class ConfluenceCacheInfo:
    def __init__(self, builder):
        self.builder = builder
        self.env = builder.env
        self._active_dochash = {}
        self._active_hash = None
        self._active_pids = {}
        self._cache_cfg_file = builder.out_dir / ENV_CACHE_CONFIG
        self._cache_hash_file = builder.out_dir / ENV_CACHE_DOCHASH
        self._cache_publish_file = builder.out_dir / ENV_CACHE_PUBLISH
        self._cached_dochash = {}
        self._cached_hash = None
        self._cached_pids = {}

    def configure(self, hash_):
        """
        track the active configuration hash

        This call is used to accept the known hash representing the active
        configuration of a Confluence builder run. This hash can later be
        used when checking for outdated documents, as well as saving on a
        run to be used to track outdated documents in future runs (if any).

        Args:
            hash_: the configuration hash
        """

        self._active_hash = hash_

    def is_outdated(self, docname):
        """
        check if a provided document is considered outdated

        This call can return whether a provided document name is believed
        to be outdated and requires a new build.

        Args:
            docname: the name of the document

        Returns:
            whether the page is outdated
        """

        # if the document was not already cached in Sphinx's environment,
        # consider is outdated
        if docname not in self.env.all_docs:
            return True

        # if there is no previous cached hash, all documents are considered
        # outdated
        if not self._cached_hash:
            return True

        # if there is not output file, considered outdated
        dst_filename = self.builder.file_transform(docname)
        dst_file = self.builder.out_dir / dst_filename
        if not dst_file.is_file():
            return True

        # if there is not source file (removed document), considered outdated
        src_file = Path(self.env.doc2path(docname))
        if not src_file.is_file():
            return True

        # check if the hashes do not match; if not, this document is outdated
        doc_hash = self.track_page_hash(docname)
        old_doc_hash = self._cached_dochash.get(docname)
        return doc_hash != old_doc_hash

    def last_page_id(self, docname):
        """
        return the last publish page identifier for a document (if any)

        This call can return the last page identifier a specific document was
        published to, if published at all. This is to help unflag documents
        queued for removal (cleanup), when documents are skipped since they
        are not outdated and not processed for writing.

        Args:
            docname: the name of the document

        Returns:
            the page identifier or ``None``
        """

        pid = self._cached_pids.get(docname)

        # if we checked for a "last page id" for a document, this means that
        # we there is a new or unchanged document being processed -- if an
        # unchanged document, used the cached page id and track it as an
        # assumed active id
        if pid is not None:
            self.track_last_page_id(docname, pid)

        return pid

    def track_page_hash(self, docname):
        """
        track the last publish page hash for a document

        This call can be used to track last page hash a specific document.
        This is to help on re-runs when checking to see if a given page
        is outdated if the hash changes.

        Args:
            docname: the name of the document

        Returns:
            the document's hash
        """

        doc_hash = self._active_dochash.get(docname)
        if doc_hash:
            return doc_hash

        # determine the hash of the document based on data + config-hash
        src_file = Path(self.env.doc2path(docname))
        src_file_hash = ConfluenceUtil.hash_asset(src_file)
        doc_hash_data = self._active_hash + src_file_hash
        doc_hash = ConfluenceUtil.hash(doc_hash_data)

        # remember this document hash when we may later save
        self._active_dochash[docname] = doc_hash

        return doc_hash

    def track_last_page_id(self, docname, page_id):
        """
        track the last publish page identifier for a document

        This call can be used to track last page identifier a specific
        document was published to. This is to help on re-runs where a
        run may wish to be aware of already published documents.

        Args:
            docname: the name of the document
            page_id: the page identifier
        """

        self._active_pids[docname] = page_id
        self._cached_pids.pop(docname, None)

    def load_cache(self):
        """
        load persisted cached information from a previous run (if any)

        After build run with Confluence, information about the build may be
        cached to help track outdated documents. This call can reload any
        cache information stored from a previous run.
        """

        try:
            with self._cache_cfg_file.open(encoding='utf-8') as f:
                self._cached_hash = json.load(f).get('hash')
        except FileNotFoundError:
            pass
        except OSError as e:
            self.builder.warn('failed to load cache (config): ' + e)

        try:
            with self._cache_hash_file.open(encoding='utf-8') as f:
                self._cached_dochash = json.load(f)
        except FileNotFoundError:
            pass
        except OSError as e:
            self.builder.warn('failed to load cache (hashes): ' + e)

        try:
            with self._cache_publish_file.open(encoding='utf-8') as f:
                self._cached_pids = json.load(f)
        except FileNotFoundError:
            pass
        except OSError as e:
            self.builder.warn('failed to load cache (pids): ' + e)

    def save_cache(self):
        """
        save persisted cached information from a run

        Save the updated state of this build information instance into a
        cache file stored in the project's output directory. This information
        can be later used for re-runs tracking outdated documents.
        """

        new_cfg = {
            'hash': self._active_hash,
        }

        new_dochashs = dict(self._cached_dochash)
        new_dochashs.update(self._active_dochash)

        new_pids = dict(self._cached_pids)
        new_pids.update(self._active_pids)

        try:
            with self._cache_cfg_file.open('w', encoding='utf-8') as f:
                json.dump(new_cfg, f)
        except OSError as e:
            self.builder.warn('failed to save cache (config): ' + e)

        try:
            with self._cache_hash_file.open('w', encoding='utf-8') as f:
                json.dump(new_dochashs, f)
        except OSError as e:
            self.builder.warn('failed to save cache (hashes): ' + e)

        try:
            with self._cache_publish_file.open('w', encoding='utf-8') as f:
                json.dump(new_pids, f)
        except OSError as e:
            self.builder.warn('failed to save cache (pids): ' + e)
