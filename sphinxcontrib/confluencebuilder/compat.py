# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020-2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from sphinx.locale import __
from sphinx.util.console import bold # pylint: disable=no-name-in-module
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger as logger

# input support with all supported python interpreters
try:
    input = raw_input
except NameError:
    input = input  # pylint: disable=W0127

# load sphinx's progress_message or use a compatible instance
try:
    from sphinx.util import progress_message  # pylint: disable=W0611
except ImportError:
    class progress_message:
        def __init__(self, msg):
            self.msg = msg

        def __enter__(self):
            logger.info(bold(self.msg + '... '), nonl=True)

        def __exit__(self, type, value, traceback):
            if type:
                logger.info(__('failed'))
            else:
                logger.info(__('done'))
