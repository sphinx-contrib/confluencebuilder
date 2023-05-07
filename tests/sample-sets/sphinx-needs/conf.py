from docutils.parsers.rst import directives

extensions = [
    'sphinx_needs',
    'sphinxcontrib.confluencebuilder',
]

# confluence_editor = 'v2'
# confluence_full_width = False

needs_extra_options = {
    'author': directives.unchanged,
}

needs_layouts = {
    'example': {
        'grid': 'simple_side_right_partial',
        'layout': {
            'head': ['**<<meta("title")>>** for *<<meta("author")>>*'],
            'meta': ['**status**: <<meta("status")>>',
                     '**author**: <<meta("author")>>'],
            'side': ['<<image("_images/{{author}}.png", align="center")>>']
        }
    }
}

# html builder options (to compare)
html_static_path = ['_static']

def setup(app):
    app.require_sphinx('6.0')
    app.add_js_file('jquery-3.6.3.min.js')
