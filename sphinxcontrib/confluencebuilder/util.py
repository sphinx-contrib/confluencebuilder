# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from contextlib import contextmanager
from sphinxcontrib.confluencebuilder.std.confluence import API_REST_BIND_PATH
from sphinxcontrib.confluencebuilder.std.confluence import FONT_SIZE
from sphinxcontrib.confluencebuilder.std.confluence import FONT_X_HEIGHT
from hashlib import sha256
import getpass
import os
import re
import shutil
import subprocess
import tempfile
import unicodedata


class ConfluenceUtil:
    """
    confluence utility helper class

    This class is used to hold a series of utility methods.
    """

    @staticmethod
    def hash(data):
        """
        generate a hash of the provided string

        Calculate a hash for a string. When publishing Confluence pages, hashes
        can be used to check if pages needs to be uploaded again.

        Args:
            data: the raw string

        Returns:
            the hash
        """
        return sha256(data.encode()).hexdigest()

    @staticmethod
    def hash_asset(asset):
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
    def normalize_base_url(url):
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


def convert_length(value, unit, pct=True):
    """
    convert a length value to a confluence-supported integer-equivalent value

    This call accepts a length value and associated units and will return a
    pixel or percentage length representation of the provided length value. If
    no units are provided in this call, it will be assumed that the units are
    already represented by a pixel unit.

    Args:
        value: the value to convert
        unit: the units of the value
        pct: permit a percentage value

    Returns:
        the length in pixels
    """

    if value is None:
        return None

    fvalue = float(value)

    if unit is None:
        return int(round(fvalue))

    if unit == 'px':
        pass
    elif unit == 'em':
        fvalue *= FONT_SIZE
    elif unit == 'ex':
        fvalue *= FONT_X_HEIGHT
    elif unit == 'mm':
        fvalue *= 3.7795
    elif unit == 'cm':
        fvalue *= 37.7952
    elif unit == 'in':
        fvalue *= 96
    elif unit == 'pt':
        fvalue *= 1.3333
    elif unit == 'pc':
        fvalue *= 16
    elif pct and unit == '%':
        pass
    else:
        return None

    return int(round(fvalue))


def extract_length(value):
    """
    extract length data from a provided value

    Returns a tuple of a detected length value and a length unit. If no unit
    type can be extracted, it will be assumed that the provided value has no
    unit.

    Args:
        value: the value to parse

    Returns:
        the length and unit type
    """

    if not value:
        return None, None

    matched = re.match(r'^\s*(\d*\.?\d*)\s*(\S*)?\s*$', value)
    if not matched:
        return None, None

    amount, unit = matched.groups()

    if not amount:
        amount = None
        unit = None
    elif not unit:
        unit = None

    return amount, unit


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


def find_env_abspath(env, outdir, path):
    """
    find an existing absolute path for a provided path in a sphinx environment

    This call will accept a path string and attempt to return an absolute path
    to the file (if it exists). If no path can be found, this call will return
    `None`.

    Args:
        env: the build environment
        outdir: the build's output directory
        path: the path to use

    Returns:
        the absolute path
    """

    abspath = None
    if path:
        path = os.path.normpath(path)
        if os.path.isabs(path):
            abspath = path

            # some generated nodes will prefix the path of an asset with `/`,
            # with the intent of that path being the root from the
            # configured source directory instead of an absolute path on the
            # system -- check the environment's source directory first before
            # checking the full system's path
            if path[0] == os.sep:
                new_path = os.path.join(env.srcdir, path[1:])

                if os.path.isfile(new_path):
                    abspath = new_path
        else:
            abspath = os.path.join(env.srcdir, path)

            # extensions may dump a generated asset in the output directory; if
            # the absolute mapping to the source directory does not find the
            # asset, attempt to bind the path based on the output directory
            if not os.path.isfile(abspath):
                abspath = os.path.join(outdir, path)

    # if no asset can be found, ensure a `None` path is returned
    if not os.path.isfile(abspath):
        abspath = None

    return abspath


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
            value = input(prompt)
        finally:
            subprocess.check_call(['stty', 'echo'])
        print('')
        return value
    else:
        return getpass.getpass(prompt=prompt)


def handle_cli_file_subset(builder, option, value):
    """
    process a file subset entry based on a cli-provided value

    If the value of an option is provided in the "overrides", this is (most
    likely) an option set from the command line. If this string points to an
    existing file, we will return the provided file name as is. However, if
    this is a string, it is most likely a list of files from the command line.

    Args:
        builder: the confluence builder
        option: the key associated to this configuration value
        value: the configuration value

    Returns:
        the resolved configuration value
    """

    if option in builder.config['overrides'] and isinstance(value, str):
        if not value:
            # an empty command line subset is an "unset" request
            # (and not an empty list); if no values are detected,
            # return `None`
            return None
        else:
            if os.path.isabs(value):
                target_file = value
            else:
                target_file = os.path.join(builder.env.srcdir, value)

            if os.path.isfile(target_file):
                value = target_file
            else:
                value = value.split(',')

    return value


def remove_nonspace_control_chars(text):
    """
    remove any non-space control characters from text

    This utility calls removes any non-space control characters that cannot be
    published to a Confluence instance.

    Args:
        text: the text to sanitize

    Returns:
        the sanitized text
    """

    return ''.join(c for c in text if c.isspace()
        or unicodedata.category(c) != 'Cc')


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


@contextmanager
def temp_dir():
    """
    generate a temporary directory

    Creates a temporary directory into the system's default temporary folder.
    This is a context-supported call and will automatically remove the directory
    when completed.
    """
    dir_ = tempfile.mkdtemp()
    try:
        yield dir_
    finally:
        shutil.rmtree(dir_, ignore_errors=True)
