# Sample sets

The following contains a series of sample sets to help sanity check the use of
the Confluence Builder extension using various data sets or other third-party
extensions. These sample sets are used for manual testing. There is no
guarantee that the samples provided here will work as expected, let alone work
at all. There may be uses of third-party extensions which may be attempted to
be supported; however, it should be noted that even if there is an example
sample for a given third-party extension in this testing area, the Confluence
Builder extension still provides no guaranteed supported for third-party
extensions that exist outside of the Sphinx's repository (for extensions that
are compatible with a Confluence environment).

For example, a developer wishing to test math-related changes, the following
command can be used to build a math-specific Sphinx project in its own tox
environment:

```
tox -c tests/sample-sets/math
```

Developers are compare Confluence-generated documents with other builders. For
example, to run a project with the `html` builder, the following may be
invoked:

```
tox -c tests/sample-sets/math -- -b html
```
