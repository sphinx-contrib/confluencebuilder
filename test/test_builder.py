import unittest
from sphinx.application import Sphinx
import os


class TestConfluenceBuilder(unittest.TestCase):
    def setUp(self):
        srcdir = os.path.join(os.getcwd(), 'testproj')
        self.app = Sphinx(srcdir, srcdir, srcdir, srcdir, 'confluence')

    def test_registry(self):
        self.assertTrue('sphinxcontrib.confluencebuilder' in self.app._extensions.keys())

    def test_build(self):
        self.app.build()

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())