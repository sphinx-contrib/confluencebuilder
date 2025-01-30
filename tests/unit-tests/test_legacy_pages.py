# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from sphinxcontrib.confluencebuilder.builder import ConfluenceBuilder
from sphinxcontrib.confluencebuilder.util import temp_dir
from tests.lib import prepare_dirs
from tests.lib.testcase import ConfluenceTestCase
from unittest.mock import patch


class TestConfluenceLegacyPages(ConfluenceTestCase):
    def test_legacy_pages(self):
        """validate publisher will store a page by id (default)"""
        #
        # Verify that a publisher can update an existing page by an
        # identifier value. By default, the update request will ensure
        # the user configures to not watch the page.

        config = dict(self.config)
        config['confluence_publish'] = True
        config['confluence_publish_intersphinx'] = False
        config['confluence_server_url'] = 'https://example.com/'
        config['confluence_space_key'] = 'TEST'
        config['confluence_cleanup_purge'] = True

        # prepare a mocked publisher that we can emulate publishing events
        # and check if legacy pages are properly remain/purged
        old_init = ConfluenceBuilder.init
        publisher = MockedPublisher()

        def wrapped_init(builder):
            builder.publisher = publisher
            return old_init(builder)

        # prepare a fixed source and working directory, since we will be
        # performing rebuilds and want to ensure the extension handles
        # rebuilds approriately (e.g. not purging pages that have not been
        # updated but are still valid)
        out_dir = prepare_dirs()

        with temp_dir() as src_dir:
            conf_file = src_dir / 'conf.py'
            write_doc(conf_file, '')

            index_file = src_dir / 'index.rst'
            write_doc(index_file, '''\
index
=====

.. toctree::

    second
    third
''')

            second_file = src_dir / 'second.rst'
            write_doc(second_file, '''\
second
======

content
''')

            third_file = src_dir / 'third.rst'
            write_doc(third_file, '''\
third
=====

content
''')

            # first pass build
            with patch.object(ConfluenceBuilder, 'init', wrapped_init):
                self.build(src_dir, config=config, out_dir=out_dir)

            # all three pages should be "published"
            self.assertEqual(len(publisher.published), 3)

            # rebuild documentations; no pages should be removed even if
            # not pages have been republished (since they are not outdated)
            with patch.object(ConfluenceBuilder, 'init', wrapped_init):
                self.build(src_dir, config=config, out_dir=out_dir, force=False)

            # no pages "published"; no pages removed
            self.assertEqual(len(publisher.published), 0)
            self.assertEqual(len(publisher.removed), 0)

            # remove the second file; update the index to drop the entry
            second_file.unlink()

            write_doc(index_file, '''\
index
=====

.. toctree::

    third
''')

            # rebuild documentations; this should trigger an update of the
            # index page and detect the third page is now legacy
            with patch.object(ConfluenceBuilder, 'init', wrapped_init):
                self.build(src_dir, config=config, out_dir=out_dir, force=False)

            self.assertEqual(len(publisher.published), 1)
            self.assertListEqual(publisher.published, [
                'index',
            ])

            self.assertEqual(len(publisher.removed), 1)
            self.assertListEqual(publisher.removed, [
                'second',
            ])


class MockedPublisher:
    base_page_idx = 2
    page2id = {}
    id2page = {}

    def init(self, config, cloud=None):
        self.published = []
        self.removed = []

    def get_base_page_id(self):
        return 1

    def get_descendants(self, page_id, mode):
        return set(self.id2page.keys())

    def remove_page(self, page_id):
        page_name = self.id2page.get(page_id)
        self.removed.append(page_name)

    def store_page(self, page_name, data, parent_id=None):
        page_id = self.page2id.get(page_name)
        if not page_id:
            page_id = self.base_page_idx
            self.base_page_idx += 1

            self.page2id[page_name] = page_id
            self.id2page[page_id] = page_name

        self.published.append(page_name)

        return page_id

    # other unused methods

    def connect(self):
        pass

    def disconnect(self):
        pass

    def get_ancestors(self, page_id):
        return set()

    def get_attachments(self, page_id):
        return {}

    def restrict_ancestors(self, ancestors):
        pass

    def store_attachment(self, page_id, name, data, mimetype, hash_, force=False):
        return 0


def write_doc(file, data):
    try:
        with file.open('w') as f:
            f.write(data)
    except OSError:
        pass
