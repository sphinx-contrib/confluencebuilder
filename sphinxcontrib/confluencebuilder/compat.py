# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2017 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

class ConfluenceCompat:
    """
    confluence compatibility helper class

    This class is used to hold a series of compatibility methods, etc. to assist
    in supporting this Sphinx extension with new and deprecated dependencies.
    """

    @staticmethod
    def status_iterator(context, *args, **kwargs):
        """
        compatibility supported status iterator

        This compatibility method returns an iterator from a support Sphinx-
        implemented status iterator method. An attempt will be made to load the
        method from the utility class `sphinx.util.status_iterator` (Sphinx
        1.6+). If unavailable, the method will attempt to fallback on the Sphinx
        application instance's (context) status_iterator.
        """
        try:
            from sphinx.util import status_iterator
            iterator = status_iterator(*args, **kwargs)
        except ImportError:
            iterator = context.status_iterator(*args, **kwargs)

        return iterator
