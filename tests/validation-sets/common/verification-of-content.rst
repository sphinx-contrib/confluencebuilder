verification of content
=======================

The following page tests a series of content containing characters which may
cause issues between documentation data and Confluence data publishing.

.. consider this failed if any point has additional formatting

Raw XML outside of a code block should be unaffected:

<xml><strong><node a="1" b='1' /></strong></xml>

.. consider this failed if any content is not an exact match of the source

Characters in a code block should be unaffected:

.. code-block:: xml

   <languages>
       <language name="c" />
       <language name="cpp" />
       <language name="c#" />
       <language name="xml">
           <option key="key" value="value" />
       </language>
   </languages>

.. consider this failed if any inlined content has additional formatting

Characters in inline literals should be unaffected:

    This is an ``<strong>inline</strong>`` ``<em>blocks</em>`` with
    ``<sup>tags</sup>``.

.. consider this failed if Confluence renders "Letâ€™s see if..."

Let's see if this encoding on this page is improperly handled.
