# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2017-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from sphinxcontrib.confluencebuilder.builder import ConfluenceBuilder
from tests.lib import assertExpectedWithOutput
from tests.lib import buildSphinx
from tests.lib import prepareConfiguration
from tests.lib import prepareDirectories
import os
import shutil
import tempfile
import unittest

class TestImageStar(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        test_dir = os.path.dirname(os.path.realpath(__file__))
        cls.image_file = os.path.join(test_dir, 'assets', 'image01.png')
        cls.image_basename = cls.file_basename(cls.image_file)
        cls.datasetdir = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(self.datasetdir)

    @staticmethod
    def file_basename(filepath):
        return os.path.basename(filepath).rsplit('.')[0]

    @staticmethod
    def file_extension(filepath):
        return os.path.basename(filepath).rsplit('.')[1]

    def build_document_given_dataset(self, dataset):
        config = prepareConfiguration()
        doc_dir, doctree_dir = prepareDirectories('image-star')
        buildSphinx(dataset, doc_dir, doctree_dir, config)
        return doc_dir

    def write_index_file(self, indexfile):
        with open(indexfile, 'w') as out:
            out.write('.. image:: {}.*'.format(self.image_basename))

    def write_expected_index_file(self, outfile, actual_extension):
        ''' writes the expected content into outfile using
        the actual extension
        '''
        image_filename = self.image_basename + '.' + actual_extension
        content = '<ri:attachment ri:filename="{}">'.format(image_filename)
        content += '</ri:attachment>\n'
        content = '<ac:image>\n' + content + '</ac:image>'
        with open(outfile, 'w') as out:
            out.write(content)

    def test_image_ending_with_star(self):
        ''' Test how Confluence Builder resolves the image path when
        it ends with star (*).
        A temporary datasetdir is created to store::
        - image with the extension as the image type to be tested (png): copy
          of the image01.png from assets folder
        - index.rst: created on the fly using star notation
        - expected output file: expected_index.conf (created on the fly too)

        Sphinx builders finds the png as the candidate. Similar tests
        can be created for all ConfluenceBuilder.supported_image_types
        but it requires an actual image of each image type.
        '''
        image_extension = self.file_extension(self.image_file)
        self.assertIn('image/' + image_extension,
                      ConfluenceBuilder.supported_image_types)
        shutil.copyfile(
            self.image_file,
            os.path.join(self.datasetdir,
                         self.image_basename + '.' + image_extension))

        self.write_index_file(os.path.join(self.datasetdir, 'index.rst'))
            
        expected_outfile = os.path.join(self.datasetdir,
                                        'expected_index.conf')
        self.write_expected_index_file(expected_outfile, image_extension)

        doc_dir = self.build_document_given_dataset(self.datasetdir)
        assertExpectedWithOutput(self,
                                   self.file_basename(expected_outfile),
                                   self.datasetdir,
                                   doc_dir,
                                   tpn='index')
