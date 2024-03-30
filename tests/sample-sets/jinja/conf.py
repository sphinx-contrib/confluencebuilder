from datetime import datetime
from datetime import timezone
from pathlib import Path
import json


extensions = [
    'sphinx_jinja',
    'sphinxcontrib.confluencebuilder',
]


# load sample data
test_dir = Path(__file__).parent.resolve()
data = test_dir / 'test.json'

with data.open('rb') as f:
    data = json.load(f)

for feature in data['features']:
    raw_sec = float(feature['properties']['time'])/1000
    ts = datetime.fromtimestamp(raw_sec, tz=timezone.utc)
    feature['properties']['time_str'] = ts.strftime('%Y-%m-%dT%H:%M:%SZ')

# inject data for our directive
jinja_contexts = {
    'ctx': data,
}
