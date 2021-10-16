# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

import os

from sphinxcontrib.confluencebuilder.exceptions import ConfluenceConfigurationError
from sphinxcontrib.confluencebuilder.util import extract_strings_from_file, str2bool

try:
    basestring
except NameError:
    basestring = str


class ConfigurationValidation:
    def __init__(self, builder):
        """
        configuration validation helper

        A helper class used to help validate the configuration state of a
        builder instance. A validator provides a way to performed a chain of
        queries for a configuration entry. In the event that a configuration
        condition fails, an `ConfluenceConfigurationError` is thrown to indicate
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
        key is a boolean. If not, an `ConfluenceConfigurationError` exception
        will be thrown.

        In the event that the configuration is not set (e.g. a value of `None`),
        this method will have no effect.

        Returns:
            the validator instance
        """
        value = self._value()

        if value is not None:
            if isinstance(value, basestring):
                try:
                    str2bool(value)
                except ValueError:
                    raise ConfluenceConfigurationError(
                        "%s is not a boolean string" % self.key
                    )
            elif not isinstance(value, bool) and not isinstance(value, int):
                raise ConfluenceConfigurationError(
                    "%s is not a boolean type" % self.key
                )

        return self

    def callable_(self):
        """
        checks if a configuration is a callable

        After an instance has been set a configuration key (via `conf`), this
        method can be used to check if the value (if any) configured with this
        key is a callable type. If not, an `ConfluenceConfigurationError`
        exception will be thrown.

        In the event that the configuration is not set (e.g. a value of `None`),
        this method will have no effect.

        Returns:
            the validator instance
        """
        value = self._value()

        if value is not None and not callable(value):
            raise ConfluenceConfigurationError("%s is not a callable" % self.key)

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
        `ConfluenceConfigurationError` exception will be thrown.

        In the event that the configuration is not set (e.g. a value of `None`)
        or is an empty dictionary, this method will have no effect.

        Returns:
            the validator instance
        """
        value = self._value()

        if value is not None:
            if not isinstance(value, dict) or not all(
                isinstance(k, basestring) and isinstance(v, basestring)
                for k, v in value.items()
            ):
                raise ConfluenceConfigurationError(
                    "%s is not a dictionary of strings" % self.key
                )

        return self

    def docnames(self):
        """
        checks if a configuration is a collection of valid docnames

        After an instance has been set a configuration key (via `conf`), this
        method can be used to check if the value (if any) configured with this
        key is a collection of valid docnames. If not, an
        `ConfluenceConfigurationError` exception will be thrown.

        In the event that the configuration is not set (e.g. a value of `None`)
        or is an empty collection, this method will have no effect.

        Returns:
            the validator instance
        """
        value = self._value()

        if value is not None:
            if not (
                isinstance(value, (list, set, tuple))
                or not all(isinstance(label, basestring) for label in value)
            ):
                raise ConfluenceConfigurationError(
                    "%s is not a collection of filenames" % self.key
                )

            for docname in value:
                if not any(
                    os.path.isfile(os.path.join(self.env.srcdir, docname + suffix))
                    for suffix in self.config.source_suffix
                ):
                    raise ConfluenceConfigurationError(
                        "%s is missing document %s" % (self.key, docname)
                    )

        return self

    def docnames_from_file(self):
        """
        checks if a configuration is a collection of valid docnames from a file

        After an instance has been set a configuration key (via `conf`), this
        method can be used to check if the value (if any) configured with this
        key is a collection of valid docnames found within the contents of a
        valid file. If not, an `ConfluenceConfigurationError` exception will be
        thrown.

        In the event that the configuration is not set (e.g. a value of `None`),
        this method will have no effect.

        Returns:
            the validator instance
        """
        value = self._value()

        if value is not None:
            if not isinstance(value, basestring) or not os.path.isfile(
                os.path.join(self.env.srcdir, value)
            ):
                raise ConfluenceConfigurationError("%s is not a file" % self.key)

            docnames = extract_strings_from_file(value)
            for docname in docnames:
                if not any(
                    os.path.isfile(os.path.join(self.env.srcdir, docname + suffix))
                    for suffix in self.config.source_suffix
                ):
                    raise ConfluenceConfigurationError(
                        "%s is missing document %s" % (self.key, docname)
                    )

        return self

    def file(self):
        """
        checks if a configuration is a valid file

        After an instance has been set a configuration key (via `conf`), this
        method can be used to check if the value (if any) configured with this
        key is a valid file. If not, an `ConfluenceConfigurationError` exception
        will be thrown.

        In the event that the configuration is not set (e.g. a value of `None`),
        this method will have no effect.

        Returns:
            the validator instance
        """
        value = self._value()

        if value is not None:
            if not isinstance(value, basestring) or not os.path.isfile(
                os.path.join(self.env.srcdir, value)
            ):
                raise ConfluenceConfigurationError("%s is not a file" % self.key)

        return self

    def int_(self, positive=False):
        """
        checks if a configuration is an integer

        After an instance has been set a configuration key (via `conf`), this
        method can be used to check if the value (if any) configured with this
        key is an integer. If not, an `ConfluenceConfigurationError` exception
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
            if isinstance(value, basestring):
                try:
                    value = int(value)
                except ValueError:
                    raise ConfluenceConfigurationError(
                        "%s is not an integer string" % self.key
                    )

            if positive:
                if not isinstance(value, int) or value <= 0:
                    raise ConfluenceConfigurationError(
                        "%s is not a positive integer" % self.key
                    )
            elif not isinstance(value, int) or value < 0:
                raise ConfluenceConfigurationError(
                    "%s is not a non-negative integer" % self.key
                )

        return self

    def matching(self, *expected):
        """
        checks if a configuration matches any of the expected arguments

        After an instance has been set a configuration key (via `conf`), this
        method can be used to check if the value (if any) configured with this
        key matches one of the provided expected arguments. If not, an
        `ConfluenceConfigurationError` exception will be thrown.

        In the event that the configuration is not set (e.g. a value of `None`),
        this method will have no effect.

        Args:
            *expected: valid entries for a configuration to check against

        Returns:
            the validator instance
        """
        value = self._value()

        if value is not None and value not in expected:
            raise ConfluenceConfigurationError(
                "%s does not match expected values" % self.key
            )

        return self

    def string(self, permit_empty=False):
        """
        checks if a configuration is a string

        After an instance has been set a configuration key (via `conf`), this
        method can be used to check if the value (if any) configured with this
        key is a string. If not, an `ConfluenceConfigurationError` exception
        will be thrown.

        In the event that the configuration is not set (e.g. a value of `None`),
        this method will have no effect.

        Args:
            permit_empty (optional): whether or not all an empty string of this
                                      value is considered to be a set value

        Returns:
            the validator instance
        """
        value = self._value(permit_empty=True)

        if value is not None and not isinstance(value, basestring):
            raise ConfluenceConfigurationError("%s is not a string" % self.key)

        return self

    def string_or_strings(self):
        """
        checks if a configuration is a string or collection of strings

        After an instance has been set a configuration key (via `conf`), this
        method can be used to check if the value (if any) configured with this
        key is a string or collection of strings. If not, an
        `ConfluenceConfigurationError` exception will be thrown.

        In the event that the configuration is not set (e.g. a value of `None`)
        or is an empty collection, this method will have no effect.

        Returns:
            the validator instance
        """
        value = self._value()

        if value is not None:
            if isinstance(value, (list, set, tuple)):
                if not all(isinstance(entry, basestring) for entry in value):
                    raise ConfluenceConfigurationError(
                        "%s is not a collection of strings" % self.key
                    )
            elif not isinstance(value, basestring):
                raise ConfluenceConfigurationError(
                    "%s is not a string or collection of strings" % self.key
                )

        return self

    def strings(self, no_space=False):
        """
        checks if a configuration is a collection of strings

        After an instance has been set a configuration key (via `conf`), this
        method can be used to check if the value (if any) configured with this
        key is a collection of strings. If not, an
        `ConfluenceConfigurationError` exception will be thrown.

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
            if not (
                isinstance(value, (list, set, tuple))
                and all(isinstance(entry, basestring) for entry in value)
            ):
                raise ConfluenceConfigurationError(
                    "%s is not a collection of strings" % self.key
                )

            if no_space:
                for entry in value:
                    if " " in entry:
                        raise ConfluenceConfigurationError(
                            "%s has an entry containing a space" % self.key
                        )

        return self

    def _value(self, permit_empty=False):
        """
        return a value for a configuration

        Return the value (if any) of the provided key found in the registered
        builder's configuration. If any configuration translator is set for a
        key, the translation will be performed and returned with this call.

        Args:
            permit_empty (optional): whether or not all an empty string of this
                                      value is considered to be a set value

        Returns:
            the value for a key
        """
        value = getattr(self.config, self.key)

        if value is not None and self._translate:
            value = self._translate(value)

        # If an empty string, treat (in most cases) that this value is actually
        # a `None` value. This permits callers from passing "empty"/unset
        # configuration entries via the command line to "clear" a configuration
        # value. Note that this does not apply to all configuration entries (for
        # example, see `confluence_secnumber_suffix`).
        if not permit_empty and isinstance(value, basestring) and not value:
            value = None

        return value
