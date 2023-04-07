# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

class ConfigManager:
    def __init__(self, app):
        """
        configuration manager

        The goal of a configuration manager is to track Confluence-specific
        configuration options for late stage referencing. Configuration
        options in this extension may be adjusted at a later stage beyond
        the extension's setup stage. The manager can be used to track
        what configuration options exist, even for specific types, which
        can allow configuration tweaks to processing against tracked
        options instead of having to explicitly reference groups of
        configuration options outside the setup implementation.

        Args:
            app: the sphinx application instance

        Attributes:
            app: the sphinx application instance
            options: set of registered extension options
            options_bool: set of registered extension options (bool-specific)
            options_int: set of registered extension options (integer-specific)
        """
        self.app = app
        self.options = set()
        self.options_bool = set()
        self.options_int = set()

    def add_conf(self, name, rebuild=''):
        """
        register a configuration option

        Registers a provided configuration option into the Sphinx application.
        Provides a simplified call over `add_config_value`, which always
        specifics a `None` default type (required for the Confluence
        extension's configuration processing) and defaults to a no rebuild
        condition.

        Args:
            name: the name of the configuration value
            rebuild (optional): the condition of rebuild based on Sphinx's
                                 `add_config_value` option (defaults to `''`
                                 for no rebuild)
        """
        self.options.add(name)
        self.app.add_config_value(name, None, rebuild=rebuild)

    def add_conf_bool(self, name, rebuild=''):
        """
        register a boolean-typed configuration option

        Register a configuration option as outlined in `add_conf`. This call
        is specific for registering options which values will be of a boolean
        type, to help track all boolean-typed options for future processing.

        Args:
            name: the name of the configuration value
            rebuild (optional): the condition of rebuild based on Sphinx's
                                 `add_config_value` option (defaults to `''`
                                 for no rebuild)
        """
        self.options_bool.add(name)
        self.add_conf(name, rebuild=rebuild)

    def add_conf_int(self, name, rebuild=''):
        """
        register a integer-typed configuration option

        Register a configuration option as outlined in `add_conf`. This call
        is specific for registering options which values will be of a integer
        type, to help track all integer-typed options for future processing.

        Args:
            name: the name of the configuration value
            rebuild (optional): the condition of rebuild based on Sphinx's
                                 `add_config_value` option (defaults to `''`
                                 for no rebuild)
        """
        self.options_int.add(name)
        self.add_conf(name, rebuild=rebuild)
