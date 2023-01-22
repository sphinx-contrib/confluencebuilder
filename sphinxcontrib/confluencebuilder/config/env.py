# SPDX-License-Identifier: BSD-2-Clause
# Copyright 2022-2023 Sphinx Confluence Builder Contributors (AUTHORS)

from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger as logger
from sphinxcontrib.confluencebuilder.util import str2bool
import os


def apply_env_overrides(builder):
    """
    applies configuration options from the environment into the extension

    The Confluence builder extension will accept configuration options
    provided from the running environment. For each configuration option
    registered by this extension, the environment will be checked to see if
    a matching environment key (capitalized) exists.

    Args:
        builder: the builder which configuration defaults should be applied on
    """

    conf = builder.config
    config_manager = builder.app.config_manager_

    for key in sorted(config_manager.options):
        # skip over options that have been already set
        if getattr(conf, key) is not None:
            continue

        env_key = key.upper()
        env_val = os.getenv(env_key)
        if env_val:
            logger.verbose('accepting configuration from env: %s' % env_val)

            if key in config_manager.options_bool:
                conf[key] = str2bool(env_val)
            elif key in config_manager.options_int:
                conf[key] = int(env_val)
            else:
                conf[key] = env_val
