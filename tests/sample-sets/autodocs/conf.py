from pathlib import Path
import sys


extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinxcontrib.confluencebuilder',
]


test_dir = Path(__file__).parent.resolve()
src_dir = test_dir / 'src'
sys.path.insert(0, str(src_dir))
