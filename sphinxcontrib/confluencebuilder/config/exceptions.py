# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from sphinx.errors import ConfigError
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceError


class ConfluenceConfigurationError(ConfluenceError, ConfigError):
    pass
