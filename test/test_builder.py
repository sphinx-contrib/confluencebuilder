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
        self.app.build()
        self.assertTrue(os.path.exists(os.path.join(self.outdir, 'test.conf')))

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())