# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from sphinx.environment.adapters.indexentries import IndexEntries
from sphinxcontrib.confluencebuilder.state import ConfluenceState
from sphinxcontrib.confluencebuilder.storage import intern_uri_anchor_value
import pkgutil
import posixpath
import os


def generate_storage_format_domainindex(builder, docname, f):
    """
    generate the domain index content for the builder into the provided file

    This call can be used to generate a domain index for a provided builder.
    This generated index can then be included in the list of documents to be
    published to an instance.

    Args:
        builder: the builder
        docname: the docname
        f: the file to write to
    """

    _, content = builder.domain_indices[docname]
    if not content:
        return

    # pre-process link entries to use final document titles/anchor values
    for key, entries in content:
        for (i, entry) in enumerate(entries):
            if isinstance(entry, list):
                refuri = '{}#{}'.format(entry[2], entry[3])
                doctitle, anchor_value = process_doclink(builder.config, refuri)
                entry[2] = doctitle
                entry[3] = anchor_value
            else:
                refuri = '{}#{}'.format(entry.docname, entry.anchor)
                doctitle, anchor_value = process_doclink(builder.config, refuri)
                entries[i] = entries[i]._replace(
                    docname=doctitle, anchor=anchor_value)

    # fetch raw template data
    domainindex_template = os.path.join('templates', 'domainindex.html')
    template_data = pkgutil.get_data(__name__, domainindex_template)

    # process the template with the generated index
    ctx = {
        'index': content,
    }
    output = builder.templates.render_string(template_data.decode('utf-8'), ctx)
    f.write(output)


def generate_storage_format_genindex(builder, docname, f):
    """
    generate the genindex content for the builder into the provided file

    This call can be used to generate an index for a provided builder. This
    generated index can then be included in the list of documents to be
    published to an instance.

    Args:
        builder: the builder
        docname: the docname
        f: the file to write to
    """

    genindex = IndexEntries(builder.env).create_index(builder)
    if not genindex:
        return

    # pre-process link entries to use final document titles/anchor values
    for key, columns in genindex:
        for entryname, (links, subitems, key_) in columns:
            for (i, (ismain, link)) in enumerate(links):
                links[i] = (
                    ismain, process_doclink(builder.config, link))
            for subentryname, subentrylinks in subitems:
                for (i, (ismain, link)) in enumerate(subentrylinks):
                    subentrylinks[i] = (
                        ismain, process_doclink(builder.config, link))

    # fetch raw template data
    genindex_template = os.path.join('templates', 'genindex.html')
    template_data = pkgutil.get_data(__name__, genindex_template)

    # process the template with the generated index
    ctx = {
        'index': genindex,
    }
    output = builder.templates.render_string(template_data.decode('utf-8'), ctx)
    f.write(output)


def process_doclink(config, refuri):
    """
    process a generated index link entry

    This call is used to process a index-generated link value -- to translate a
    docname/anchor value to a final document title/anchor value. This is to
    better prepare an index for the template to easily work with.

    Args:
        config: the active configuration
        refuri: the uri

    Returns:
        the document's title and anchor value
    """

    docname = posixpath.normpath(os.path.splitext(refuri.split('#')[0])[0])
    doctitle = ConfluenceState.title(docname)
    anchor_value = intern_uri_anchor_value(config, docname, refuri)

    return doctitle, anchor_value
