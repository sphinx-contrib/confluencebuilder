# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)
# Copyright 2007-2020 by the Sphinx team (sphinx-doc/sphinx#AUTHORS)

from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger as logger
import re
import requests
import zlib

# inventory filename to hold intersphinx information
INVENTORY_FILENAME = 'objects.inv'


def build_intersphinx(builder):
    """
    build intersphinx information from the state of the builder

    Attempt to build a series of entries for an intersphinx inventory resource
    for Confluence builder generated content. This is only supported after
    processing a publishing event where page identifiers are cached to build URI
    entries.

    Args:
        builder: the builder
    """
    def escape(string):
        return re.sub("\\s+", ' ', string)

    pages_part_fmt = 'pages/'
    pages_part_fmt += '{}/' if builder.cloud else 'viewpage.action?pageId={}'

    inventory_db = builder.out_dir / INVENTORY_FILENAME
    with inventory_db.open('wb') as f:
        # header
        f.write(
            (
                '# Sphinx inventory version 2\n'
                f'# Project: {escape(builder.env.config.project)}\n'
                f'# Version: {escape(builder.env.config.version)}\n'
                '# The remainder of this file is compressed using zlib.\n'
            ).encode(),
        )

        # contents
        compressor = zlib.compressobj(9)

        for domainname, domain in sorted(builder.env.domains.items()):
            for name, dispname, typ, docname, raw_anchor, prio in sorted(
                    domain.get_objects()):

                page_id = builder.state.upload_id(docname)
                if not page_id:
                    continue

                target_name = f'{docname}#{raw_anchor}'
                target = builder.state.target(target_name)

                if raw_anchor and target:
                    title = builder.state.title(docname)
                    anchor = 'id-' + title + '-' + target
                    anchor = anchor.replace(' ', '')

                    # confluence will convert quotes to right-quotes for
                    # anchor values; replace and encode the anchor value
                    anchor = anchor.replace('"', '”')
                    anchor = anchor.replace("'", '’')  # noqa: RUF001
                    anchor = requests.utils.quote(anchor.encode('utf-8'))
                else:
                    anchor = ''

                uri = pages_part_fmt.format(page_id)
                if anchor:
                    uri += '#' + anchor
                display = '-' if dispname == name else dispname
                entry = f'{name} {domainname}:{typ} {prio} {uri} {display}\n'
                logger.verbose('(intersphinx) ' + entry.strip())
                f.write(compressor.compress(entry.encode('utf-8')))

        f.write(compressor.flush())
