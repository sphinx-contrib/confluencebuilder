# -*- coding: utf-8 -*-
"""
    sphinxcontrib.confluencebuilder.experimental
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2017 by the contributors (see AUTHORS file).
    :license: BSD, see LICENSE.txt for details.
"""

try:
    from html.parser import HTMLParser
except ImportError:
    from HTMLParser import HTMLParser

CONFLUENCE_DEFAULT_MARGIN_OFFSET = 30
EXPERIMENTAL_QUOTE_KEYWORD = 'SCCB_CSFT_QUOTE'

class ConfluenceExperimentalQuoteSupportParser(HTMLParser):
    data = ''
    para_attrs = None

    def __init__(self):
        try:
            HTMLParser.__init__(self, convert_charrefs=True)
        except TypeError:
            HTMLParser.__init__(self)

    def get_data(self):
        return self.data

    def handle_starttag(self, tag, attrs):
        self._process_para()
        if tag == 'p':
            self.para_attrs = attrs
        else:
            raw = '<%s' % tag
            for att, val in attrs:
                raw += " %s='%s'" % (att, val)
            raw += '>'
            self.data += raw

    def handle_data(self, data):
        if isinstance(self.para_attrs, list):
            level = 0
            while data.startswith(EXPERIMENTAL_QUOTE_KEYWORD):
                data = data[len(EXPERIMENTAL_QUOTE_KEYWORD):]
                level += 1
            self._process_para(level)
        self.data += data

    def handle_endtag(self, tag):
        self._process_para()
        self.data += '</%s>' % tag

    def unknown_decl(self, data):
        if data.upper().startswith('CDATA['):
            self.data += '<!['
            self.data += data
            self.data += ']]>'

    def _process_para(self, level = 0):
        if isinstance(self.para_attrs, list):
            raw = '<p'
            for att, val in self.para_attrs:
                raw += " %s='%s'" % (att, val)
            if level > 0:
                raw += ' style="margin-left: %d.0px"' % (
                    CONFLUENCE_DEFAULT_MARGIN_OFFSET * level)
            raw += '>'
            self.data += raw
            self.para_attrs = None
