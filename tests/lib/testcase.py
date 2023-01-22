# SPDX-License-Identifier: BSD-2-Clause
# Copyright 2022-2023 Sphinx Confluence Builder Contributors (AUTHORS)

from functools import wraps
from tests.lib import build_sphinx
from tests.lib import prepare_conf
from tests.lib import prepare_sphinx
import os
import unittest

# default builder to test against
DEFAULT_BUILDER = 'confluence'


class ConfluenceTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        """
        confluence test case

        Provides a test case for unit testing which includes helper calls to
        build/prepare Sphinx environments and helps managing parsing. Unit
        tests can take advantage of available decorators to help configure
        their setups.

        For example:

            @setup_builder('confluence')
            def test_storage_example(self):
                out_dir = self.build(self.dataset)

                ...
        """

        super(ConfluenceTestCase, self).__init__(*args, **kwargs)

        self.builder = DEFAULT_BUILDER

    @classmethod
    def setUpClass(cls):
        # always prepare a dummy configuration a unit test could use
        cls.config = prepare_conf()

        # provide a reference to common directories
        lib_dir = os.path.dirname(os.path.realpath(__file__))
        tests_dir = os.path.join(lib_dir, os.pardir)
        unit_tests_dir = os.path.join(tests_dir, 'unit-tests')

        cls.assets_dir = os.path.join(unit_tests_dir, 'assets')
        cls.datasets = os.path.join(unit_tests_dir, 'datasets')
        cls.templates_dir = os.path.join(unit_tests_dir, 'templates')

    def build(self, *args, **kwargs):
        """
        helper to invoke `build_sphinx` with decorator configured options

        Args:
            *args: argument values to forward
            **kwargs: kw-argument values to forward
        """

        new_kwargs = dict(kwargs)
        new_kwargs.setdefault('builder', self.builder)
        new_kwargs.setdefault('config', self.config)

        return build_sphinx(*args, **new_kwargs)

    def prepare(self, *args, **kwargs):
        """
        helper to invoke `prepare_sphinx` with decorator configured options

        Args:
            *args: argument values to forward
            **kwargs: kw-argument values to forward
        """

        new_kwargs = dict(kwargs)
        new_kwargs.setdefault('builder', self.builder)
        new_kwargs.setdefault('config', self.config)

        return prepare_sphinx(*args, **new_kwargs)


def setup_builder(builder):
    """
    prepare a confluence unit test for a specific builder configuration

    A utility "decorator" to help setup builder options for a unit test. This
    avoids the need to explicitly configure a builder options directly in a
    build/prepare call for a unit test testing against a dataset.

    Args:
        builder: the builder to use
    """

    def _decorator(func):
        @wraps(func)
        def _wrapper(self, *args, **kwargs):
            self.builder = builder

            return func(self, *args, **kwargs)
        return _wrapper
    return _decorator
