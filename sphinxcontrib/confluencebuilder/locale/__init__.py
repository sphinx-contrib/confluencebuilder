# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from sphinx.locale import get_translation

# name of this extension's gettext catalog
MESSAGE_CATALOG_NAME = 'sphinxcontrib.confluencebuilder'

# translator for messages in documentation
L = get_translation(MESSAGE_CATALOG_NAME)

# translator for console messages
C = get_translation(MESSAGE_CATALOG_NAME, 'console')
