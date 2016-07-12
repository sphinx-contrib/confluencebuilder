import unittest
from sphinx.application import Sphinx
import os


class FakeServerProxy(object):
    def __init__(self, server):
        self.server = server


class TestConfluenceBuilder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        srcdir = os.path.join(os.getcwd(), 'testproj')
        cls.outdir = os.path.join(srcdir, 'out')
        confdir = srcdir
        doctreedir = os.path.join(srcdir, 'doctree')
        cls.app = Sphinx(srcdir, confdir, cls.outdir, doctreedir, 'confluence')
        cls.app.build(force_all=True)

    def test_registry(self):
        self.assertTrue('sphinxcontrib.confluencebuilder' in
                        self.app._extensions.keys())

    def test_heading(self):
        test_path = os.path.join(self.outdir, 'heading.conf')
        self.assertTrue(os.path.exists(test_path))

        with open(test_path, 'r') as test_file:
            lines = test_file.readlines()

            self.assertEqual(lines[0], "h1. HEADING_TEST\n")
            self.assertEqual(lines[1], '\n')
            self.assertEqual(lines[2], 'h2. SUBHEADER_TEST\n')

    def test_list(self):
        test_path = os.path.join(self.outdir, 'list.conf')
        self.assertTrue(os.path.exists(test_path))

        with open(test_path, 'r') as test_file:
            lines = test_file.readlines()
            self.assertEqual(lines[0], 'h1. list test\n')
            self.assertEqual(lines[1], '\n')
            self.assertEqual(lines[2], "* BULLET_1\n")
            self.assertEqual(lines[3], '* BULLET_2\n')
            self.assertEqual(lines[4], '\n')
            self.assertEqual(lines[5], "# ENUMERATED_1\n")
            self.assertEqual(lines[6], '# ENUMERATED_2\n')

    def test_formatting(self):
        test_path = os.path.join(self.outdir, 'text.conf')
        self.assertTrue(os.path.exists(test_path))

        with open(test_path, 'r') as test_file:
            lines = test_file.readlines()
            self.assertEqual(lines[0], 'h1. this is a text test\n')
            self.assertEqual(lines[2], '_emphasis_\n')
            self.assertEqual(lines[4], '*strong emphasis*\n')
            self.assertEqual(lines[6], '[http://website.com/]\n')
            self.assertEqual(lines[10], '----\n')
            self.assertEqual(lines[12], 'End of transition test\n');

    def test_code(self):
        test_path = os.path.join(self.outdir, 'code.conf')
        self.assertTrue(os.path.exists(test_path))

        with open(test_path, 'r') as test_file:
            lines = test_file.readlines()
            self.assertEqual(lines[0], 'h1. Code Test\n')
            self.assertEqual(lines[2], '{code:title=|theme=Default|linenumbers=false|language=py|collapse=false}\n')
            self.assertEqual(lines[4], 'import antigravity\n')
            self.assertEqual(lines[5], 'antigravity.space(){code}\n')

    @unittest.expectedFailure
    def test_toctree(self):
        test_path = os.path.join(self.outdir, 'toctree.conf')
        self.assertTrue(os.path.exists(test_path))

        with open(test_path, 'r') as test_file:
            lines = test_file.readlines()
            self.assertEqual(lines[0], 'h1. TOCTREE\n')
            self.assertEqual(lines[2], '* [Code Test]\n')
            self.assertEqual(lines[3], '* [HEADING_TEST]\n')
            # This assertion fails. I need to program this logic.
            self.assertEqual(lines[4], '   * [HEADING_TEST#subheading-test]\n')

    def test_table(self):
        test_path = os.path.join(self.outdir, 'tables.conf')
        self.assertTrue(os.path.exists(test_path))

        with open(test_path, 'r') as test_file:
            lines = test_file.readlines()
            self.assertEqual(len(lines), 5)
            self.assertEqual(lines[0], 'h1. Table Test\n')
            self.assertEqual(lines[2], '|| A     || B     || A or B ||\n')
            self.assertEqual(lines[3], '| False | False | False  |\n')
            self.assertEqual(lines[4], '| True  | False | True   |\n')

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())