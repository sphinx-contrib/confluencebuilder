# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2018-2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from sphinxcontrib.confluencebuilder import compat
from sphinxcontrib.confluencebuilder.std.confluence import API_REST_BIND_PATH
from hashlib import sha256
import getpass
import os
import subprocess

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

def extract_strings_from_file(filename):
    """
    extracts strings from a provided filename

    Returns the a list of extracted strings found in a provided filename.
    Entries are stripped when processing and lines leading with a comment are
    ignored.

    Args:
        filename: the filename

    Returns:
        the list of strings
    """
    filelist = []

    if os.path.isfile(filename):
        with open(filename) as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith('#'):
                    continue
                filelist.append(line)

    return filelist

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

def getpass2(prompt='Password: '):
    """
    prompt the user for a password without echoing

    Provides a call which can help acquire a password from the user's session
    without attempting to echo the password on the standard output stream. This
    is a support call to help override select environments which may not be able
    to handle the `getpass` call as expected; specifically, this call checks for
    an msystem-based environment on Windows that is not wrapped in a winpty
    call. If `getpass` is called in this environment, the input cannot be
    captured -- which is replaced in this method to configure the terminal not
    to echo, perform a standard input capture and restore the terminal state
    back.

    Args:
        prompt: the value to prompt to the user

    Returns:
        the password value
    """

    # check for a msystem environment which may not be able to use getpass
    #  nt: windows specific; can help exclude some cygwin/msys environments
    #  MSYSTEM: help exclude non-msys/mingw environments
    #  TERM: exclude winpty invokes
    #
    # For environments where this override may be causing issues, a user can
    # configure the `CONFLUENCEBUILDER_NO_GETPASS_HOOK` environment variable to
    # disable this feature.
    if (os.name == 'nt' and 'MSYSTEM' in os.environ and 'TERM' in os.environ and
            'CONFLUENCEBUILDER_NO_GETPASS_HOOK' not in os.environ):
        subprocess.check_call(['stty', '-echo'])
        try:
            value = compat.input(prompt)
        finally:
            subprocess.check_call(['stty', 'echo'])
        print('')
        return value
    else:
        return getpass.getpass(prompt=prompt)

def str2bool(value):
    """
    returns the boolean value for a string

    Returns the boolean value for a provided string. Acceptable values for a
    ``True`` case includes ``y``, ``yes``, ``t``, ``true``, ``on`` and ``1``;
    for a ``False`` case includes ``n``, ``no``, ``f``, ``false``, ``off`` and
    ``0``. Raises ``ValueError`` on error.

    Args:
        value: the raw value

    Returns:
        the boolean interpretation

    Raises:
        ``ValueError`` is raised if the string value is not an accepted string
    """

    value = value.lower()
    if value in ['y', 'yes', 't', 'true', 'on', '1']:
        return True
    elif value in ['n', 'no', 'f', 'false', 'off', '0']:
        return False
    else:
        raise ValueError
