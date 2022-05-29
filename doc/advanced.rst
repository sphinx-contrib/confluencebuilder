Advanced
========

Publishing permissions
----------------------

An account used for authentication requires the following permissions_ when
attempting to publish to a configured space:

- Space -- View
- Page -- Add, Delete
- Attachments -- Add, Delete

For environments using an OAuth connector, the following scopes are required:

.. code-block:: none

    delete:content:confluence
    read:content-details:confluence
    write:attachment:confluence
    write:content:confluence
    write:watcher:confluence


.. references ------------------------------------------------------------------

.. _Permissions: https://confluence.atlassian.com/x/_AozKw
