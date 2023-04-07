# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from sphinxcontrib.confluencebuilder.state import ConfluenceState


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
    data = str(data).replace('&', '&amp;')

    for find, encoded in STORAGE_FORMAT_REPLACEMENTS:
        data = data.replace(find, encoded)

    return data


def intern_uri_anchor_value(docname, refuri):
    """
    determine the anchor value for an internal uri point

    This call helps determine the anchor value to use for a link to an anchor
    for an internal document. The anchor value will be parsed out of the
    provided URI checked to see if a target entry already exists (e.g. if a
    header with a preconfigured identifier can be used). If so, the target value
    will be provided. If not, the parsed/raw anchor value will be returned.

    Args:
        docname: the docname of the page to link to
        refuri: the uri

    Returns:
        the encoded text
    """

    anchor_value = None
    if '#' in refuri:
        anchor = refuri.split('#')[1]
        target_name = f'{docname}#{anchor}'

        # check if this target is reachable without an anchor; if so, use
        # the identifier value instead
        target = ConfluenceState.target(target_name)
        if target:
            anchor_value = target
        else:
            anchor_value = anchor

        anchor_value = encode_storage_format(anchor_value)

    return anchor_value
