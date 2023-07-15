extensions = [
    'myst_parser',
    'sphinxcontrib.confluencebuilder',
]

rst_prolog = '''

.. role:: strike
    :class: strike

'''

html_static_path = ['_static']

def setup(app):
    app.add_css_file('test.css')
