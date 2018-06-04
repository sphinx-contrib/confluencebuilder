# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2017 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from sphinx.util import logging
import io

class ConfluenceLogger():
    """
    confluence logger class

    This class is used to manage an internally logger instance and provide
    methods to easily log message at specific logging levels.
    """
    logger = None

    @staticmethod
    def initialize():
        """
        initialize the confluence logger

        Before using the Confluence logger utility class, it needs to be
        initialized. This method should be invoked once (ideally before any
        attempts made to log).
        """
        ConfluenceLogger.logger = logging.getLogger("confluence")

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
    def verbose(msg, *args, **kwargs):
        """
        log a verbose message

        Log a message at the verbose level. `msg` is a format string with the
        arguments provided by `args`. See also:
         https://docs.python.org/3/library/logging.html#logging.Logger.debug
        """
        if ConfluenceLogger.logger:
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
            with io.open('trace.log', 'a', encoding='utf-8') as file:
                file.write(u'[%s]\n' % container)
                file.write(data)
                file.write(u'\n')
        except (IOError, OSError) as err:
            ConfluenceLogger.warn('unable to trace: %s' % err)
