.. index:: Confluence Macros
.. index:: Macros; Confluence Macros

Confluence Macros
=================

The Confluence Builder extension may attempt to support various stock
Confluence macros through the use of custom :doc:`directives <directives>`
or :doc:`roles <roles>`. However, not all macros will have a markup defined
for them with this extension. Some macros may not have a graceful way to
be used in documentation, a stock macro has yet to have a directive/role
created or the macro is provided by a third-party vendor.

.. note::

    Typically, third-party vendor macros are not added into this
    extension. Exceptions may be made for free addons. However, this
    extension's main goal is to focus on supporting stock macros.

If a stock Confluence macro does not have a directive/role created for it,
users are welcome to submit a pull request to support the macro or create
an issue outlining a desire for one. For developers wishing to support a
third-party macro, it is recommended that developers create a custom
extension providing support for this macro that can integrate with the
Confluence Builder extension.

That all being said, users looking to use macros that do not have a
directive/role define can add any custom macro using the `raw`_ directive.
Consider the following examples. A user can add a `"Cheese" macro`_ using
the following in a reStructuredText document:

.. code-block:: rst

    .. raw:: confluence_storage

        <ac:structured-macro ac:name="cheese" ac:macro-id="5d87ef61-1fcf-4d30-8d3b-82305e13233a" />

Or create an `"Info" macro`_  in a Markdown document:

.. code-block:: md

    ```{raw} confluence_storage
    <ac:structured-macro ac:name="info" ac:macro-id="ecc1aad7-f2f5-4b75-86d1-786370e6d499">
        <ac:rich-text-body>
            <p>Test</p>
        </ac:rich-text-body>
    </ac:structured-macro>
    ```

Try adding either of these example into a document to observe their results.

After trying out adding a raw macro from above, follow the steps in the next
section to help add a custom macro to a document.

Steps
-----

To add a custom macro available on a Confluence instance, perform the
following steps:

1. Creating a new page on the Confluence instance
2. Add the specific macro to be captured on the page and saving
3. Selecting the page's option menu and selecting "View Storage format"
4. Look for the ``ac:structured-macro`` tags in the storage format
5. Copy the tags and place them into a raw-directive in the documentation


.. references ------------------------------------------------------------------

.. _raw: https://docutils.sourceforge.io/docs/ref/rst/directives.html#raw-data-pass-through
.. _"Cheese" macro: https://confluence.atlassian.com/doc/cheese-macro-154632825.html
.. _"Info" macro: https://confluence.atlassian.com/doc/info-tip-note-and-warning-macros-51872369.html
