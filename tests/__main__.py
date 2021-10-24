# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2018-2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib import enable_sphinx_info
import argparse
import fnmatch
import os
import sys
import unittest

# default verbosity for unit tests
DEFAULT_VERBOSITY = 2

def main():
    """
    process main for unit tests

    This method will prepare the test suite, load listed test classes and
    perform a run.
    """
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--help', '-h', action='store_true')
    parser.add_argument('--unbuffered', '-U', action='store_true')
    parser.add_argument('--verbose', '-V', action='count', default=0)

    args, _ = parser.parse_known_args()
    if args.help:
        print(usage())
        sys.exit(0)

    # toggle verbose mode (if provided)
    buffered = not args.unbuffered
    verbosity = 0
    if args.verbose:
        buffered = False

        try:
            verbosity = int(args.verbose)
            verbosity -= 1 # ignore first level for 'status' information
        except ValueError:
            pass

        enable_sphinx_info(verbosity=verbosity)

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
        target_unit_tests, issued = find_tests(unit_tests,
            target_unit_test_name_pattern)
        if not target_unit_tests:
            print('\nERROR: unable to find test with pattern: '
                '{}\n'.format(target_unit_test_name_pattern))
            if issued:
                issued[0].debug()
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
    runner = unittest.TextTestRunner(buffer=buffered,
        verbosity=DEFAULT_VERBOSITY)
    return 0 if runner.run(suite).wasSuccessful() else 1

def find_tests(entity, pattern):
    """
    search for a unit test with a matching wildcard pattern

    Looks for the first 'unittest.case.TestCase' instance where its identifier
    matches the provided wildcard pattern.
    """
    found_tests = []
    issued_tests = []

    if isinstance(entity, unittest.case.TestCase):
        if fnmatch.fnmatch(entity.id(), '*{}*'.format(pattern)):
            return [entity], None

        failed_test_check = ['LoadTestsFailure', 'ModuleImportFailure']
        if any(x in entity.id() for x in failed_test_check):
            issued_tests.append(entity)

    elif isinstance(entity, unittest.TestSuite):
        for subentity in entity:
            found, issued = find_tests(subentity, pattern)
            if found:
                found_tests.extend(found)
            if issued:
                issued_tests.extend(issued)

    return found_tests, issued_tests

def usage():
    """
    display the usage for invoking the unit test engine

    Returns a command line usage string for all options available when invoking
    extension-specific help options.

    Returns:
        the usage string
    """
    return ("""test-engine <options> [test-pattern]

A user can provide a test pattern to use when searching for a subset of unit
tests to run for this execution.

(options)
 -h, --help            show this help
 -V, --verbose         enable verbose messages
""")

if __name__ == "__main__":
    sys.exit(main())
