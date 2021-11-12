# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2017-2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from sphinxcontrib.confluencebuilder.std.confluence import SUPPORTED_IMAGE_TYPES
from tests.lib import build_sphinx
from tests.lib import parse
from tests.lib import prepare_conf
from tests.lib import prepare_dirs
import mimetypes
import os
import shutil
import sys
import unittest


class TestConfluenceSphinxImageCandidate(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        self.test_dir = os.path.dirname(os.path.realpath(__file__))

    def test_storage_sphinx_image_candidate(self):
        config = prepare_conf()

        assets_dir = os.path.join(self.test_dir, 'assets')
        sample_img = os.path.join(assets_dir, 'test.png')

        for mime_type in SUPPORTED_IMAGE_TYPES:
            ext = mimetypes.guess_extension(mime_type)

            # handle python 3.7 interpreter | image/x-ms-bmp -> image/bmp
            # https://bugs.python.org/issue22589
            if not ext and mime_type == 'image/x-ms-bmp':
                ext = mimetypes.guess_extension('image/bmp')

            self.assertIsNotNone(ext)

            pyver = 'py{}{}'.format(sys.version_info.major,
                sys.version_info.minor)
            doc_dir = prepare_dirs(postfix='-{}-docs-{}'.format(pyver, ext[1:]))
            out_dir = prepare_dirs(postfix='-{}-out-{}'.format(pyver, ext[1:]))

            # prepare documentation set
            #  - create and index document with an asterisk image extension
            #  - copies over an image which should be mapped; note that a real
            #     image is needed as the contents can be parsed through sphinx
            #     to see if its a real image before considering it to be a
            #     candidate
            os.makedirs(doc_dir)

            index_file = os.path.join(doc_dir, 'index.rst')
            with open(index_file, 'w') as f:
                f.write('.. image:: candidate.*')

            img_filename = 'candidate' + ext
            dummy_img_file = os.path.join(doc_dir, img_filename)
            shutil.copyfile(sample_img, dummy_img_file)

            # build and check
            build_sphinx(doc_dir, config=config, out_dir=out_dir)

            with parse('index', out_dir) as data:
                image = data.find('ac:image')
                self.assertIsNotNone(image)

                attachment = image.find('ri:attachment', recursive=False)
                self.assertIsNotNone(attachment)
                self.assertTrue(attachment.has_attr('ri:filename'))
                self.assertEqual(attachment['ri:filename'], img_filename)
