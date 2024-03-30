extensions = [
    'sphinxcontrib.confluencebuilder',
]

# language override
language = 'cs'

# use options which generate text
confluence_include_search = True
confluence_page_generation_notice = True
confluence_sourcelink = {
    'type': 'github',
    'owner': 'sphinx-contrib',
    'repo': 'confluencebuilder',
    'container': 'doc/',
    'version': 'main',
    'view': 'edit',
}
confluence_use_index = True
