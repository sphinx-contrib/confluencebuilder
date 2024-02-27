# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from sphinxcontrib.confluencebuilder.util import temp_dir
from tests.lib import prepare_dirs
from tests.lib.testcase import ConfluenceTestCase


class TestCache(ConfluenceTestCase):
    def test_cache_outdated_config(self):
        """validate triggering outdated content with config change"""
        #
        # Ensures documents will be flagged as outdated if a
        # Confluence-specific configuration flags that a rebuild is needed.

        config = dict(self.config)
        dataset = self.datasets / 'minimal'
        out_dir = prepare_dirs()
        src_docs = []

        def doctree_resolved_handler(app, doctree, docname):
            src_docs.append(docname)

        with self.prepare(dataset, config=config, out_dir=out_dir) as app:
            app.connect('doctree-resolved', doctree_resolved_handler)
            app.build()

        self.assertListEqual(src_docs, [
            'index',
        ])

        # re-run with no changes -- no document will be outdated and
        # no source documents will be read
        src_docs.clear()

        with self.prepare(dataset, config=config, out_dir=out_dir) as app:
            app.connect('doctree-resolved', doctree_resolved_handler)
            app.build()

        self.assertListEqual(src_docs, [
        ])

        # re-run with a configuration change that won't trigger a rebuild
        src_docs.clear()
        config['confluence_watch'] = True

        with self.prepare(dataset, config=config, out_dir=out_dir) as app:
            app.connect('doctree-resolved', doctree_resolved_handler)
            app.build()

        self.assertListEqual(src_docs, [
        ])

        # re-run with a configuration change to trigger an outdated doc
        src_docs.clear()
        config['confluence_global_labels'] = [
            'new-label',
        ]

        with self.prepare(dataset, config=config, out_dir=out_dir) as app:
            app.connect('doctree-resolved', doctree_resolved_handler)
            app.build()

        self.assertListEqual(src_docs, [
            'index',
        ])

    def test_cache_outdated_content(self):
        """validate handling outdated content"""
        #
        # Ensures the Sphinx engine will trigger/processed an outdated
        # document. While the results should be expected (since we are
        # basically re-validating a Sphinx capability), the purpose of this
        # test is to ensure no oddities when an environment-flagged outdated
        # document when this extension is loaded.

        added_docs = []
        changed_docs = []
        out_dir = prepare_dirs()

        def env_get_outdated(app, env, added, changed, removed):
            added_docs.clear()
            added_docs.extend(added)
            added_docs.sort()

            changed_docs.clear()
            changed_docs.extend(changed)
            changed_docs.sort()

            return []

        def write_doc(file, data):
            try:
                with file.open('w') as f:
                    f.write(data)
            except OSError:
                pass

        with temp_dir() as src_dir:
            index_file = src_dir / 'index.rst'
            write_doc(index_file, '''\
index
=====

content
''')

            second_file = src_dir / 'second.rst'
            write_doc(second_file, '''\
:orphan:

second
======

more content
''')

            with self.prepare(src_dir, out_dir=out_dir) as app:
                app.connect('env-get-outdated', env_get_outdated)
                app.build()

            self.assertListEqual(added_docs, [
                'index',
                'second',
            ])

            self.assertListEqual(changed_docs, [
            ])

            # re-run with no changes -- no document will be outdated and
            # no source documents will be read

            with self.prepare(src_dir, out_dir=out_dir) as app:
                app.connect('env-get-outdated', env_get_outdated)
                app.build()

            self.assertListEqual(added_docs, [
            ])

            self.assertListEqual(changed_docs, [
            ])

            # re-run with with a change to a single document, and this new
            # file should be listed as outdated
            changed_docs.clear()
            write_doc(second_file, '''\
:orphan:

second
======

changed content
''')

            with self.prepare(src_dir, out_dir=out_dir) as app:
                app.connect('env-get-outdated', env_get_outdated)
                app.build()

            self.assertListEqual(added_docs, [
            ])

            self.assertListEqual(changed_docs, [
                'second',
            ])
