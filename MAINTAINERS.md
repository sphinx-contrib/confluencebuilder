# Maintainers

This document serves as a reminder/guide for maintainers for this extension.
For users wishes to contribute to this extension, please see
[CONTRIBUTING.md][contributing] instead.

## System testing

When a major release is made, it is recommended to perform system testing on
as many supported versions of Confluence Data Center/Server and Confluence
Cloud. This includes (if possible):

- Confluence Cloud with an organization account.
- Confluence Cloud with a user account (tilde-leading).
- Confluence Data Center/Server that are not [end-of-life][eol].

## Internationalization

When new translations are added into the implementation/templates, ensure
these messages are included in the portable object template (`.pot`):

```shell-session
$ ./babel extract
...
writing PO template file to sphinxcontrib/confluencebuilder/locale/sphinxcontrib.confluencebuilder.pot
```

If adding support for a new locale, invoke the following:

```shell-session
$ ./babel init --locale <locale>
running init_catalog
...
```

Ensure each supported locale has the most recent portable object (`.po`)
state:

```shell-session
$ ./babel update
running update_catalog
...
```

Push updated catalogs to Crowdin:

```shell-session
$ crowdin upload sources
[OK] Fetching project info
...
```

Pull most recent translations from Crowdin:

```shell-session
$ crowdin download
[OK] Fetching project info
...
```

Compile machine objects  (`.mo`) using the following:

```shell-session
$ ./babel compile
running compile_catalog
...
```

## Release steps

When implementation is deemed to be ready for a stable release, ensure the
following steps are performed:

- Ensure newly added/changed configuration options are properly reflecting a
  `versionadded` or equivalent hint.
- Ensure message catalogs are up-to-date (see "Internationalization"; above).
- Update `README.md`, replacing any notes of active requirements compared
  to future requirements, to only a requirements list.
- Update `CHANGES.rst`, replacing the development title with release version
  and date.
- Ensure the version value in the implementation has been updated.

A release can be made with the following commands.

----

Perform a local clean build:

```shell
python -m build
```

Verify packages can be published:

```shell
twine check dist/*
```

Validate artifacts with a local pip install:

```shell
pip install dist/*.whl
cd <working-project>
python -m sphinxcontrib.confluencebuilder --version
python -m sphinx -b confluence . _build/confluence -E -a
pip uninstall sphinxcontrib-confluencebuilder
```

Create a local release tag and verify the signed tag:

```shell
git tag -s -a v<version> <hash> -m "sphinxcontrib-confluencebuilder <version>"
git verify-tag <tag>
```

Push the tag to GitHub to start the release workflow:

```shell
git push origin <tag>
```

After the release workflow creates a build, sanity check its logs to ensure
the generated artifact seems sane. If the package appears to be in a good
state, authorize the workflow's environment to complete publishing.

After a release is made, check the pip install with PyPI:

```shell
cd <working-project>
pip install sphinxcontrib-confluencebuilder
python -m sphinxcontrib.confluencebuilder --version
python -m sphinx -b confluence . _build/confluence -E -a
pip uninstall sphinxcontrib-confluencebuilder
```

If no issues, complete the automatically created draft release notes in
GitHub to complete the release.

## Sanity checks and cleanup

After a release has been published to PyPI and a tag is available for users to
reference, ensure the following post-release tasks are performed:

- Verify [Read the Docs space][docs] reflects the most recent documentation.
  `stable` should now point to the most recent release. The contents of
  `latest` should match the `stable` documentation. Also, ensure the newly
  created tag is listed as a valid option for users to reference.
- Generate online validation set (examples) based off the recent release tag.
  This includes both the version space and the `STABLE` space. Overrides for
  consideration:

  ```python
  # version space
  config_overrides['confluence_space_key'] = 'V010X00'
  config_test_key = 'v1.x'
  config_test_desc = 'v1.x release'
  config_version = '<tag>'

  # stable space
  config_overrides['confluence_space_key'] = 'STABLE'
  config_test_key = 'Stable'
  config_test_desc = 'stable release (v1.x)'
  config_version = '<tag>'
  ```


[contributing]: https://github.com/sphinx-contrib/confluencebuilder/blob/main/CONTRIBUTING.md
[docs]: https://sphinxcontrib-confluencebuilder.readthedocs.io/
[eol]: https://confluence.atlassian.com/support/atlassian-support-end-of-life-policy-201851003.html
