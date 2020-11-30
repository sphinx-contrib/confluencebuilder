# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2017-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'Sphinx Confluence Builder'
copyright = '2020 Sphinx Confluence Builder Contributors'
author = 'Sphinx Confluence Builder Contributors'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = ''
# The full version, including alpha/beta/rc tags.
release = ''

# reStructuredText string included at the end of every source
rst_epilog = """
.. |supported_confluence_ver| replace:: 6.13+
.. |supported_python_ver| replace:: 2.7 or 3.6+
.. |supported_sphinx_ver| replace:: 1.8 or 2.4+
"""

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# -- Application hook -----------------------------------------------------

def setup(app):
    # append theme override
    app.add_css_file('theme_overrides.css')

    # append unreleased version-alert
    app.add_js_file('version-alert.js')
