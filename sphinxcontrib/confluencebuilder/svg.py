# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from hashlib import sha256
from sphinx.util.images import guess_mimetype
from sphinx.util.osutil import ensuredir
from sphinxcontrib.confluencebuilder.util import convert_px_length
from sphinxcontrib.confluencebuilder.util import extract_length
from sphinxcontrib.confluencebuilder.util import find_env_abspath
import os
import xml.etree.ElementTree as xml_et


# xml declaration string
XML_DEC = b'<?xml version="1.0" encoding="UTF-8" standalone="no"?>'


def svg_initialize():
    """
    initialize support for processing svgs

    The following call will initialize this extension to help support processing
    SVG files which need manipulation.
    """

    # prevent ns0 namespace introduction if ever generating svg files
    xml_et.register_namespace('', 'http://www.w3.org/2000/svg')


def confluence_supported_svg(builder, node):
    """
    process an image node and ensure confluence-supported svg  (if applicable)

    SVGs have some limitations when being presented on a Confluence instance.
    The following have been observed issues:

    1) If an SVG file does not have an XML declaration, Confluence will fail to
       render an image.
    2) If an `ac:image` macro is applied custom width/height values on an SVG,
       Confluence Confluence will fail to render the image.

    This call will process a provided image node and ensure an SVG is in a ready
    state for publishing. If a node is not an SVG, this method will do nothing.

    To support custom width/height fields for an SVG image, the image file
    itself will be modified to an expected lengths. Any hints in the
    documentation using width/height or scale, the desired width and height
    fields of an image will calculated and replaced/injected into the SVG image.

    Any SVG files which do not have an XML declaration will have on injected.

    Args:
        builder: the builder
        node: the image node to check
    """

    uri = node['uri']

    # ignore external/embedded images
    if uri.find('://') != -1 or uri.startswith('data:'):
        return

    # invalid uri/path
    uri_abspath = find_env_abspath(builder.env, builder.outdir, uri)
    if not uri_abspath:
        return

    # ignore non-svgs
    mimetype = guess_mimetype(uri_abspath)
    if mimetype != 'image/svg+xml':
        return

    try:
        with open(uri_abspath, 'rb') as f:
            svg_data = f.read()
    except (IOError, OSError) as err:
        builder.warn('error reading svg: %s' % err)
        return

    modified = False
    svg_root = xml_et.fromstring(svg_data)

    # determine (if possible) the svgs desired width/height
    svg_height = None
    if 'height' in svg_root.attrib:
        svg_height = svg_root.attrib['height']

    svg_width = None
    if 'width' in svg_root.attrib:
        svg_width = svg_root.attrib['width']

    # try to fallback on the viewbox attribute
    viewbox = False
    if svg_height is None or svg_width is None:
        if 'viewBox' in svg_root.attrib:
            try:
                _, _, svg_width, svg_height = \
                    svg_root.attrib['viewBox'].split(' ')
                viewbox = True
            except ValueError:
                pass

    # if tracking an svg width/height, ensure the sizes are in pixels
    if svg_height:
        svg_height, svg_height_units = extract_length(svg_height)
        svg_height = convert_px_length(svg_height, svg_height_units)
    if svg_width:
        svg_width, svg_width_units = extract_length(svg_width)
        svg_width = convert_px_length(svg_width, svg_width_units)

    # extract length/scale properties from the node
    height, hu = extract_length(node.get('height'))
    scale = node.get('scale')
    width, wu = extract_length(node.get('width'))

    # confluence can have difficulty rendering svgs with only a viewbox entry;
    # if a viewbox is used, use it for the height/width if these options have
    # not been explicitly configured on the directive
    if viewbox and not height and not width:
        height = svg_height
        width = svg_width

    # if only one size is set, fetch (and scale) the other
    if width and not height:
        if svg_height and svg_width:
            height = float(width) / svg_width * svg_height
        else:
            height = width
        hu = wu

    if height and not width:
        if svg_height and svg_width:
            width = float(height) / svg_height * svg_width
        else:
            width = height
        wu = hu

    # if a scale value is provided and a height/width is not set, attempt to
    # determine the size of the image so that we can apply a scale value on
    # the detected size values
    if scale:
        if not height and svg_height:
            height = svg_height
            hu = 'px'

        if not width and svg_width:
            width = svg_width
            wu = 'px'

    # apply scale factor to height/width fields
    if scale:
        if height:
            height = int(round(float(height) * scale / 100))
        if width:
            width = int(round(float(width) * scale / 100))

    # confluence only supports pixel sizes -- adjust any other unit type
    # (if possible) to a pixel length
    if height:
        height = convert_px_length(height, hu)
        if height is None:
            builder.warn('unsupported unit type for confluence: ' + hu)
    if width:
        width = convert_px_length(width, wu)
        if width is None:
            builder.warn('unsupported unit type for confluence: ' + wu)

    # if we have a height/width to apply, adjust the svg
    if height and width:
        svg_root.attrib['height'] = str(height)
        svg_root.attrib['width'] = str(width)
        svg_data = xml_et.tostring(svg_root)
        modified = True

    # ensure xml declaration exists
    if not svg_data.lstrip().startswith(b'<?xml'):
        svg_data = XML_DEC + b'\n' + svg_data
        modified = True

    # ignore svg file if not modifications are needed
    if not modified:
        return

    fname = sha256(svg_data).hexdigest() + '.svg'
    outfn = os.path.join(builder.outdir, builder.imagedir, 'svgs', fname)

    # write the new svg file (if needed)
    if not os.path.isfile(outfn):
        ensuredir(os.path.dirname(outfn))
        try:
            with open(outfn, 'wb') as f:
                f.write(svg_data)
        except (IOError, OSError) as err:
            builder.warn('error writing svg: %s' % err)
            return

    # replace the required node attributes
    node['uri'] = outfn

    if 'height' in node:
        del node['height']
    if 'scale' in node:
        del node['scale']
    if 'width' in node:
        del node['width']
