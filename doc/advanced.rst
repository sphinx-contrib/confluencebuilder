Advanced
========

Publishing permissions
----------------------

An account used for authentication will have the best experience with the
following permissions_ when attempting to publish to a configured space:

- Space -- View
- Page -- Add, Delete
- Attachments -- Add, Delete

Delete permissions are only required for environments using the
``confluence_cleanup_purge`` (:ref:`ref<confluence_cleanup_purge>`)
capabilitity.

For environments using an OAuth connector, the following scopes are required:

.. code-block:: none

    delete:content:confluence
    read:content-details:confluence
    write:attachment:confluence
    write:content:confluence
    write:watcher:confluence

.. raw:: latex

    \newpage

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

.. references ------------------------------------------------------------------

.. _Permissions: https://support.atlassian.com/confluence-cloud/docs/what-are-confluence-cloud-permissions-and-restrictions/
