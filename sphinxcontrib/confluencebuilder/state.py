# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from __future__ import annotations
import hashlib
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluenceConfigError
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger as logger
from sphinxcontrib.confluencebuilder.std.confluence import CONFLUENCE_MAX_TITLE_LEN


class ConfluenceState:
    """
    confluence state tracking

    This class is used to track the state of a Confluence building/publishing
    operation. This includes, but not limited to, remember title names for
    documents, tracking reference identifiers to other document names and more.
    """
    doc2uploadId: dict[str, int] = {}
    doc2parentDoc: dict[str, str] = {}
    doc2title: dict[str, str] = {}
    doc2ttd: dict[str, int] = {}
    refid2target: dict[str, str] = {}
    title2doc: dict[str, str] = {}

    @staticmethod
    def register_parent_docname(docname: str, parent_docname: str):
        """
        register a parent docname for a provided docname

        When using Sphinx's toctree, documents defined in the tree can be
        considered child pages (see the configuration option
        'confluence_page_hierarchy'). This method helps track a parent document
        for a provided child document. With the ability to track a parent
        document and track publish upload identifiers (see `registerUploadId`),
        the publish operation can help ensure pages are structured in a
        hierarchical fashion (see also `parentDocname`).

        [1]: http://www.sphinx-doc.org/en/stable/markup/toctree.html#directive-toctree
        """
        ConfluenceState.doc2parentDoc[docname] = parent_docname
        logger.verbose(f'setting parent of {docname} to: {parent_docname}')

    @staticmethod
    def register_target(refid: str, target: str, *, overwrite: bool=False):
        """
        register a reference to a specific (anchor) target

        When interpreting a reference in reStructuredText, the reference could
        point to an anchor in the same document, another document or an anchor
        in another document. In Confluence, the target name is typically
        dependent on the document's title name (auto-generated targets provided
        by Confluence; ex. title#header). This register method allows a builder
        to track the target value to use for a provided reference (so that a
        writer can properly prepare a link; see also `target`).
        """
        exists = refid in ConfluenceState.refid2target
        if exists and not overwrite:
            logger.verbose(f'ignore mapping {refid} to target: {target}')
        else:
            ConfluenceState.refid2target[refid] = target
            postfix = ' [OVERWRITE]' if exists else ''
            logger.verbose(f'mapping {refid} to target: {target}{postfix}')

    @staticmethod
    def register_title(docname: str, title: str, config) -> str:
        """
        register the title for the provided document name

        In Confluence, a page is identified by the name/title of a page (at
        least, from the user's perspective). When processing a series of
        document names, the title value used for a document is based off the
        first heading detected. This register method allows a builder to track
        a document's title name name, so it may provide a document's contents
        and target title when passed to the publish operation.

        If a prefix (or postfix) value is provided, it will be added to the
        beginning (or at the end) of the provided title value.
        """
        try_max = CONFLUENCE_MAX_TITLE_LEN
        base_tail = ''
        postfix = None
        prefix = None

        if config and (not config.confluence_ignore_titlefix_on_index or
                docname != config.root_doc):
            prefix = config.confluence_publish_prefix

            postfix = ConfluenceState._format_postfix(
                postfix=config.confluence_publish_postfix, docname=docname,
                config=config,
            )

        if prefix:
            title = prefix + title

        if postfix:
            base_tail += postfix

        if len(title) + len(base_tail) > try_max:
            warning = f'document title has been trimmed due to length: {title}'
            if len(base_tail) > 0:
                warning += f'; With postfix: {base_tail}'
            logger.warn(warning)
            title = title[0:try_max - len(base_tail)]

        base_title = title
        title += base_tail

        # check if title is already used; if so, append a new value
        offset = 2
        while title.lower() in ConfluenceState.title2doc:
            if offset == 2:
                docname2 = ConfluenceState.title2doc[title.lower()]
                logger.warn('title conflict detected with '
                    f"'{docname2}' and '{docname}'")

            tail = f' ({offset}){base_tail}'
            if len(base_title) + len(tail) > try_max:
                base_title = base_title[0:(try_max - len(tail))]

            title = base_title + tail
            offset += 1

        ConfluenceState.doc2title[docname] = title
        ConfluenceState.title2doc[title.lower()] = docname
        logger.verbose(f'mapping {docname} to title: {title}')
        return title

    @staticmethod
    def register_toctree_depth(docname: str, depth: int):
        """
        register the toctree-depth for the provided document name

        Documents using toctree's will only use the first toctree's 'maxdepth'
        option [1]. This method provides the ability to track the depth of a
        document before toctree resolution removes any hints at the maximum
        depth desired.

        [1]: http://www.sphinx-doc.org/en/stable/markup/toctree.html#id3
        """
        ConfluenceState.doc2ttd[docname] = depth
        logger.verbose(f'track {docname} toc-depth: {depth}')

    @staticmethod
    def register_upload_id(docname: str, id_: int):
        """
        register a page (upload) identifier for a docname

        When a publisher creates/updates a page on a Confluence instance, the
        resulting page will have an identifier for it. This state utility class
        can help track the Confluence page's identifier by invoking this
        registration method. This method is primarily used to help track/order
        published documents into a hierarchical fashion (see
        `registerParentDocname`). It is important to note that the order of
        published documents will determine if a page's upload identifier is
        tracked in this state (see also `uploadId`).
        """
        ConfluenceState.doc2uploadId[docname] = id_
        logger.verbose(
            f"tracking docname {docname}'s upload id: {id_}")

    @staticmethod
    def reset():
        """
        reset all state information

        Provides the ability for uses of a Confluence state singleton to reset
        known tracked data.
        """
        ConfluenceState.doc2uploadId.clear()
        ConfluenceState.doc2parentDoc.clear()
        ConfluenceState.doc2title.clear()
        ConfluenceState.doc2ttd.clear()
        ConfluenceState.refid2target.clear()
        ConfluenceState.title2doc.clear()

    @staticmethod
    def parent_docname(docname: str) -> str | None:
        """
        return the parent docname (if any) for a provided docname

        See `registerParentDocname` for more information.
        """
        return ConfluenceState.doc2parentDoc.get(docname)

    @staticmethod
    def target(refid: str) -> str | None:
        """
        return the (anchor) target for a provided reference

        See `registerTarget` for more information.
        """
        return ConfluenceState.refid2target.get(refid)

    @staticmethod
    def title(docname: str, default: str | None = None) -> str | None:
        """
        return the title value for a provided docname

        See `registerTitle` for more information.
        """
        return ConfluenceState.doc2title.get(docname, default)

    @staticmethod
    def toctree_depth(docname: str) -> int | None:
        """
        return the toctree-depth value for a provided docname

        See `registerToctreeDepth` for more information.
        """
        return ConfluenceState.doc2ttd.get(docname)

    @staticmethod
    def upload_id(docname: str) -> int | None:
        """
        return the confluence (upload) page id for the provided docname

        See `registerUploadId` for more information.
        """
        return ConfluenceState.doc2uploadId.get(docname)

    @staticmethod
    def _format_postfix(postfix: str, docname: str, config) -> str:
        """
        Format a postfix that may have placeholders.
        All placeholders used must be supported otherwise an error is raised
        """
        if postfix:
            try:
                return postfix.format(
                    hash=ConfluenceState._create_docname_unique_hash(docname, config),
                )
            except KeyError as ex:
                msg = (
                    f"Configured confluence_publish_prefix '{postfix}' has "
                    'an unknown template replacement.'
                )
                raise ConfluenceConfigError(msg) from ex
        return postfix

    @staticmethod
    def _create_docname_unique_hash(docname: str, config) -> str:
        """
        Create a unique(ish) hash for the given source file to avoid collisions
        when pushing pages to confluence.
        """
        prehash = docname
        prehash += str(config.project)
        prehash += str(config.confluence_parent_page)
        prehash += str(config.confluence_publish_root)
        return hashlib.sha1(prehash.encode()).hexdigest()  # noqa: S324
