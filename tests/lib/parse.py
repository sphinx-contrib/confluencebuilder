# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from bs4 import BeautifulSoup
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def parse(filename, dirname=None):
    """
    parse the output of a generated sphinx document

    Parses the provided filename for generated Confluence-supported markup which
    can be examined for expected content. This function will return an instance
    of BeautifulSoup which a tester can take advantage of the utility calls the
    library provides.

    Args:
        filename: the filename to parse
        dirname (optional): the directory the provided filename exists in

    Returns:
        the parsed output
    """
    if dirname:
        target = Path(dirname) / filename
    else:
        target = Path(filename)

    target = target.parent / (target.name + '.conf')

    with target.open(encoding='utf-8') as fp:
        soup = BeautifulSoup(fp, 'html.parser')
        yield soup
