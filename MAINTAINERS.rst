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

    $ python setup.py extract_messages
    running extract_messages
    ...
    writing PO template file to sphinxcontrib/confluencebuilder/locale/sphinxcontrib.confluencebuilder.pot

If adding support for a new locale, invoke the following:

.. code-block:: shell-session

    $ python setup.py init_catalog --locale <locale>
    running init_catalog
    ...

Ensure each supported locale has the most recent portable object (``.po``)
state:

.. code-block:: shell-session

    $ python setup.py update_catalog
    running update_catalog
    ...

Compile machine objects  (``.mo``) using the following:

.. code-block:: shell-session

    $ python setup.py compile_catalog
    running compile_catalog
    ...

Release steps
-------------

When implementation is deemed to be ready for a stable release, ensure the
following steps are performed:

- Ensure newly added/changed configuration options are properly reflecting a
  ``versionadded`` or equivalent hint.
- Ensure message catalogs are up-to-date (see "Internationalization"; above).
- Update ``CHANGES.rst``, replacing the development title with release version
  and date.
- Ensure version values in the implementation are incremented and tagged
  appropriately. The tagged commit should have a "clean" version string.
- Ensure the release tag is signed.
- After invoking ``bdist_wheel``, ensure a universal wheel has been created
  (i.e. inspect that the generated package inside ``dist/``  properly reflects
  ``py2.py3`` support).

A release can be made with the following commands:

.. code-block:: shell-session

    $ python -m build
    running sdist
    running egg_info
    ...

    (note: verify packages can be published)

    $ twine check dist/*

    (note: validate artifacts with a local pip install)

    $ gpg --detach-sign -a dist/sphinxcontrib*.gz
    $ gpg --detach-sign -a dist/sphinxcontrib*.whl

    (note: verify with `gpg --verify <artifact>`)

    $ twine upload dist/*

    (note: check pip install with PyPI package)

    $ git tag -s -a v<version> <hash> -m "sphinxcontrib-confluencebuilder <version>"
    $ git verify-tag <tag>
    $ git push origin <tag>

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
