# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from sphinxcontrib.confluencebuilder.std.confluence import SUPPORTED_IMAGE_TYPES
from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import prepare_dirs
import mimetypes
import shutil
import sys


class TestConfluenceSphinxImageCandidate(ConfluenceTestCase):
    @setup_builder('confluence')
    def test_storage_sphinx_image_candidate(self):
        sample_img = self.assets_dir / 'test.png'

        for mime_type in SUPPORTED_IMAGE_TYPES:
            ext = mimetypes.guess_extension(mime_type)

            # handle python 3.7 interpreter | image/x-ms-bmp -> image/bmp
            # https://bugs.python.org/issue22589
            if not ext and mime_type == 'image/x-ms-bmp':
                ext = mimetypes.guess_extension('image/bmp')

            self.assertIsNotNone(ext)

            pyver = f'py{sys.version_info.major}{sys.version_info.minor}'
            doc_dir = prepare_dirs(postfix=f'-{pyver}-docs-{ext[1:]}')
            out_dir = prepare_dirs(postfix=f'-{pyver}-out-{ext[1:]}')

            # prepare documentation set
            #  - create and index document with an asterisk image extension
            #  - copies over an image which should be mapped; note that a real
            #     image is needed as the contents can be parsed through sphinx
            #     to see if its a real image before considering it to be a
            #     candidate
            doc_dir.mkdir(parents=True, exist_ok=True)

            index_file = doc_dir / 'index.rst'
            with index_file.open('w') as f:
                f.write('.. image:: candidate.*')

            img_filename = 'candidate' + ext
            dummy_img_file = doc_dir / img_filename
            shutil.copyfile(sample_img, dummy_img_file)

            # build and check
            self.build(doc_dir, out_dir=out_dir)

            with parse('index', out_dir) as data:
                image = data.find('ac:image')
                self.assertIsNotNone(image)

                attachment = image.find('ri:attachment', recursive=False)
                self.assertIsNotNone(attachment)
                self.assertTrue(attachment.has_attr('ri:filename'))
                self.assertEqual(attachment['ri:filename'], img_filename)
