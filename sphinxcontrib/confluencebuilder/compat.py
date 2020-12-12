# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from sphinx.locale import __
from sphinx.util.console import bold # pylint: disable=no-name-in-module
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger

# load sphinx's progress_message or use a compatible instance
try:
    from sphinx.util import progress_message
except ImportError:
    class progress_message:
        def __init__(self, msg):
            self.msg = msg

        def __enter__(self):
            ConfluenceLogger.info(bold(self.msg + '... '), nonl=True)

        def __exit__(self, type, value, traceback):
            if type:
                ConfluenceLogger.info(__('failed'))
            else:
                ConfluenceLogger.info(__('done'))
