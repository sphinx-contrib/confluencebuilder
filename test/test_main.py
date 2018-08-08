# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2018 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from sphinxcontrib_confluencebuilder_util import ConfluenceTestUtil
import fnmatch
import os
import sys
import unittest

"""
default verbosity for unit tests
"""
DEFAULT_VERBOSITY = 2

def main():
    """
    process main for unit tests

    This method will prepare the test suite, load listed test classes and
    perform a run.
    """
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()

    # toggle verbose mode (if provided)
    if '--verbose' in sys.argv or '-V' in sys.argv:
        ConfluenceTestUtil.enableVerbose()

    # discover unit tests
    test_base = os.path.dirname(os.path.realpath(__file__))
    unit_tests_dir = os.path.join(test_base, 'unit-tests')
    unit_tests = loader.discover(unit_tests_dir)

    # check if a unit test name was provided
    #
    # Partially emulation Python's unittest capability by accepting a unit test
    # name value via command line arguments. This is to help testers invoke only
    # a single test (if desired; and in a much more flexible way).
    target_unit_test_name_pattern = None
    for arg in sys.argv[1:]:
        if not arg.startswith('-'):
            target_unit_test_name_pattern = arg
            break

    # register tests
    if target_unit_test_name_pattern:
        target_unit_tests = find_tests(unit_tests, target_unit_test_name_pattern)
        if not target_unit_tests:
            print('ERROR: unable to find test with pattern: '
                '{}'.format(target_unit_test_name_pattern))
            sys.exit(1)

        print('')
        print('running specific test(s) (total: {})'.format(
            len(target_unit_tests)))
        for target_unit_test in target_unit_tests:
            print(' {}'.format(target_unit_test.id()))
        print('')
        sys.stdout.flush()

        suite.addTests(target_unit_tests)
    else:
        suite.addTests(unit_tests)

    # invoke test suite
    runner = unittest.TextTestRunner(verbosity=DEFAULT_VERBOSITY)
    return 0 if runner.run(suite).wasSuccessful() else 1

def find_tests(entity, pattern):
    """
    search for a unit test with a matching wildcard pattern

    Looks for the first 'unittest.case.TestCase' instance where its identifier
    matches the provided wildcard pattern.
    """
    found_tests = []

    if isinstance(entity, unittest.case.TestCase):
        if fnmatch.fnmatch(entity.id(), '*{}*'.format(pattern)):
            return [entity]
    elif isinstance(entity, unittest.TestSuite):
        for subentity in entity:
            found = find_tests(subentity, pattern)
            if found:
                found_tests.extend(found)

    return found_tests

if __name__ == "__main__":
    sys.exit(main())
