# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2018-2020 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from .std.confluence import API_REST_BIND_PATH
from hashlib import sha256

class ConfluenceUtil:
    """
    confluence utility helper class

    This class is used to hold a series of utility methods.
    """

    @staticmethod
    def hashAsset(asset):
        """
        generate a hash of the provided asset

        Calculate a hash for an asset file (e.g. an image file). When publishing
        assets as attachments for a Confluence page, hashes can be used to check
        if an attachment needs to be uploaded again.

        Args:
            asset: the asset (file)

        Returns:
            the hash
        """
        BLOCKSIZE = 65536
        sha = sha256()
        with open(asset, 'rb') as file:
            buff = file.read(BLOCKSIZE)
            while len(buff) > 0:
                sha.update(buff)
                buff = file.read(BLOCKSIZE)

        return sha.hexdigest()

    @staticmethod
    def normalizeBaseUrl(url):
        """
        normalize a confluence base url

        A Confluence base URL refers to the URL portion excluding the target
        API bind point. This method attempts to handle a series of user-provided
        URL values and attempt to determine the proper base URL to use.
        """
        if url:
            # removing any trailing forward slash user provided
            if url.endswith('/'):
                url = url[:-1]
            # check for rest bind path; strip and return if found
            if url.endswith(API_REST_BIND_PATH):
                url = url[:-len(API_REST_BIND_PATH)]
            # restore trailing forward flash
            elif not url.endswith('/'):
                url += '/'
        return url

def first(it):
    """
    returns the first element in an iterable

    Returns the first element found in a provided iterable no matter if it is a
    list or generator type. If no element is found, this call will return a
    `None` value.

    Args:
        it: an iterable type

    Returns:
        the first element
    """
    return next(iter(it), None)
