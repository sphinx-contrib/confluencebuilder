Events
======

The following outlines additional `events`_ supported by this extension.

Generic events
--------------

.. event:: confluence-publish-attachment (app, docname, key, aid, meta)

   :param app: :class:`.Sphinx`
   :param docname: ``str`` of the document name
   :param key: ``str`` of the attachment key
   :param aid: ``int`` of the upload id of the published attachment
   :param meta: ``dict`` of additional metadata for this event

   Emitted when this extension has completed the upload of an attachment.

   .. versionadded:: 2.8

.. event:: confluence-publish-page (app, docname, pid, meta)

   :param app: :class:`.Sphinx`
   :param docname: ``str`` of the document name
   :param pid: ``int`` of the upload id of the published page
   :param meta: ``dict`` of additional metadata for this event

   Emitted when this extension has completed the upload of a document.

   .. versionadded:: 2.8

.. event:: confluence-publish-point (app, point_url)

   :param app: :class:`.Sphinx`
   :param point_url: ``str`` of the publish point URL

   Emitted when this extension prints the "publish point" URL to the
   standard output stream.

   .. versionadded:: 2.6

Advanced events
---------------

.. event:: confluence-publish-override-pageid (app, docname, meta)

   :param app: :class:`.Sphinx`
   :param docname: ``str`` of the document name
   :param meta: ``dict`` of additional metadata for this event
   :returns: ``int | None`` of the new page identifier

   Emitted when this extension is about to determine the page identifier
   to publish a document. A configuration and register this event and
   return a new identifier to use for a page. If ``None`` is returned,
   the extension will operate in the same manner as if no override was
   provided.

   .. versionadded:: 2.8

.. references ------------------------------------------------------------------

.. _events: https://www.sphinx-doc.org/en/master/extdev/event_callbacks.html
