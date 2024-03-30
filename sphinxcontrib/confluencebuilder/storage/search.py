# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from pathlib import Path
from sphinxcontrib.confluencebuilder.locale import L as sccb_translation  # noqa: N811
import pkgutil


def generate_storage_format_search(builder, docname, f):
    """
    generate the search content for the builder into the provided file

    This call can be used to generate a search document for a provided builder.
    This generated search is then included in the list of documents to be
    published to an instance.

    Args:
        builder: the builder
        docname: the docname
        f: the file to write to
    """

    space_key = builder.config.confluence_space_key

    # fetch raw template data
    search_template = Path('templates', 'search.html')
    template_data = pkgutil.get_data(__name__, str(search_template))

    # process the template with the generated index
    ctx = {
        'L': sccb_translation,
        'pagegen_notice': builder.config.confluence_page_generation_notice,
        'space': space_key,
    }
    output = builder.templates.render_string(template_data.decode('utf-8'), ctx)
    f.write(output)
