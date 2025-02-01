# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from base64 import b64encode
from datetime import datetime
from datetime import timezone
from docutils import __version__ as docutils_version
from pathlib import Path
from sphinx import __version__ as sphinx_version
from sphinx.config import Config
from sphinxcontrib.confluencebuilder.state import ConfluenceState
from sphinxcontrib.confluencebuilder.util import ConfluenceUtil
from typing import Any
import json
import os


class ConfluenceManifest:
    def __init__(self, config: Config, state: ConfluenceState):
        """
        a confluence manifest

        A manifest is generated after a build. It can be used to inform a
        user or other tooling what pages/attachments have been processed along
        what page titles and detected hierarchy is expected (if any).

        While this can be used for informational purposes, this information
        can also be used by third-party tooling to take generated Confluence
        information and perform publishing in their own manner (e.g. users
        with an air-gapped environment or needing some sort of publish
        separation due to authentication considerations). Note that while
        this extension can generate a manifest, there is no tooling provided
        to use the manifest in a way to publish.

        Args:
            config: the active configuration
            state: this extension's runtime state tracking
        """
        self.config = config
        self.state = state

        self.data = {
            'type': 'SphinxConfluenceBuilder/Manifest',
            'spec': 1,
        }

    def register_metadata(self) -> None:
        """
        register metadata into the tracked manifest

        When invoked, this call will populate various metadata into the
        manifest cache from the resolved configuration (e.g. project version).
        """

        cfg = self.config

        if cfg.project and cfg.project != 'Project name not set':
            self.data['project'] = cfg.project

        if cfg.release:
            self.data['release'] = cfg.release

        if cfg.version:
            self.data['version'] = cfg.version

        if cfg.author and cfg.author != 'Author name not set':
            self.data['author'] = cfg.author

        if cfg.copyright:
            self.data['copyright'] = cfg.copyright

        if cfg.language:
            self.data['language'] = cfg.language

        if self.config.confluence_manifest_data:
            self.data['includesData'] = True

    def add_page(self, docname: str, output: str,
            out_file: Path, out_dir: Path) -> None:
        """
        add a page into the manifest

        For any page that is built, this call is used to track it into the
        manifest cache. This includes using the docname as a page identifier
        and includes information such as the expected title for a page.

        Args:
            docname: the docname
            output: the raw output for a page
            out_file: the relative path to the built page
            out_dir: the base folder for any output data
        """

        title = self.state.title(docname)

        entry: dict[str, Any] = {
            'id': docname,
            'title': title,
        }

        is_root_doc = self.config.root_doc == docname
        if is_root_doc:
            entry['isRoot'] = True

        parent_docname = self.state.parent_docname(docname)
        if parent_docname:
            parent_title = self.state.title(parent_docname)

            entry['parentId'] = parent_docname
            entry['parentTitle'] = parent_title

        entry.update({
            'hash': {
                # Note that this hash will be of the contents with LF
                # line endings. For output generated on Windows, the
                # hash here will not explicit match the hash of the file.
                # This is fine as this hash is mainly to help identify
                # the uniqueness of the content.
                'sha256': ConfluenceUtil.hash(output),
            },
            'path': self._resolve_path(out_file, out_dir),
        })

        if self.config.confluence_manifest_data:
            entry['data'] = b64encode(output.encode('utf-8')).decode()

        pages = self.data.setdefault('pages', [])
        pages.append(entry)  # type: ignore [attr-defined]

    def add_attachment(self, docname: str, key: str, mime: str, hash_: str,
            path: Path, out_dir: Path) -> None:
        """
        add an attachment into the manifest

        For any attachment that is processed, this call is used to track it
        into the manifest cache. This includes using the expected attachment
        name, the page that should hold the attachment and more.

        Args:
            docname: the docname that should hold this attachment
            key: the identifier to use for an attachment on publish
            mime: the media type of the attachment
            hash_: the hash of the attachment
            path: the relative path to the attachment
            out_dir: the base folder for any output data
        """

        title = self.state.title(docname)

        entry = {
            'id': key,
            'pageId': docname,
            'pageTitle': title,
            'mimeType': mime,
            'hash': {
                'sha256': hash_,
            },
            'path': self._resolve_path(path, out_dir),
        }

        if self.config.confluence_manifest_data:
            with path.open('rb') as fp:
                entry['data'] = b64encode(fp.read()).decode()

        attachments = self.data.setdefault('attachments', [])
        attachments.append(entry)  # type: ignore [attr-defined]

    def export(self, out_dir: Path) -> None:
        """
        export the manifest content

        When an export is requested, the contents will be published into
        a `scb-manifest.json` file into the project's output directory.

        Args:
            out_dir: the folder to output the manifest into
        """

        from sphinxcontrib.confluencebuilder import __version__ as scb_version
        self.data.update({
            'confluencebuilderVersion': scb_version,
            'sphinxVersion': sphinx_version,
            'docutilsVersion': docutils_version,
            'generated': datetime.now(timezone.utc).isoformat(),
        })

        manifest_path = out_dir / 'scb-manifest.json'
        with manifest_path.open('w') as fp:
            json.dump(self.data, fp, indent=4)

    def _resolve_path(self, path: Path, base: Path) -> str:
        """
        resolve a page/attachment path based off a base path

        We attempt to provide a path in the manifest if tooling wishes to
        reference/use a given page/attachment file. The path will be relative
        to the output directory.

        Note that it is possible for an attachment to exist outside of the
        output directory.

        Args:
            path: the path of the file
            base: the output directory to be relative to

        Returns:
            the relative path
        """

        return str(Path(os.path.relpath(path, base)).as_posix())
