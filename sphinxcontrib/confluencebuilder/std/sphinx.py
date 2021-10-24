# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2018-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from __future__ import absolute_import
from sphinx import version_info as sphinx_version_info

# sphinx's default highlight style\
#  http://www.sphinx-doc.org/en/stable/config.html#confval-highlight_language
DEFAULT_HIGHLIGHT_STYLE = 'default'

# sphinx's default alignment
#  https://github.com/sphinx-doc/sphinx/issues/4550
if sphinx_version_info >= (2, 0):
    DEFAULT_ALIGNMENT = 'center'
else:
    DEFAULT_ALIGNMENT = None # 'left'
