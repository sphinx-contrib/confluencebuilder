# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger as logger
from sphinxcontrib.confluencebuilder.util import ConfluenceUtil
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

    # check if the configuration has disabled environment options
    if conf.confluence_disable_env_conf:
        return

    for key in sorted(config_manager.options):
        # skip over options that have been already set
        if getattr(conf, key) is not None:
            continue

        env_key = key.upper()
        env_val = os.getenv(env_key)
        if env_val:
            logger.info(f'accepting configuration from env: {env_key}')

            if key in config_manager.options_bool:
                conf[key] = str2bool(env_val)
            elif key in config_manager.options_int:
                conf[key] = int(env_val)
            else:
                conf[key] = env_val


def build_hash(config):
    """
    builds a confluence configuration hash

    This call will build a hash based on Confluence-specific configuration
    entries. This hash can later be used to determine whether or not
    re-processing documents is needed based certain configuration values
    being changed.

    Args:
        config: the configuration
    """

    # extract confluence configuration options
    entries = []
    for c in sorted(config.filter(['confluence'])):
        entries.append(c.name)
        entries.append(c.value)

    # compile a string to hash, sorting dictionary/list/etc. entries along
    # the way
    hash_data = []
    while entries:
        value = entries.pop(0)

        if isinstance(value, dict):
            sorted_value = dict(sorted(value.items()))
            for k, v in sorted_value.items():
                entries.append(k)
                entries.append(v)
        elif isinstance(value, (list, set, tuple)):
            entries.extend(sorted(value))
        else:
            hash_data.append(str(value))

    # generate a configuration hash
    return ConfluenceUtil.hash(''.join(hash_data))
