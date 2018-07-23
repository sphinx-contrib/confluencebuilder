# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2016-2018 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from __future__ import unicode_literals
from .exceptions import ConfluenceError
from docutils import nodes
from docutils.nodes import NodeVisitor as BaseTranslator

class ConfluenceTranslator(BaseTranslator):
    """
    confluence extension translator

    Translator instance for the Confluence extension for Sphinx. This
    implementation is responsible for processing individual documents based on
    parsed node entries provided by docutils (used by Sphinx).

    Args:
        document: the document being translated
        builder: the sphinx builder instance
    """
    def __init__(self, document, builder):
        BaseTranslator.__init__(self, document)
        self.builder = builder

        self.body = []
        self.context = []
        self.nl = '\n'

    # ##########################################################################
    # #                                                                        #
    # # base translator overrides                                              #
    # #                                                                        #
    # ##########################################################################

    def visit_document(self, node):
        pass

    def depart_document(self, node):
        self.document = ''.join(self.body)

    def visit_Text(self, node):
        text = node.astext()
        text = self._escape_sf(text)
        self.body.append(text)
        raise nodes.SkipNode

    def unknown_visit(self, node):
        raise NotImplementedError('unknown node: ' + node.__class__.__name__)

    # ##########################################################################
    # #                                                                        #
    # # helpers                                                                #
    # #                                                                        #
    # ##########################################################################

    def _start_tag(self, node, tag, suffix=None, empty=False, **kwargs):
        """
        generates start tag content for a given node

        A helper used to return content to be appended to a document which
        initializes the start of a storage format element (i.e. generates a
        start tag). The element of type `tag` will be initialized. This method
        may use provided `node` to tweak the final content.

        Args:
            node: the node processing the start-tag
            tag: the type of tag
            suffix (optional): the suffix to add (defaults to nothing)
            empty (optional): tag will not hold child nodes (defaults to False)
            **kwargs (optional): dictionary of attributes to include in the tag

        Returns:
            the content
        """
        tag = tag.lower()
        data = [tag]

        attribs = {}
        for key, value in kwargs.items():
            attribs[key.lower()] = value

        for key, value in attribs.items():
            data.append('{}="{}"'.format(key, value))

        if suffix is None:
            suffix = ''

        suffix = '>' + suffix
        if empty:
            suffix = ' /' + suffix
        else:
            try:
                node.__confluence_tag.append(tag)
            except AttributeError:
                node.__confluence_tag = [tag]

        return '<{}{}'.format(' '.join(data), suffix)

    def _end_tag(self, node, suffix=None):
        """
        generates end tag content for a given node

        A helper used to return content to be appended to a document which
        finalizes a storage format element (i.e. generates an end tag). This
        method should* be used to help close a _start_tag call (*with the
        exception of when _start_tag is invoked with empty=True).

        Args:
            node: the node processing the end-tag
            suffix (optional): the suffix to add (defaults to newline)

        Returns:
            the content
        """
        try:
            tag = node.__confluence_tag.pop()
        except:
            raise ConfluenceError('end tag invoke without matching start tag')

        if suffix is None:
            suffix = self.nl

        return '</{}>{}'.format(tag, suffix)

    def _build_ac_parameter(self, node, name, value):
        """
        generates a confluence parameter element

        A helper used to return content to be appended to a document which
        builds a complete storage format parameter element. The 'ac:parameter'
        element will be built. This method may use provided `node` to tweak the
        final content.

        Args:
            node: the node processing the parameter
            name: the parameter name
            value: the value for the parameter

        Returns:
            the content
        """
        return (self._start_tag(node, 'ac:parameter', **{'ac:name': name}) +
            value + self._end_tag(node))

    def _start_ac_link(self, node, anchor=None):
        """
        generates a confluence link start tag

        A helper used to return content to be appended to a document which
        initializes the start of a storage format link element of a specific
        `type`. The 'ac:link' element will be initialized. This method may use
        provided `node` to tweak the final content.

        Args:
            node: the node processing the link
            anchor (optional): the anchor value to use (defaults to None)

        Returns:
            the content
        """
        attribs = {}
        if anchor:
            attribs['ac:anchor'] = anchor
        return self._start_tag(node, 'ac:link', suffix=self.nl, **attribs)

    def _end_ac_link(self, node):
        """
        generates confluence link end tag content for a node

        A helper used to return content to be appended to a document which
        finalizes a storage format link element. This method should be used to
        help close a _start_ac_link call.

        Args:
            node: the node processing the link

        Returns:
            the content
        """
        return self._end_tag(node, suffix='')

    def _start_ac_macro(self, node, type, empty=False):
        """
        generates a confluence macro start tag

        A helper used to return content to be appended to a document which
        initializes the start of a storage format macro element of a specific
        `type`. The 'ac:structured-macro' element will be initialized. This
        method may use provided `node` to tweak the final content.

        Args:
            node: the node processing the macro
            type: the type of macro
            empty (optional): tag will not hold child nodes (defaults to False)

        Returns:
            the content
        """
        return self._start_tag(node, 'ac:structured-macro',
            suffix=self.nl, empty=empty, **{'ac:name': type})

    def _end_ac_macro(self, node):
        """
        generates confluence macro end tag content for a node

        A helper used to return content to be appended to a document which
        finalizes a storage format macro element. This method should* be used to
        help close a _start_ac_macro call (*with the exception of when
        _start_ac_macro is invoked with empty=True).

        Args:
            node: the node processing the macro

        Returns:
            the content
        """
        return self._end_tag(node)

    def _start_ac_rich_text_body_macro(self, node):
        """
        generates a confluence rich-text-body start tag

        A helper used to return content to be appended to a document which
        initializes the start of a storage format rich-text-body element. The
        'ac:rich-text-body' element will be initialized. This method may use
        provided `node` to tweak the final content.

        Args:
            node: the node processing the macro

        Returns:
            the content
        """
        return self._start_tag(node, 'ac:rich-text-body', suffix=self.nl)

    def _end_ac_rich_text_body_macro(self, node):
        """
        generates confluence rich-text-body end tag content for a node

        A helper used to return content to be appended to a document which
        finalizes a storage format rich-text-body element. This method should
        be used to help close a _start_ac_rich_text_body_macro call.

        Args:
            node: the node processing the macro

        Returns:
            the content
        """
        return self._end_tag(node)

    def _start_ac_plain_text_body_macro(self, node):
        """
        generates a confluence plain-text-body start tag

        A helper used to return content to be appended to a document which
        initializes the start of a storage format plain-text-body element. The
        'ac:plain-text-body' element will be initialized. This method may use
        provided `node` to tweak the final content.

        Args:
            node: the node processing the macro

        Returns:
            the content
        """
        return self._start_tag(node, 'ac:plain-text-body', suffix='<![CDATA[')

    def _end_ac_plain_text_body_macro(self, node):
        """
        generates confluence plain-text-body end tag content for a node

        A helper used to return content to be appended to a document which
        finalizes a storage format plain-text-body element. This method should
        be used to help close a _start_ac_plain_text_body_macro call.

        Args:
            node: the node processing the macro

        Returns:
            the content
        """
        return ']]>' + self._end_tag(node)

    def _start_ac_plain_text_link_body_macro(self, node):
        """
        generates a confluence plain-text-link-body start tag

        A helper used to return content to be appended to a document which
        initializes the start of a storage format plain-text-body element. The
        'ac:plain-text-body' element will be initialized. This method may use
        provided `node` to tweak the final content.

        Args:
            node: the node processing the macro

        Returns:
            the content
        """
        return self._start_tag(node, 'ac:plain-text-link-body',
            suffix='<![CDATA[')

    def _end_ac_plain_text_link_body_macro(self, node):
        """
        generates confluence plain-text-link-body end tag content for a node

        A helper used to return content to be appended to a document which
        finalizes a storage format plain-text-link-body element. This method
        should be used to help close a _start_ac_plain_text_link_body_macro
        call.

        Args:
            node: the node processing the macro

        Returns:
            the content
        """
        return ']]>' + self._end_tag(node)

    def _escape_cdata(self, data):
        """
        escapes text to be inserted into a cdata

        A helper used to return content that has been properly escaped and can
        be directly placed inside a CDATA container.

        Args:
            data: the text

        Returns:
            the escaped text
        """
        return data.replace(']]>', ']]]]><![CDATA[>')

    def _escape_sf(self, data):
        """
        escapes text to be inserted directly into a storage format area

        A helper used to return content that has been properly escaped and can
        be directly placed inside a Confluence storage-format-prepared document.

        Args:
            data: the text

        Returns:
            the escaped text
        """
        STORAGE_FORMAT_REPLACEMENTS = {
            ('<', '&lt;'),
            ('>', '&gt;'),
            ('"', '&quot;'),
            ("'", '&apos;'),
        }

        # first pass needs to handle ampersand
        data = data.replace('&', '&amp;')

        for find, encoded in STORAGE_FORMAT_REPLACEMENTS:
            data = data.replace(find, encoded)
        return data
