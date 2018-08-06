tips
====

.. contents::
   :local:

confluence spaces and unique page names
---------------------------------------

An important consideration when using this extension is that Confluence has a
requirement to having unique page names for a given space. When this extension
parses a document's title value, the title is used as either a creation point or
an update point (i.e. if the page name does not exist, it will be created; if
the page name does exist, it will be updated).

One must be cautious when mixing a space with manually prepared content and
published content from this extension. Consider the following use case.

A space MyAwesomeSpace already exists with the following content:

* MyHome
* About
* Tutorials
* See Also

A user may desire to publish a series of Sphinx documentation into a "container"
by, so the page "Documentation" is made:

- MyHome
- About
- **Documentation**
- Tutorials
- See Also

If the Sphinx documentation contains a page named "About", unexpected events
may occur to new users after publishing for the first time. One might expect the
following to be published:

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
(:ref:`jump<confluence_publish_prefix>`) option.

setting a publishing timeout
----------------------------

By default, this extension does not define any timeouts for a publish event. It
is recommended to provide a timeout value based on the environment being used
(see ``confluence_timeout``; :ref:`jump<confluence_timeout>`).

disable xml-rpc
---------------

When published, the default configuration will attempt to first publish using
REST API. If publishing fails, the extension automatically attempts to publish
using the XML-RPC API. This is solely for compatibility reasons (i.e.
environments which for some reason cannot support the REST API). If in an
environment where access to a Confluence instance is limited by the network, one
may not desire two failed attempts when publishing a documentation set. To
disable attempts to publish using the XML-RPC API, see
``confluence_disable_xmlrpc`` (:ref:`jump<confluence_disable_xmlrpc>`).

asking for help
---------------

Having trouble or concerns using this extension? Do not hesitate to bring up an
issue:

   | Atlassian Confluence Builder for Confluence - Issues
   | https://github.com/tonybaloney/sphinxcontrib-confluencebuilder/issues
