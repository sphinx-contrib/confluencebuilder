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


.. references ------------------------------------------------------------------

.. _Permissions: https://confluence.atlassian.com/x/_AozKw
