from pathlib import Path
import sys


extensions = [
    'sphinx_click',
    'sphinxcontrib.confluencebuilder',
]


test_dir = Path(__file__).parent.resolve()
sys.path.insert(0, test_dir)
