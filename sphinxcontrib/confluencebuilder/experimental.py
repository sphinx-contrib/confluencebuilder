# -*- coding: utf-8 -*-
"""
    sphinxcontrib.confluencebuilder.experimental
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2017 by the contributors (see AUTHORS file).
    :license: BSD, see LICENSE.txt for details.
"""

CONFLUENCE_DEFAULT_MARGIN_OFFSET = 30
EXPERIMENTAL_QUOTE_KEYWORD_START = 'SCCB_CSFT_QUOTE_START_'
EXPERIMENTAL_QUOTE_KEYWORD_END = 'SCCB_CSFT_QUOTE_END'

class ConfluenceExperimentalQuoteSupport:
    @staticmethod
    def quoteStart(level):
        return '%s%02d' % (EXPERIMENTAL_QUOTE_KEYWORD_START, level)

    @staticmethod
    def quoteEnd():
        return EXPERIMENTAL_QUOTE_KEYWORD_END

    @staticmethod
    def quoteProcess(data):
        data = data.replace(EXPERIMENTAL_QUOTE_KEYWORD_END, '</p>')
        parts = data.split(EXPERIMENTAL_QUOTE_KEYWORD_START)
        for idx, part in enumerate(parts[1:]):
            margin = CONFLUENCE_DEFAULT_MARGIN_OFFSET * int(part[:2])
            part_data = part[2:]
            parts[idx+1] = \
                '<p style="margin-left: %d.0px">%s' % (margin, part_data)

        return ''.join(parts);
