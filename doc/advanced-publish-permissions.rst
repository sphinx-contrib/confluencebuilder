.. _publish_permissions:

Publishing permissions
======================

An account used for authentication will have the best experience with the
following permissions_ when attempting to publish to a configured space:

- Space -- View
- Page -- Add, Delete
- Attachments -- Add, Delete

Delete permissions are only required for environments using the
:lref:`confluence_cleanup_purge` capabilitity.

For environments using an OAuth connector or scoped API tokens, the following
scopes are required:

.. code-block:: none

    read:space:confluence
    read:content.metadata:confluence
    read:page:confluence
    write:page:confluence
    delete:page:confluence
    read:attachment:confluence
    read:content-details:confluence
    write:attachment:confluence
    delete:attachment:confluence
    write:watcher:confluence

.. references ------------------------------------------------------------------

.. _Permissions: https://support.atlassian.com/confluence-cloud/docs/what-are-confluence-cloud-permissions-and-restrictions/
