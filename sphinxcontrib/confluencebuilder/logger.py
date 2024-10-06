# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from collections import deque
from contextlib import suppress
from pathlib import Path
from sphinx.util import logging
from sphinx.util.console import bold  # pylint: disable=no-name-in-module
import sys


class ConfluenceLogger:
    """
    confluence logger class

    This class is used to manage an internally logger instance and provide
    methods to easily log message at specific logging levels.
    """
    logger = None

    @staticmethod
    def initialize(preload=False):
        """
        initialize the confluence logger

        Before using the Confluence logger utility class, it needs to be
        initialized. This method should be invoked once (ideally before any
        attempts made to log).

        Args:
            preload (optional): attempt to mock a Sphinx application to pre-use
                                 logging features before attempting to load a
                                 Sphinx application
        """
        ConfluenceLogger.logger = logging.getLogger('confluence')

        # setup logging for features like coloring before starting Sphinx
        if preload:
            class MockSphinx:
                def __init__(self):
                    self.messagelog = deque(maxlen=10)
                    self.verbosity = 0
                    self.warningiserror = False
                    self._exception_on_warning = False
                    self._warncount = 0

            # fail silently if mocked application is missing something
            with suppress(Exception):
                logging.setup(MockSphinx(), sys.stdout, sys.stderr)

    @staticmethod
    def error(msg, *args, **kwargs):
        """
        log an error message

        Log a message at the error level. `msg` is a format string with the
        arguments provided by `args`. See also:
         https://docs.python.org/3/library/logging.html#logging.Logger.error
        """
        if ConfluenceLogger.logger:
            ConfluenceLogger.logger.error(msg, *args, **kwargs)

    @staticmethod
    def info(msg, *args, **kwargs):
        """
        log an informative message

        Log a message at the information level. `msg` is a format string with
        the arguments provided by `args`. See also:
         https://docs.python.org/3/library/logging.html#logging.Logger.info
        """
        if ConfluenceLogger.logger:
            ConfluenceLogger.logger.info(msg, *args, **kwargs)

    @staticmethod
    def note(msg, *args, **kwargs):
        """
        log an notable message

        Log a message at the information level with bolded text. `msg` is a
        format string with the arguments provided by `args`. See also:
         https://docs.python.org/3/library/logging.html#logging.Logger.info
        """
        if ConfluenceLogger.logger:
            ConfluenceLogger.logger.info(bold(msg), *args, **kwargs)

    @staticmethod
    def verbose(msg, *args, **kwargs):
        """
        log a verbose message

        Log a message at the verbose level. `msg` is a format string with the
        arguments provided by `args`. See also:
         https://docs.python.org/3/library/logging.html#logging.Logger.debug
        """
        if ConfluenceLogger.logger:
            msg = '[confluence] ' + msg
            ConfluenceLogger.logger.verbose(msg, *args, **kwargs)

    @staticmethod
    def warn(msg, *args, **kwargs):
        """
        log a warning message

        Log a message at the warning level. `msg` is a format string with the
        arguments provided by `args`. See also:
         https://docs.python.org/3/library/logging.html#logging.Logger.warning
        """
        if ConfluenceLogger.logger:
            kwargs['type'] = 'confluence'
            ConfluenceLogger.logger.warning(msg, *args, **kwargs)

    @staticmethod
    def trace(container, data):
        """
        trace data for a given container name

        Traces data with a given container name by dumping the contents directly
        to a log file `trace.log`. The log file, if exists, will be appended.
        This is solely for manually debugging unexpected scenarios.
        """
        try:
            trace_file = Path('trace.log')
            with trace_file.open('a', encoding='utf-8') as file:
                file.write(f'[{container}]\n')
                file.write(data)
                file.write('\n')
        except OSError as err:
            ConfluenceLogger.warn(f'unable to trace: {err}')
