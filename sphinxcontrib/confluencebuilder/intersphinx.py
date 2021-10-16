# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020 Sphinx Confluence Builder Contributors (AUTHORS)
:copyright: Copyright 2007-2020 by the Sphinx team (sphinx-doc/sphinx#AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from __future__ import unicode_literals

import re
import zlib
from os import path

import requests

from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger
from sphinxcontrib.confluencebuilder.state import ConfluenceState

"""
inventory filename to hold intersphinx information
"""
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

    if builder.cloud:
        pages_part = 'pages/{}/'
    else:
        pages_part = 'pages/viewpage.action?pageId={}'

    with open(path.join(builder.outdir, INVENTORY_FILENAME), 'wb') as f:
        # header
        f.write((
            '# Sphinx inventory version 2\n'
            '# Project: %s\n'
            '# Version: %s\n'
            '# The remainder of this file is compressed using zlib.\n' % (
                escape(builder.env.config.project),
                escape(builder.env.config.version))).encode())

        # contents
        compressor = zlib.compressobj(9)

        for domainname, domain in sorted(builder.env.domains.items()):
            if domainname == 'std':
                for name, dispname, typ, docname, raw_anchor, prio in sorted(
                        domain.get_objects()):

                    page_id = ConfluenceState.uploadId(docname)
                    if not page_id:
                        continue

                    target_name = '{}#{}'.format(docname, raw_anchor)
                    target = ConfluenceState.target(target_name)

                    if raw_anchor and target:
                        title = ConfluenceState.title(docname)
                        anchor = 'id-' + title + '-' + target
                        anchor = anchor.replace(' ', '')

                        # confluence will convert quotes to right-quotes for
                        # anchor values; replace and encode the anchor value
                        anchor = anchor.replace('"', '”')
                        anchor = anchor.replace("'", '’')
                        anchor = requests.utils.quote(anchor.encode('utf-8'))
                    else:
                        anchor = ''

                    uri = pages_part.format(page_id)
                    if anchor:
                        uri += '#' + anchor
                    if dispname == name:
                        dispname = '-'
                    entry = ('%s %s:%s %s %s %s\n' %
                             (name, domainname, typ, prio, uri, dispname))
                    ConfluenceLogger.verbose('(intersphinx) ' + entry.strip())
                    f.write(compressor.compress(entry.encode('utf-8')))

        f.write(compressor.flush())
