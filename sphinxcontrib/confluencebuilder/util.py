# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from __future__ import annotations
from contextlib import contextmanager
from contextlib import suppress
from pathlib import Path
from sphinxcontrib.confluencebuilder.std.confluence import API_REST_V1
from sphinxcontrib.confluencebuilder.std.confluence import API_REST_V2
from sphinxcontrib.confluencebuilder.std.confluence import FONT_SIZE
from sphinxcontrib.confluencebuilder.std.confluence import FONT_X_HEIGHT
from subprocess import check_call
from hashlib import sha256
from urllib.parse import urlparse
import getpass
import os
import re
import shutil
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
        with asset.open('rb') as file:
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
                url = url.removesuffix('/')
            # check for rest api prefix; strip and return if found
            if url.endswith(API_REST_V1):
                url = url.removesuffix(API_REST_V1)
            if url.endswith(API_REST_V2):
                url = url.removesuffix(API_REST_V2)
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


def detect_cloud(site):
    """
    attempt to detect if the site is a cloud or data center instance

    Returns whether the provided site is most likely either a Confluence
    Cloud or Confluence Data Server instance.

    Args:
        site: the configured site value

    Returns:
        whether it is believed the site is a cloud instance
    """

    is_cloud = False

    try:
        parsed = urlparse(site)
    except ValueError:
        pass
    else:
        if parsed.hostname and parsed.hostname.endswith('atlassian.net'):
            is_cloud = True

    return is_cloud


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

    file = Path(filename) if isinstance(filename, str) else filename
    if file.is_file():
        with file.open() as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith('#'):
                    continue
                filelist.append(line)

    return filelist


def find_env_abspath(env, out_dir, path: str) -> Path | None:
    """
    find an existing absolute path for a provided path in a sphinx environment

    This call will accept a path string and attempt to return an absolute path
    to the file (if it exists). If no path can be found, this call will return
    `None`.

    Args:
        env: the build environment
        out_dir: the build's output directory
        path: the path to use

    Returns:
        the absolute path
    """

    if not path:
        return None

    try:
        normalized_path = Path(os.path.normpath(path))
    except OSError:
        # ignore paths that may not resolve; this may include paths with
        # with wildcard hints to be used for candidate fetching at a
        # later stage
        return None

    # some generated nodes will prefix the path of an asset with `/`,
    # with the intent of that path being the root from the
    # configured source directory instead of an absolute path on the
    # system -- check the environment's source directory first before
    # checking the full system's path
    if normalized_path.parts[0] == os.sep:
        abs_path = Path(env.srcdir, *normalized_path.parts[1:])

        if abs_path.is_file():
            return abs_path

    if normalized_path.is_absolute():
        abs_path = normalized_path
    else:
        abs_path = Path(env.srcdir, normalized_path)

        # extensions may dump a generated asset in the output directory; if
        # the absolute mapping to the source directory does not find the
        # asset, attempt to bind the path based on the output directory
        if not abs_path.is_file():
            abs_path = out_dir / normalized_path

    if abs_path.is_file():
        return abs_path

    # if no asset can be found, ensure a `None` path is returned
    return None


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
        try:
            check_call(['/usr/bin/stty', '-echo'])  # noqa: S603
        except:  # noqa: E722
            print()
            print()
            print('(error) pass input not available; please run with winpty')
            print()
            return None
        else:
            try:
                value = input(prompt)
            finally:
                with suppress(Exception):
                    check_call(['/usr/bin/stty', 'echo'])  # noqa: S603

            print()
            return value

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

    if option in builder.config['overrides'] and \
            isinstance(value, (str, os.PathLike)):
        if not value:
            # an empty command line subset is an "unset" request
            # (and not an empty list); if no values are detected,
            # return `None`
            return None

        target_file = Path(value)
        if not target_file.is_absolute():
            target_file = Path(builder.env.srcdir, value)

        value = target_file if target_file.is_file() else value.split(',')

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


def str2bool(value) -> bool:
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

    value = str(value).lower()

    if value in ['y', 'yes', 't', 'true', 'on', '1']:
        return True

    if value in ['n', 'no', 'f', 'false', 'off', '0']:
        return False

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
        yield Path(dir_)
    finally:
        shutil.rmtree(dir_, ignore_errors=True)
