# -*- coding: utf-8 -*-

try:
    unicode
except NameError:
    unicode = str


def encode_storage_format(data):
    """
    encodes text to be inserted directly into a storage format area

    A helper used to return content that has been properly encoded and can
    be directly placed inside a Confluence storage-format-prepared document.

    Args:
        data: the text

    Returns:
        the encoded text
    """

    STORAGE_FORMAT_REPLACEMENTS = {
        ('<', '&lt;'),
        ('>', '&gt;'),
        ('"', '&quot;'),
        ("'", '&apos;'),
    }

    # first pass needs to handle ampersand
    data = unicode(data).replace('&', '&amp;')

    for find, encoded in STORAGE_FORMAT_REPLACEMENTS:
        data = data.replace(find, encoded)

    return data
