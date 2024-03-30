from datetime import datetime
import json
import os


extensions = [
    'sphinx_jinja',
    'sphinxcontrib.confluencebuilder',
]


# load sample data
test_dir = os.path.dirname(os.path.realpath(__file__))
data = os.path.join(test_dir, 'test.json')

with open(data, 'rb') as f:
    data = json.load(f)

for feature in data['features']:
    raw_sec = float(feature['properties']['time'])/1000
    ts = datetime.fromtimestamp(raw_sec)
    feature['properties']['time_str'] = ts.strftime('%Y-%m-%dT%H:%M:%SZ')

# inject data for our directive
jinja_contexts = {
    'ctx': data,
}
