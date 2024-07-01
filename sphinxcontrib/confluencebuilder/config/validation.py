# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from pathlib import Path
from sphinxcontrib.confluencebuilder.config.exceptions import ConfluenceConfigError
from sphinxcontrib.confluencebuilder.util import extract_strings_from_file
from sphinxcontrib.confluencebuilder.util import str2bool
import os


class ConfigurationValidation:
    def __init__(self, builder):
        """
        configuration validation helper

        A helper class used to help validate the configuration state of a
        builder instance. A validator provides a way to performed a chain of
        queries for a configuration entry. In the event that a configuration
        condition fails, an `ConfluenceConfigError` is thrown to indicate
        an issue. For example, if there is a desire to check if a configuration
        value `my_config` points to a valid file, the following can be used:

            validator = ConfigurationValidation(builder)
            validator.conf('my_config').file()

        When testing configuration entries, a `conf` value needs to be set
        first, followed by one or more configuration checks provided in this
        validator implementation.

        Args:
            builder: the sphinx builder instance
        """
        self.config = builder.config
        self.env = builder.app.env
        self.key = None
        self._translate = None

    def bool(self):
        """
        checks if a configuration is a boolean

        After an instance has been set a configuration key (via `conf`), this
        method can be used to check if the value (if any) configured with this
        key is a boolean. If not, an `ConfluenceConfigError` exception
        will be thrown.

        In the event that the configuration is not set (e.g. a value of `None`),
        this method will have no effect.

        Returns:
            the validator instance
        """
        value = self._value()

        if value is not None:
            if isinstance(value, (int, str)):
                try:
                    str2bool(value)
                except ValueError as ex:
                    msg = f'{self.key} is not a boolean string'
                    raise ConfluenceConfigError(msg) from ex
            elif not isinstance(value, bool):
                msg = f'{self.key} is not a boolean type'
                raise ConfluenceConfigError(msg)

        return self

    def callable_(self):
        """
        checks if a configuration is a callable

        After an instance has been set a configuration key (via `conf`), this
        method can be used to check if the value (if any) configured with this
        key is a callable type. If not, an `ConfluenceConfigError`
        exception will be thrown.

        In the event that the configuration is not set (e.g. a value of `None`),
        this method will have no effect.

        Returns:
            the validator instance
        """
        value = self._value()

        if value is not None and not callable(value):
            msg = f'{self.key} is not a callable'
            raise ConfluenceConfigError(msg)

        return self

    def conf(self, key, translate=None):
        """
        register the configuration key to validate

        When invoked, this will configure the validator to use the provided key
        as the configuration to perform future validation checks on. A caller
        will invoke this method at least once before attempting to invoke other
        validation calls.

        Args:
            key: the key to check in the configuration
            translate (optional): perform any special translation of a
                                   configuration's value (if any) before
                                   attempting to perform a configuration check

        Returns:
            the validator instance
        """
        self.key = key
        self._translate = translate
        return self

    def dict_str_str(self):
        """
        checks if a configuration is a dictionary (str, str)

        After an instance has been set a configuration key (via `conf`), this
        method can be used to check if the value (if any) configured with this
        key is a dictionary type with string keys and values. If not, an
        `ConfluenceConfigError` exception will be thrown.

        In the event that the configuration is not set (e.g. a value of `None`)
        or is an empty dictionary, this method will have no effect.

        Returns:
            the validator instance
        """
        value = self._value()

        if value is not None:
            if not isinstance(value, dict) or not all(isinstance(k, str)
                    and isinstance(v, str) for k, v in value.items()):
                msg = f'{self.key} is not a dictionary of strings'
                raise ConfluenceConfigError(msg)

        return self

    def docnames(self):
        """
        checks if a configuration is a collection of valid docnames

        After an instance has been set a configuration key (via `conf`), this
        method can be used to check if the value (if any) configured with this
        key is a collection of valid docnames. If not, an
        `ConfluenceConfigError` exception will be thrown.

        In the event that the configuration is not set (e.g. a value of `None`)
        or is an empty collection, this method will have no effect.

        Returns:
            the validator instance
        """
        value = self._value()

        if value is not None:
            if not (isinstance(value, (list, set, tuple))) or not all(
                    isinstance(label, (str, os.PathLike)) for label in value):
                msg = f'{self.key} is not a collection of filenames'
                raise ConfluenceConfigError(msg)

            for docname in value:
                if not any(
                        Path(self.env.srcdir, docname + suffix).is_file()
                        for suffix in self.config.source_suffix):
                    msg = f'{self.key} is missing document {docname}'
                    raise ConfluenceConfigError(msg)

        return self

    def docnames_from_file(self):
        """
        checks if a configuration is a collection of valid docnames from a file

        After an instance has been set a configuration key (via `conf`), this
        method can be used to check if the value (if any) configured with this
        key is a collection of valid docnames found within the contents of a
        valid file. If not, an `ConfluenceConfigError` exception will be
        thrown.

        In the event that the configuration is not set (e.g. a value of `None`),
        this method will have no effect.

        Returns:
            the validator instance
        """
        value = self._value()

        if value is not None:
            self.file()

            docnames = extract_strings_from_file(value)
            for docname in docnames:
                if not any(
                        Path(self.env.srcdir, docname + suffix).is_file()
                        for suffix in self.config.source_suffix):
                    msg = f'{self.key} is missing document {docname}'
                    raise ConfluenceConfigError(msg)

        return self

    def enum(self, etype):
        """
        checks if a configuration is an enumeration type

        After an instance has been set a configuration key (via `conf`), this
        method can be used to check if the value (if any) configured with this
        key is an enumeration of type `etype`. If not, a
        `ConfluenceConfigError` exception will be thrown.

        In the event that the configuration is not set (e.g. a value of `None`),
        this method will have no effect.

        Returns:
            the validator instance
        """

        value = self._value()

        if value is not None and not isinstance(value, etype):
            try:
                value = etype[value.replace('-', '_').lower()]
            except (AttributeError, KeyError) as ex:
                msg = f'{self.key} is not an enumeration ({etype.__name__})'
                raise ConfluenceConfigError(msg) from ex

        return self

    def file(self):
        """
        checks if a configuration is a valid file

        After an instance has been set a configuration key (via `conf`), this
        method can be used to check if the value (if any) configured with this
        key is a valid file. If not, an `ConfluenceConfigError` exception
        will be thrown.

        In the event that the configuration is not set (e.g. a value of `None`),
        this method will have no effect.

        Returns:
            the validator instance
        """
        value = self._value()

        if value is not None:
            if not isinstance(value, (str, os.PathLike)) or \
                    not Path(self.env.srcdir, value).is_file():
                msg = f'{self.key} is not a file'
                raise ConfluenceConfigError(msg)

        return self

    def float_(self, positive=False):
        """
        checks if a configuration is a float

        After an instance has been set a configuration key (via `conf`), this
        method can be used to check if the value (if any) configured with this
        key is a float. If not, an `ConfluenceConfigError` exception
        will be thrown.

        In the event that the configuration is not set (e.g. a value of `None`),
        this method will have no effect.

        Args:
            positive (optional): whether or not the float value must be a
                                  positive value (default: False)

        Returns:
            the validator instance
        """
        value = self._value()

        if value is not None:
            if isinstance(value, str):
                try:
                    value = float(value)
                except ValueError as ex:
                    msg = f'{self.key} is not a float string'
                    raise ConfluenceConfigError(msg) from ex
            elif isinstance(value, int):
                value = float(value)

            if positive:
                if not isinstance(value, float) or value <= 0:
                    msg = f'{self.key} is not a positive float'
                    raise ConfluenceConfigError
            elif not isinstance(value, float) or value < 0:
                msg = f'{self.key} is not a non-negative float'
                raise ConfluenceConfigError(msg)

        return self

    def int_(self, positive=False):
        """
        checks if a configuration is an integer

        After an instance has been set a configuration key (via `conf`), this
        method can be used to check if the value (if any) configured with this
        key is an integer. If not, an `ConfluenceConfigError` exception
        will be thrown.

        In the event that the configuration is not set (e.g. a value of `None`),
        this method will have no effect.

        Args:
            positive (optional): whether or not the integer value must be a
                                  positive value (default: False)

        Returns:
            the validator instance
        """
        value = self._value()

        if value is not None:
            if isinstance(value, str):
                try:
                    value = int(value)
                except ValueError as ex:
                    msg = f'{self.key} is not an integer string'
                    raise ConfluenceConfigError(msg) from ex

            if positive:
                if not isinstance(value, int) or value <= 0:
                    msg = f'{self.key} is not a positive integer'
                    raise ConfluenceConfigError(msg)
            elif not isinstance(value, int) or value < 0:
                msg = f'{self.key} is not a non-negative integer'
                raise ConfluenceConfigError(msg)

        return self

    def matching(self, *expected):
        """
        checks if a configuration matches any of the expected arguments

        After an instance has been set a configuration key (via `conf`), this
        method can be used to check if the value (if any) configured with this
        key matches one of the provided expected arguments. If not, an
        `ConfluenceConfigError` exception will be thrown.

        In the event that the configuration is not set (e.g. a value of `None`),
        this method will have no effect.

        Args:
            *expected: valid entries for a configuration to check against

        Returns:
            the validator instance
        """
        value = self._value()

        if value is not None and value not in expected:
            msg = f'{self.key} does not match expected values'
            raise ConfluenceConfigError(msg)

        return self

    def path(self):
        """
        checks if a configuration is a valid path

        After an instance has been set a configuration key (via `conf`), this
        method can be used to check if the value (if any) configured with this
        key is a valid path. If not, an `ConfluenceConfigError` exception
        will be thrown.

        In the event that the configuration is not set (e.g. a value of `None`),
        this method will have no effect.

        Returns:
            the validator instance
        """
        value = self._value()

        if value is not None:
            if not isinstance(value, (str, os.PathLike)) or \
                    not Path(self.env.srcdir, value).exists():
                msg = f'{self.key} is not a path'
                raise ConfluenceConfigError(msg)

        return self

    def string(self):
        """
        checks if a configuration is a string

        After an instance has been set a configuration key (via `conf`), this
        method can be used to check if the value (if any) configured with this
        key is a string. If not, an `ConfluenceConfigError` exception
        will be thrown.

        In the event that the configuration is not set (e.g. a value of `None`),
        this method will have no effect.

        Returns:
            the validator instance
        """

        value = self._value()

        if value is not None and not isinstance(value, str):
            msg = f'{self.key} is not a string'
            raise ConfluenceConfigError(msg)

        return self

    def strings(self, no_space=False):
        """
        checks if a configuration is a collection of strings

        After an instance has been set a configuration key (via `conf`), this
        method can be used to check if the value (if any) configured with this
        key is a collection of strings. If not, an
        `ConfluenceConfigError` exception will be thrown.

        In the event that the configuration is not set (e.g. a value of `None`)
        or is an empty collection, this method will have no effect.

        Args:
            no_space (optional): whether or not all string values cannot contain
                                  any spaces (default: False)

        Returns:
            the validator instance
        """
        value = self._value()

        if value is not None:
            if not (isinstance(value, (list, set, tuple)) and all(
                    isinstance(entry, str) for entry in value)):
                msg = f'{self.key} is not a collection of strings'
                raise ConfluenceConfigError(msg)

            if no_space:
                for entry in value:
                    if ' ' in entry:
                        msg = f'{self.key} has an entry containing a space'
                        raise ConfluenceConfigError(msg)

        return self

    def _value(self):
        """
        return a value for a configuration

        Return the value (if any) of the provided key found in the registered
        builder's configuration. If any configuration translator is set for a
        key, the translation will be performed and returned with this call.

        Returns:
            the value for a key
        """
        value = getattr(self.config, self.key)

        if value is not None and self._translate:
            value = self._translate(value)

        # If an empty string, treat that this value is actually a `None` value.
        # This permits callers from passing "empty"/unset configuration entries
        # via the command line to "clear" a configuration value.
        if isinstance(value, str) and not value:
            value = None

        return value
