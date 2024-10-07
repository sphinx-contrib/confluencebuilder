extensions = [
    'sphinxcontrib.confluencebuilder',
    'sphinx.ext.linkcode',
]

def linkcode_resolve(domain, info):
    name = info.get('fullname', None)
    if not name:
        return None
    return  f'https://example.org/src/{name}'
