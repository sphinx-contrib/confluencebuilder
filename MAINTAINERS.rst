Maintainers
===========

This document serves as a reminder/guide for maintainers for this extension. For
users wishes to contribute to this extension, please consult `CONTRIBUTING.rst`_
instead.

System testing
--------------

When a major release is made, it is recommended to perform system testing on all
supported versions of Confluence Server and Confluence Cloud. Test both
Confluence Cloud with an organization account and a user account (tilde-leading)
as well as all Confluence supported server revisions (consult
`Atlassian Support End of Life Policy`_ for the most recent list).

Internationalization
--------------------

When new translations are added into the implementation/templates, ensure these
messages are included in the portable object template (``.pot``):

.. code-block:: shell-session

    $ ./babel extract
    ...
    writing PO template file to sphinxcontrib/confluencebuilder/locale/sphinxcontrib.confluencebuilder.pot

If adding support for a new locale, invoke the following:

.. code-block:: shell-session

    $ ./babel init --locale <locale>
    running init_catalog
    ...

Ensure each supported locale has the most recent portable object (``.po``)
state:

.. code-block:: shell-session

    $ ./babel update
    running update_catalog
    ...

Push updated catalogs to Crowdin:

.. code-block:: shell-session

    $ crowdin upload sources
    [OK] Fetching project info
    ...

Pull most recent translations from Crowdin:

.. code-block:: shell-session

    $ crowdin download
    [OK] Fetching project info
    ...

Compile machine objects  (``.mo``) using the following:

.. code-block:: shell-session

    $ ./babel compile
    running compile_catalog
    ...

Release steps
-------------

When implementation is deemed to be ready for a stable release, ensure the
following steps are performed:

- Ensure newly added/changed configuration options are properly reflecting a
  ``versionadded`` or equivalent hint.
- Ensure message catalogs are up-to-date (see "Internationalization"; above).
- Update ``README.rst``, replacing any notes of active requirements compared
  to future requirements, to just a requirements list.
- Update ``CHANGES.rst``, replacing the development title with release version
  and date.
- Ensure version values in the implementation are incremented and tagged
  appropriately. The tagged commit should have a "clean" version string.
- Ensure the release tag is signed.

A release can be made with the following commands.

----

Perform a clean build:

.. code-block:: shell

    python -m build

Verify packages can be published:

.. code-block:: shell

    twine check dist/*

Validate artifacts with a local pip install:

.. code-block:: shell

    pip install dist/*.whl
    cd <working-project>
    python -m sphinxcontrib.confluencebuilder --version
    python -m sphinx -b confluence . _build/confluence -E -a
    pip uninstall sphinxcontrib-confluencebuilder

Sign the packages:

.. code-block:: shell

    gpg --detach-sign -a dist/sphinxcontrib*.gz
    gpg --detach-sign -a dist/sphinxcontrib*.whl

Sanity check the signed packages:

.. code-block:: shell-session

    gpg --verify dist/sphinxcontrib*.gz.asc
    gpg --verify dist/sphinxcontrib*.whl.asc

Publish the packages:

.. code-block:: shell

    twine upload dist/*

Check pip install with PyPI package:

.. code-block:: shell

    cd <working-project>
    pip install sphinxcontrib-confluencebuilder
    python -m sphinxcontrib.confluencebuilder --version
    python -m sphinx -b confluence . _build/confluence -E -a
    pip uninstall sphinxcontrib-confluencebuilder

Tag/push the release tag:

.. code-block:: shell

    git tag -s -a v<version> <hash> -m "sphinxcontrib-confluencebuilder <version>"
    git verify-tag <tag>
    git push origin <tag>

Generate hashes from the release:

.. code-block:: shell

    cd dist
    sha256sum -b * >sphinxcontrib-confluencebuilder-<version>.sha256sum

Create a new release entry on GitHub.

Sanity checks and cleanup
-------------------------

After a release has been published to PyPI and a tag is available for users to
reference, ensure the following post-release tasks are performed:

- Verify Read the Docs space reflects the most recent documentation. ``stable``
  should now point to the most recent release. The contents of ``latest`` should
  match the ``stable`` documentation. Also, ensure the newly created tag is
  listed as a valid option for users to reference.
- Generate online validation set (examples) based off the recent release tag.
  This includes both the version space and the ``STABLE`` space. Overrides for
  consideration:

  .. code-block:: python

      # version space
      config_overrides['confluence_space_name'] = 'V010X00'
      config_test_key = 'v1.x'
      config_test_desc = 'v1.x release'
      config_version = '<tag>'

      # stable space
      config_overrides['confluence_space_name'] = 'STABLE'
      config_test_key = 'Stable'
      config_test_desc = 'stable release (v1.x)'
      config_version = '<tag>'

.. _Atlassian Support End of Life Policy: https://confluence.atlassian.com/support/atlassian-support-end-of-life-policy-201851003.html
.. _CONTRIBUTING.rst: https://github.com/sphinx-contrib/confluencebuilder/blob/main/CONTRIBUTING.rst
