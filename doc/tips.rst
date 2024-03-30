Tips
====

.. _confluence_unique_page_names:

Confluence spaces and unique page names
---------------------------------------

An important consideration when using this extension is that Confluence has a
requirement to having unique page names for a given space. When this extension
parses a document's title value, the title is used as either a creation point or
an update point (i.e. if the page name does not exist, it will be created; if
the page name does exist, it will be updated).

A user must be cautious when mixing a space with manually prepared content and
published content from this extension. Consider the following use case.

A space ``MYAWESOMESPACE`` already exists with the following content:

* MyHome
* About
* Tutorials
* See Also

A user may desire to publish a series of Sphinx documentation into a
"container" page, so the page "Documentation" is made:

- MyHome
- About
- **Documentation**
- Tutorials
- See Also

If the Sphinx documentation contains a page named "About", an unexpected event
may occur for new users after publishing for the first time. A user might expect
the following to be published:

- MyHome
- About
- Documentation

  - About (new)
  - Installing (new)
  - User Guide (new)
  - Other (new)

- Tutorials
- See Also

However, since Confluence only supports a single "About" page for a space, the
original "About" page is updated with new content from the documentation set and
is moved as a child of the container page:

- MyHome
- Documentation

  - About (**updated and moved**)
  - Installing (new)
  - User Guide (new)
  - Other (new)

- Tutorials
- See Also

Users needing to restrict the extension from possibly mangling manually prepared
content can use the ``confluence_publish_prefix``
(:ref:`ref<confluence_publish_prefix>`) or ``confluence_publish_postfix``
(:ref:`ref<confluence_publish_postfix>`) options.

See also the :ref:`dry run capability <confluence_publish_dryrun>` and the
:ref:`title overrides capability <confluence_title_overrides>`.

Setting a publishing timeout
----------------------------

By default, this extension does not define any timeouts for a publish event. It
is recommended to provide a timeout value based on the environment being used
(see ``confluence_timeout``; :ref:`ref<confluence_timeout>`).

Connection troubleshooting
--------------------------

The majority of connection issues reported are typically configuration
issues. For example, attempting to configure a Confluence Cloud API token
using a configuration designed for a Confluence Server Personal Access
Token (PAT).

Users may try to invoke a connection test to help debug connection issues.
To invoke a connection test, run the following command inside the Sphinx
project:

.. code-block:: shell-session

    $ python -m sphinxcontrib.confluencebuilder connection-test
    Fetching configuration information...
    Running Sphinx v7.2.6
    ...
    Connecting to Confluence instance... connected!
    Fetching Confluence instance information... fetched!
    Decoding information... decoded!
    Parsing information... parsed!
        Type: confluence
     Version: 1000.0.0-395b9ccce521
       Build: 6452

.. index:: Wiping a space
.. index:: Page removal; Wiping a space

Wiping a space
--------------

.. danger::

    Pages removed from this call cannot be recovered without the help of an
    administrator for the Confluence space which pages will be removed from.

A command line argument ``wipe`` is available for users wishing to remove pages
from a configured space. This can be useful for users who need to clear multiple
pages which have been pushed through automation or if the Confluence instance
does not support automatically deleting page children.

A wipe request can be started using the following:

.. code-block:: shell-session

    $ python -m sphinxcontrib.confluencebuilder wipe --danger
    ...

    Are you sure you want to continue? [y/N] y

             URL: https://intranet-wiki.example.com/
           Space: TEST
           Pages: All Pages
     Total pages: 250

    Are you sure you want to REMOVE these pages? [y/N] y

    Removing pages.... done

If a user wishes to only remove child pages of a
:ref:`configured parent page <confluence_parent_page>`, the option ``--parent``
can be used:

.. code-block:: shell

    python -m sphinxcontrib.confluencebuilder wipe --danger --parent

Asking for help
---------------

Having trouble or concerns using this extension? Do not hesitate to bring up an
issue:

    | Atlassian Confluence Builder for Confluence - Issues
    | https://github.com/sphinx-contrib/confluencebuilder/issues

For issues when using this extension, generating a report and including this
content in an issue may be helpful towards finding a solution. To generate a
report, run the following command from the documentation directory:

.. code-block:: shell-session

    $ python -m sphinxcontrib.confluencebuilder report
    ...
    Confluence builder report has been generated.
    Please copy the following text for the GitHub issue:

    ------------[ cut here ]------------
    (system)
    ...

    (configuration)
    ...

    (confluence instance)
     ...
    ------------[ cut here ]------------
