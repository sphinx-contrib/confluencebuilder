import unittest
from sphinx.application import Sphinx
import os


class TestConfluenceBuilder(unittest.TestCase):
    def setUp(self):
        srcdir = os.path.join(os.getcwd(), 'testproj')
        self.outdir = os.path.join(srcdir, 'out')
        confdir = srcdir
        doctreedir = os.path.join(srcdir, 'doctree')

        self.app = Sphinx(srcdir, confdir, self.outdir, doctreedir, 'confluence')

    def test_registry(self):
        self.assertTrue('sphinxcontrib.confluencebuilder' in self.app._extensions.keys())

    def test_build(self):
        self.app.build(force_all=True)
        test_path = os.path.join(self.outdir, 'test.conf')
        self.assertTrue(os.path.exists(test_path))

        with open(test_path, 'r') as test_file:
            lines = test_file.readlines()

            self.assertEqual(lines[0], "h1. HEADING_TEST\n")
            self.assertEqual(lines[1], '\n')
            self.assertEqual(lines[2], 'h2. SUBHEADER_TEST\n')

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())