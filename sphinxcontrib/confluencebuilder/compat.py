# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from docutils import __version_info__ as docutils_version_info


# use docutil's findall call over traverse (obsolete)
def docutils_findall(doctree, *args, **kwargs):
    if docutils_version_info >= (0, 18, 1):
        return doctree.findall(*args, **kwargs)

    return doctree.traverse(*args, **kwargs)
