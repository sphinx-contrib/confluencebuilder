import unittest
from sphinx.application import Sphinx
import os


class TestConfluenceBuilder(unittest.TestCase):
    def setUp(self):
        srcdir = os.path.join(os.getcwd(), 'testproj')
        self.app = Sphinx(srcdir, srcdir, srcdir, srcdir, 'confluence')

    def test_registry(self):
        self.assertTrue('sphinxcontrib.confluencebuilder' in self.app._extensions.keys())


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())